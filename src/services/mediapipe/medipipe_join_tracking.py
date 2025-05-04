import cv2
import numpy as np
import mediapipe as mp
import time

from src.services.mediapipe.schemas import ProctoringResultSchema, ProctoringTypeSchema

# Ключевые точки
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 185, 40, 39,
        37, 0, 267, 269, 270, 409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78]


# Функция определяющая ключевые точки на лице
def landmarks_detection(img, results):
    img_height, img_width = img.shape[:2]
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in
                  results.multi_face_landmarks[0].landmark]
    landmarks = results.multi_face_landmarks

    return mesh_coord, landmarks


# Функция для подсчета векторного расстояния
def calculate_distance(point1, point2):
    return ((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2) ** 0.5


# Функция для извлечения глаз на изображении
def eyes_cutout(img, right_eye_coords, left_eye_coords):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    wh = gray.shape

    # Создание маски
    mask = np.zeros(wh, dtype=np.uint8)

    # Нарисовать маску поверх глаз
    cv2.fillPoly(mask, [np.array(right_eye_coords, dtype=np.int32)], 255)
    cv2.fillPoly(mask, [np.array(left_eye_coords, dtype=np.int32)], 255)

    # Нарисовать глаза поверх выделенной маски
    eyes = cv2.bitwise_and(gray, gray, mask=mask)

    # Заменить черный цвет на серый, кроме глаз
    eyes[mask == 0] = 155

    # Получение макс и мин значений x и y для правого и левого глаза
    # Для правого 
    r_max_x = (max(right_eye_coords, key=lambda item: item[0]))[0]
    r_min_x = (min(right_eye_coords, key=lambda item: item[0]))[0]
    r_max_y = (max(right_eye_coords, key=lambda item: item[1]))[1]
    r_min_y = (min(right_eye_coords, key=lambda item: item[1]))[1]

    # Для левого
    l_max_x = (max(left_eye_coords, key=lambda item: item[0]))[0]
    l_min_x = (min(left_eye_coords, key=lambda item: item[0]))[0]
    l_max_y = (max(left_eye_coords, key=lambda item: item[1]))[1]
    l_min_y = (min(left_eye_coords, key=lambda item: item[1]))[1]

    # Обрезка глаз из маски
    cropped_right = eyes[r_min_y: r_max_y, r_min_x: r_max_x]
    cropped_left = eyes[l_min_y: l_max_y, l_min_x: l_max_x]

    return cropped_right, cropped_left


# Функция подсчета пикселей глаза
def eye_pixels(first_piece, second_piece, third_piece):
    # Подсчет темных пикселей в разных частях
    right_part = np.sum(first_piece == 0)
    center_part = np.sum(second_piece == 0)
    left_part = np.sum(third_piece == 0)

    eye_parts = [right_part, center_part, left_part]

    # Получение макс индекса
    max_index = eye_parts.index(max(eye_parts))
    pos_eye = ''

    if max_index == 0:
        pos_eye = "RIGHT"
        color = [(128, 128, 128), (0, 255, 255)]
    elif max_index == 1:
        pos_eye = 'CENTER'
        color = [(0, 0, 0), (0, 255, 0)]
    elif max_index == 2:
        pos_eye = 'LEFT'
        color = [(128, 128, 128), (0, 255, 255)]
    else:
        pos_eye = "Closed"
        color = [(0, 255, 255), (147, 20, 255)]

    return pos_eye, color


# Функция определения положения глаз
def eye_position(cropped_eye):
    h, w = cropped_eye.shape

    # Удаление шумов с изображения
    gaussain_blur = cv2.GaussianBlur(cropped_eye, (5, 5), 1)
    median_blur = cv2.medianBlur(gaussain_blur, 3)

    # Преобразование изображения в бинарное
    ret, threshed_eye = cv2.threshold(median_blur, 70, 255, cv2.THRESH_BINARY)

    # Выделение равной части глаза
    piece = int(w / 5)

    # Разделение глаза на три равные части
    right_piece = threshed_eye[0:h, 0:piece + piece]
    center_piece = threshed_eye[0:h, piece + piece:piece + piece + piece]
    left_piece = threshed_eye[0:h, piece + piece + piece:w]

    # Подсчет пикселей
    eye_position, color = eye_pixels(right_piece, center_piece, left_piece)

    return eye_position, color


# Функция для движения рта
def lips_ratio(landmarks):
    head_distance = calculate_distance((landmarks[10].x, landmarks[10].y),
                                       (landmarks[152].x, landmarks[152].y)) * 100

    lips_distance = calculate_distance((landmarks[13].x, landmarks[13].y),
                                       (landmarks[14].x, landmarks[14].y)) * 100

    head_lips = lips_distance / head_distance * 100

    if head_lips >= 2:
        mouth_open = True
    else:
        mouth_open = False

    return head_lips, mouth_open


# Функция для расчета степени поворота головы
def head_pose(face_2d, face_3d, w, h):
    # Преобразование в массив
    face_2d = np.array(face_2d, dtype=np.float64)

    # Преобразование в массив 
    face_3d = np.array(face_3d, dtype=np.float64)

    # Фокусное расстояние
    focal_lenght = 1 * w

    # Матрица камеры
    cam_matrix = np.array([[focal_lenght, 0, h / 2],
                           [0, focal_lenght, w / 2],
                           [0, 0, 1]])

    # Параметры искажения
    dist_matrix = np.zeros((4, 1), dtype=np.float64)

    # Преобразование 3D точки из системы координат объекта в систему координат камеры
    success, rot_vec, tranc_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

    # Получение матрицы вращения
    rmat, jac = cv2.Rodrigues(rot_vec)

    # Получение углов
    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

    # Получение степени вращения
    x = angles[0] * 360
    y = angles[1] * 360

    # Направление головы
    if y < -10:
        pos_head = "RIGHT"
        color = [(0, 255, 255), (147, 20, 255)]
        # print(f'Головая направлена вправо {time.ctime(time.time())}')
        head_turning = True
    elif y > 10:
        pos_head = "LEFT"
        color = [(0, 255, 255), (147, 20, 255)]
        # print(f'Головая направлена влево {time.ctime(time.time())}')
        head_turning = True
    elif x < -10:
        pos_head = "DOWN"
        color = [(0, 255, 255), (147, 20, 255)]
        # print(f'Головая направлена вниз {time.ctime(time.time())}')
        head_turning = True
    elif x > 10:
        pos_head = "UP"
        color = [(0, 255, 255), (147, 20, 255)]
        # print(f'Головая направлена вверх {time.ctime(time.time())}')
        head_turning = True
    else:
        pos_head = "FORWARD"
        color = [(0, 0, 0), (0, 255, 0)]
        head_turning = False

    return pos_head, color, x, y, head_turning


# Функция для количества человек
def people_counter(p_count):
    if p_count == 1:
        more_then_one = False
        no_one = False
    elif p_count > 1:
        more_then_one = True
        no_one = False
    elif p_count < 1:
        more_then_one = False
        no_one = True

    return more_then_one, no_one


# Функция для направления взгляда
def eyes_side(eye_pos_right, eye_pos_left):
    if eye_pos_right == 'LEFT' and eye_pos_left == 'LEFT' and (round(time.time(), 0) % 10 == 0):
        # print(f'Глаза направлены влево {time.ctime(time.time())}')
        looking_away = True
    elif eye_pos_right == 'RIGHT' and eye_pos_left == 'RIGHT' and (round(time.time(), 0) % 10 == 0):
        # print(f'Глаза направлены вправо {time.ctime(time.time())}')
        looking_away = True
    else:
        looking_away = False

    return looking_away


def mediapipe_all(img, w, h, proctoring_type: ProctoringTypeSchema) -> ProctoringResultSchema:
    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(max_num_faces=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:

        img.flags.writeable = False
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(img)

        img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if results.multi_face_landmarks:
            mesh_coords, landmarks = landmarks_detection(img, results)

            p_count = len(landmarks)  # Количество человек в кадре

            landmarks = results.multi_face_landmarks[0].landmark

            right_coords = [mesh_coords[p] for p in RIGHT_EYE]
            left_coords = [mesh_coords[p] for p in LEFT_EYE]
            crop_right, crop_left = eyes_cutout(img, right_coords, left_coords)

            eye_pos_right, color_right = eye_position(crop_right)
            eye_pos_left, color_left = eye_position(crop_left)

            if proctoring_type.looking_away:
                if eye_pos_right and eye_pos_left:
                    looking_away = eyes_side(eye_pos_right, eye_pos_left)
                else:
                    looking_away = True

            else:
                looking_away = None

            if proctoring_type.mouth_opening:
                # Губы
                pos_lips, mouth_open = lips_ratio(landmarks)
            else:
                mouth_open = None

            # Голова
            face_3d = []
            face_2d = []

            for face_lms in results.multi_face_landmarks:
                for idx, lm in enumerate(face_lms.landmark):
                    if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                        x, y = int(lm.x * w), int(lm.y * h)
                        # Получение 2D координат
                        face_2d.append([x, y])
                        # Получение 3D координат
                        face_3d.append([x, y, lm.z])

                if proctoring_type.hints_outside:
                    pos_head, color_head, x, y, head_turning = head_pose(face_2d, face_3d, w, h)
                else:
                    head_turning = None
        else:
            p_count = 0
            looking_away = True if proctoring_type.looking_away else None
            mouth_open = False if proctoring_type.mouth_opening else None
            head_turning = True if proctoring_type.hints_outside else None

        # Подсчет количества человек
        if proctoring_type.absence_person or proctoring_type.extra_person:
            more_then_one, no_one = people_counter(p_count)
        else:
            more_then_one, no_one = None, None

    return ProctoringResultSchema(
        detected_absence_person=no_one,
        detected_extra_person=more_then_one,
        detected_person_substitution=False,  # Проверка не реализована
        detected_looking_away=looking_away,
        detected_mouth_opening=mouth_open,
        detected_hints_outside=head_turning,
    )
