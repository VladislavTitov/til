import cv2
import numpy as np
from keras.models import load_model
from statistics import mode
from .utils.datasets import get_labels
from .utils.inference import detect_faces
from .utils.inference import draw_text
from .utils.inference import draw_bounding_box
from .utils.inference import apply_offsets
from .utils.inference import load_detection_model
from .utils.preprocessor import preprocess_input


def recognize(path: str):
    track = []

    emotion_model_path = 'emotion/models/emotion_model.hdf5'
    emotion_labels = get_labels('fer2013')

    emotion_offsets = (20, 40)

    face_cascade = cv2.CascadeClassifier('emotion/models/haarcascade_frontalface_default.xml')
    emotion_classifier = load_model(emotion_model_path)

    emotion_target_size = emotion_classifier.input_shape[1:3]

    cap = cv2.VideoCapture(path)  # Video file source

    while cap.isOpened():
        ret, bgr_image = cap.read()
        if ret:
            gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        else:
            break

        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5,
                                              minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

        for face_coordinates in faces:
            x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]
            try:
                gray_face = cv2.resize(gray_face, (emotion_target_size))
            except:
                continue

            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            emotion_prediction = emotion_classifier.predict(gray_face)
            emotion_probability = np.max(emotion_prediction)
            emotion_label_arg = np.argmax(emotion_prediction)
            emotion_text = emotion_labels[emotion_label_arg]

            track.append({emotion_text: str(emotion_probability)})

    cap.release()
    cv2.destroyAllWindows()
    return track
