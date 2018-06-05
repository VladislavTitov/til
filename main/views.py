from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import MyUserCreationForm, MyAuthForm
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
import json
from wsgiref.util import FileWrapper


# Create your views here.


def reg(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('main'))
    else:
        form = MyUserCreationForm()

    return render(request, 'registration.html', {'form': form})


# def auth(request):
#     if request.method == 'POST':
#         form = MyAuthForm(request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return HttpResponseRedirect(reverse('main'))
#     else:
#         form = MyAuthForm()
#
#     return render(request, 'login.html', {'form': form})

@login_required(login_url='/main/login')
def main(request):
    user = request.user
    apikeys = ApiKey.objects.filter(user=user)
    return render(request, 'main.html', context={'apikeys': apikeys})


def test(request, pk):
    tests = Test.objects.filter(api_key__pk=pk)
    return render(request, 'test.html', context={'tests': tests})


def testab(request, pk):
    tests = TestAB.objects.filter(test__pk=pk)
    return render(request, 'testab.html', context={'tests': tests})


def videos_view(request, pk):
    videos = Video.objects.filter(test__pk=pk)
    emotions_str = get_video_emotions(videos)

    return render(request, 'videos.html', context={'videos': videos, 'emotions': emotions_str})


def get_video_emotions(videos):
    common_labels = []
    for video in videos:
        labels, probs = parse_track(video.track)
        common_labels += labels
    all_caps = len(common_labels)
    label_count = {}
    for label in common_labels:
        if label not in label_count:
            label_count[label] = 1
        else:
            label_count[label] = label_count[label] + 1
    emotions_str = ['{} - {}'.format(k, round(label_count[k] * 100 / all_caps, 2)) for k in
                    sorted(label_count, key=label_count.get, reverse=True)]
    return emotions_str


def video_details(request, pk):
    found_video = get_object_or_404(Video, pk=pk)
    labels, probability = parse_track(found_video.track)

    if len(labels) < 1:
        return render(request, 'video.html', context={'video': found_video, 'is_empty': True})

    start = 0
    interval = found_video.finish_time.timestamp() - found_video.start_time.timestamp()
    delta = interval / len(labels)
    times = [round(start + i * delta, 3) for i in range(len(labels))]

    return render(request, 'video.html', context={'video': found_video, 'labels': labels, 'times': times})


def parse_track(trackstr):
    track = json.loads(trackstr)
    labels = []
    probability = []
    for item in track:
        for key, value in item.items():
            labels.append(key)
            probability.append(float(value))
    return labels, probability


def video_file(request, pk):
    found_video = get_object_or_404(Video, pk=pk)
    file = FileWrapper(open(found_video.video.path, 'rb'))
    response = HttpResponse(file, content_type='video/mp4')
    response['Content-Disposition'] = 'attachment; filename={}'.format(found_video.name)
    return response


class ApiKeyCreateView(LoginRequiredMixin, CreateView):
    model = ApiKey
    fields = ('name',)
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ApiKeyCreateView, self).form_valid(form)


@csrf_exempt
def upload(request):
    if request.method == 'POST':
        api_key = request.GET['api_key']
        test_name = request.GET['test']
        os = request.GET['os'][0]
        test_ab = request.GET['test_ab'][0]

        name = request.GET['name']
        start_time = int(request.GET['start'])
        finish_time = int(request.GET['finish'])

        start_time = datetime.datetime.fromtimestamp(start_time).isoformat()
        finish_time = datetime.datetime.fromtimestamp(finish_time).isoformat()

        number = int(request.GET['number'])

        video = request.FILES['file']

        api_key_obj, is_exists = check_api_key(api_key)

        if not is_exists:
            res = HttpResponse("Api key {} does'nt exist!".format(api_key), status=400)
            return res

        test, test_created = check_and_save_test(test_name, os, api_key_obj)
        test_ab, test_ab_created = check_and_save_testab(test_ab, test)
        check_and_save_video(video, name, start_time, finish_time, number, test_ab)

        return HttpResponse(
            "Uploaded\n api key = {}, test = {}, a or b = {}, os = {}, video name = {}, started in {} and finished in {}".format(
                api_key, test_name, test_ab, os, name, start_time, finish_time))
    else:
        raise Http404("Get (or another) method on this url does'nt exist!")


def check_api_key(item):
    try:
        return ApiKey.objects.get(key=item), True
    except ApiKey.DoesNotExist:
        return None, False


def check_and_save_test(test_name, os, api_key):
    return Test.objects.get_or_create(api_key=api_key, os=os, name=test_name)


def check_and_save_testab(category, test):
    return TestAB.objects.get_or_create(category=category, test=test)


def check_and_save_video(video_file, name, start_time, finish_time, number, test_ab):
    return Video.objects.get_or_create(video=video_file, name=name, start_time=start_time, finish_time=finish_time,
                                       number=number, test=test_ab)
