import cv2
import mediapipe as mp

def landmarks_detection(img, results, draw=False):
    img_height, img_width = img.shape[:2]
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw:
        [cv2.circle(img, p, 1, (0,255,0), -1) for p in mesh_coord] #убрать или поставить False

    return mesh_coord

def landmarks_face(img, draw = False):

    mp_face_mesh = mp.solutions.face_mesh
    mp_draw = mp.solutions.drawing_utils

    draw_spec_dot = mp_draw.DrawingSpec(thickness=0, circle_radius=1, color=(0, 255, 0))
    draw_spec_con = mp_draw.DrawingSpec(thickness=1, circle_radius=0, color=(0, 255, 0))

    with mp_face_mesh.FaceMesh(max_num_faces=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:

        img.flags.writeable = False
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results  = face_mesh.process(img)

        img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if results.multi_face_landmarks:
            #mesh_coords = landmarks_detection(img, results, draw_all)
            for face_lms in results.multi_face_landmarks:
                if draw:
                    mp_draw.draw_landmarks(img, landmark_list=face_lms, 
                                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                                        landmark_drawing_spec=draw_spec_dot,
                                        connection_drawing_spec=draw_spec_con)

    return img