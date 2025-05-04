import cv2
from numpy import ndarray

from src.services.mediapipe.medipipe_join_tracking import mediapipe_all
from src.services.mediapipe.schemas import ProctoringResultSchema, ProctoringTypeSchema


def handle_proctoring(*, img: ndarray, proctoring_type: ProctoringTypeSchema) -> ProctoringResultSchema:

    img = cv2.imdecode(img, cv2.IMREAD_COLOR)  # Декодируем изображение
    h, w = img.shape[:2]

    result = mediapipe_all(img, w, h, proctoring_type=proctoring_type)

    return result
