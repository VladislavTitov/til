import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import signals


# Create your models here.
from django.urls import reverse


class ApiKey(models.Model):
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(verbose_name='Application name')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    creation_date = models.DateTimeField(verbose_name="Api key creation date", auto_now_add=True)

    class Meta:
        ordering = ['creation_date']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api-key-details', args=[str(self.pk)])


class Test(models.Model):
    ANDROID = 'a'
    IOS = 'i'
    OS = (
        (ANDROID, 'Android'),
        (IOS, 'iOS')
    )

    name = models.TextField()
    os = models.CharField(max_length=1, choices=OS)
    api_key = models.ForeignKey(ApiKey, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('test-details', args=[str(self.id)])


class TestAB(models.Model):
    category = models.CharField(max_length=1, null=False)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    def __str__(self):
        return self.category

    def get_absolute_url(self):
        return reverse('testab-details', args=[str(self.id)])


class Video(models.Model):
    video = models.FileField(upload_to='videos')
    name = models.TextField()
    number = models.IntegerField(default=0)

    track = models.TextField(default="")
    is_processed = models.BooleanField(default=False)

    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    test = models.ForeignKey(TestAB, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('video-details', args=[str(self.id)])


from .tasks import process_video


def video_post_save(sender, instance, signal, *args, **kwargs):
    if not instance.is_processed:
        process_video.delay(instance.pk)


signals.post_save.connect(video_post_save, sender=Video)