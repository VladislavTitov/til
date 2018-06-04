import logging

from emotion import emotions
import json
from .models import Video
from testinterfacelibrary.celery import app


@app.task
def process_video(video_id):
    try:
        video = Video.objects.get(pk=video_id)
        track = emotions.recognize(video.video.path)
        video.is_processed = True
        video.track = json.dumps(track)
        video.save()

    except Video.DoesNotExist:
        logging.warning("Video with id = {} does'nt exist!".format(video_id))
