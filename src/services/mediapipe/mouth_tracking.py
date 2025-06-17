import cv2
import mediapipe as mp
import numpy as np
from utils import lips_scale, colorBackgroundText, FONT
import time

LIPS=[ 61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 185, 40, 39, 37, 0, 267, 269, 270, 409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78 ]

def landmarks_detection(img, results, draw=False):
    img_height, img_width = img.shape[:2]
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    landmarks = results.multi_face_landmarks[0].landmark
    if draw:
        [cv2.circle(img, p, 2, (0,255,0), -1) for p in mesh_coord]

    return mesh_coord, landmarks

# Функция расчета векторного расстояния
def calculate_distance(point1, point2):
    return ((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2) ** 0.5

def mouth_open(img, w, h):
    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        
        img.flags.writeable = False
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(img)

        img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if results.multi_face_landmarks:

            mesh_coords, landmarks = landmarks_detection(img, results, False)


            head_distance = calculate_distance((landmarks[10].x, landmarks[10].y),
                                               (landmarks[152].x, landmarks[152].y)) * 100

            lips_distance = calculate_distance((landmarks[13].x, landmarks[13].y),
                                               (landmarks[14].x, landmarks[14].y)) * 100

            #cv2.polylines(img, [np.array([mesh_coords[p] for p in LIPS], dtype=np.int32)], True, (0,255,0), 1, cv2.LINE_AA)
            [cv2.circle(img, mesh_coords[p], 1, (0, 255, 0), -1, cv2.LINE_AA) for p in LIPS] #тоже убрать

            head_lips = lips_distance / head_distance * 100

            scale = lips_scale(w, h)

            if head_lips >= 2: 
                colorBackgroundText(img, f"LIPS: {head_lips:.3f}", FONT, scale[0], (scale[1],scale[2]), scale[3], (0,0,0), (0,0,255), scale[4], scale[4]) #убрать
                print(f'Открытие рта {time.ctime(time.time())}')
            else:
                colorBackgroundText(img, f"LIPS: {head_lips:.3f}", FONT, scale[0], (scale[1],scale[2]), scale[3], (0,0,0), (0,100,255), scale[4], scale[4]) #убрать

    return img