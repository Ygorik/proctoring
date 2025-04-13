import cv2
import numpy as np
import mediapipe as mp
from utils import colorBackgroundText, eyes_scale, FONT
import time

# Ключевые точки глаз
LEFT_EYE = [ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
RIGHT_EYE = [ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]  

# Функция распознавания ключевых точек
def landmarks_detection(img, results, draw=False):
    img_height, img_width = img.shape[:2]
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw:
        [cv2.circle(img, p, 2, (0,255,0), -1) for p in mesh_coord]

    return mesh_coord

# Функция для извлечения глаз на изображении
def eyes_cutout(img, right_eye_coords, left_eye_coords):
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    wh = gray.shape

    # Создание маски
    mask = np.zeros(wh, dtype=np.uint8)

    # Нарисовать маску поверх глаз
    cv2.fillPoly(mask, [np.array(right_eye_coords, dtype=np.int32)], 255)
    cv2.fillPoly(mask, [np.array(left_eye_coords, dtype=np.int32)], 255)

    # Показать маску
    cv2.imshow('mask', mask)
    
    # Нарисовать глаза поверх выделеной маски
    eyes = cv2.bitwise_and(gray, gray, mask=mask)

    # Заменить черный цвет на серый, кроме глаз
    eyes[mask==0] = 155
    
    # Получение макс и мин значений x и y для правого и левого глаза
    # Для правого 
    r_max_x = (max(right_eye_coords, key=lambda item: item[0]))[0]
    r_min_x = (min(right_eye_coords, key=lambda item: item[0]))[0]
    r_max_y = (max(right_eye_coords, key=lambda item : item[1]))[1]
    r_min_y = (min(right_eye_coords, key=lambda item: item[1]))[1]

    # Для левого
    l_max_x = (max(left_eye_coords, key=lambda item: item[0]))[0]
    l_min_x = (min(left_eye_coords, key=lambda item: item[0]))[0]
    l_max_y = (max(left_eye_coords, key=lambda item : item[1]))[1]
    l_min_y = (min(left_eye_coords, key=lambda item: item[1]))[1]

    # Обрезка глаз из маски
    cropped_right = eyes[r_min_y: r_max_y, r_min_x: r_max_x]
    cropped_left = eyes[l_min_y: l_max_y, l_min_x: l_max_x]

    return cropped_right, cropped_left

# Функция подсчета пикселей
def pixel_counter(first_piece, second_piece, third_piece):

    # Подсчет темных пикселей в разных частях
    right_part = np.sum(first_piece==0)
    center_part = np.sum(second_piece==0)
    left_part = np.sum(third_piece==0)

    eye_parts = [right_part, center_part, left_part]

    # Получение макс индекса
    max_index = eye_parts.index(max(eye_parts))
    pos_eye ='' 

    if max_index==0:
        pos_eye = "RIGHT"
        color = [(128,128,128), (0,255,255)]
    elif max_index==1:
        pos_eye = 'CENTER'
        color = [(0,0,0), (0,255,0)]
    elif max_index ==2:
        pos_eye = 'LEFT'
        color = [(128,128,128), (0,255,255)]
    else:
        pos_eye="Closed"
        color = [(0,255,255), (147,20,255)]

    return pos_eye, color

# Функция определения положения глаз
def position_score(cropped_eye):

    h, w = cropped_eye.shape
    
    # Удаление шумов с изображения
    gaussain_blur = cv2.GaussianBlur(cropped_eye, (5,5), 1)
    median_blur = cv2.medianBlur(gaussain_blur, 3)

    # Преобразование изображения в бинарное
    ret, threshed_eye = cv2.threshold(median_blur, 70, 255, cv2.THRESH_BINARY)

    # Выделение равной части глаза
    piece = int(w / 5) 

    # Разделение глаза на три равные части
    right_piece = threshed_eye[0:h, 0:piece+piece]
    center_piece = threshed_eye[0:h, piece+piece:piece+piece+piece]
    left_piece = threshed_eye[0:h, piece+piece+piece:w]
    
    # Подсчет пикселей
    eye_position, color = pixel_counter(right_piece, center_piece, left_piece)

    return eye_position, color 


def eyes_move(img, w, h, draw_all):

    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:

        img.flags.writeable = False
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results  = face_mesh.process(img)

        img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if results.multi_face_landmarks:
            mesh_coords = landmarks_detection(img, results, draw_all)

            cv2.polylines(img, [np.array([mesh_coords[p] for p in LEFT_EYE], dtype=np.int32)], True, (0,255,0), 1, cv2.LINE_AA)
            cv2.polylines(img, [np.array([mesh_coords[p] for p in RIGHT_EYE], dtype=np.int32)], True, (0,255,0), 1, cv2.LINE_AA)

            right_coords = [mesh_coords[p] for p in RIGHT_EYE]
            left_coords = [mesh_coords[p] for p in LEFT_EYE]
            crop_right, crop_left = eyes_cutout(img, right_coords, left_coords)

            scale = eyes_scale(w, h)

            eye_position_right, color = position_score(crop_right)
            colorBackgroundText(img, f'R: {eye_position_right}', FONT, scale[0], (scale[1],scale[2]), scale[4], color[0], color[1], scale[5], scale[5])
            eye_position_left, color = position_score(crop_left)
            colorBackgroundText(img, f'L: {eye_position_left}', FONT, scale[0], (scale[1],scale[3]), scale[4], color[0], color[1], scale[5], scale[5])

            if eye_position_right == 'LEFT' and eye_position_left == 'LEFT':
                print(f'Глаза направлены влево {time.ctime(time.time())}')
            elif eye_position_right == 'RIGHT' and eye_position_left == 'RIGHT':
                print(f'Глаза направлены вправо {time.ctime(time.time())}')

    return img