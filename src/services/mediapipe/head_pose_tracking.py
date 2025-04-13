import cv2
import numpy as np
import mediapipe as mp
from utils import FONT, colorBackgroundText, head_scale
import time

def head_pose(img, draw):
    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img.flags.writeable = False

        results = face_mesh.process(img)

        img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        img_h, img_w, img_c = img.shape
        face_3d = []
        face_2d = []

        if results.multi_face_landmarks:
            for face_lms in results.multi_face_landmarks:
                for idx, lm in enumerate(face_lms.landmark):
                    if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                        if idx == 1:
                            # Координаты носа
                            nose_2d = (lm.x * img_w, lm.y * img_h)

                        x, y = int(lm.x * img_w), int(lm.y * img_h)
                        
                        # Получение 2D координат
                        face_2d.append([x, y])

                        # Получение 3D координат
                        face_3d.append([x, y, lm.z])
                
                # Преобразование 2D координат в массив
                face_2d = np.array(face_2d, dtype=np.float64)

                # Преобразование 3D координат в массив 
                face_3d = np.array(face_3d, dtype=np.float64)
                
                # Фокусное расстояние
                focal_lenght = 1 * img_w

                # Матрица камеры
                cam_matrix = np.array([ [focal_lenght, 0, img_h / 2],
                                        [0, focal_lenght, img_w / 2],
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
                z = angles[2] * 360


                # Направление головы
                if y < -10:
                    pos_head = "RIGHT"
                    color = [(0,255,255), (147,20,255)]
                    print(f'Голова направлена вправо {time.ctime(time.time())}')
                elif y > 10:
                    pos_head = "LEFT"
                    color = [(0,255,255), (147,20,255)]
                    print(f'Голова направлена влево {time.ctime(time.time())}')
                elif x < -10:
                    pos_head = "DOWN"
                    color = [(0,255,255), (147,20,255)]
                    print(f'Голова направлена вниз {time.ctime(time.time())}')
                elif x > 10:
                    pos_head = "UP"
                    color = [(0,255,255), (147,20,255)]
                    print(f'Голова направлена вверх {time.ctime(time.time())}')
                else:
                    pos_head = "FORWARD"
                    color = [(0,0,0), (0,255,0)]

                p1 = (int(nose_2d[0]), int(nose_2d[1]))
                p2 = (int(nose_2d[0] + y * 10), int(nose_2d[1] - x * 10))
                
                # Линия из носа
                #cv2.line(img, p1, p2, (255,0,0), 3)

                scale = head_scale(img_w, img_h)

                #colorBackgroundText(img, f'Head: {pos_head}', FONT, scale[0], (scale[1],scale[2]), scale[3], color[0], color[1], scale[4], scale[4]) #убрать

        return img