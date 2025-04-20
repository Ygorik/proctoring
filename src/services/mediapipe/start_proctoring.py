import cv2
from src.services.mediapipe.medipipe_join_tracking import mediapipe_all


def proctoring(img):

    img = cv2.imdecode(img, cv2.IMREAD_COLOR)  # Декодируем изображение
    h, w = img.shape[:2]

    img, result_dict = mediapipe_all(img, w, h, False)
    return result_dict
