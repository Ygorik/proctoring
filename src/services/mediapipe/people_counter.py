import cv2
import mediapipe as mp
from utils import colorBackgroundText, FONT, counter_scale
import time

def people_count(img, w, h):
    mp_face_detection = mp.solutions.face_detection

    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:

        img.flags.writeable = False
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = face_detection.process(img)

        img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        p_count = len(results.detections)

        scale = counter_scale(w, h)

        if p_count == 1:
            colorBackgroundText(img, f"ONLY ONE", FONT, scale[0], (scale[1],scale[2]), scale[3], (0,100,255), (0,0,0), scale[4], scale[4])
        elif p_count > 1:
            colorBackgroundText(img, f"MORE THEN ONE", FONT, scale[0], (scale[1],scale[2]), scale[3], (0,0,255), (0,0,0), scale[4], scale[4])
            print(f'Более одного человека в кадре {time.ctime(time.time())}')
        elif p_count < 1:
            colorBackgroundText(img, f"NO ONE", FONT, scale[0], (scale[1],scale[2]), scale[3], (0,0,255), (0,0,0), scale[4], scale[4])
            print(f'Нет человека в кадре {time.ctime(time.time())}')

    return img