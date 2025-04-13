import cv2
import time
from utils import fps_scale, colorBackgroundText, FONT
from face_id import face_rec
from face_landmark import landmarks_face
from eyes_tracking import eyes_move
from head_pose_tracking import head_pose
from people_counter import people_count
from mouth_tracking import mouth_open
from medipipe_join_tracking import mediapipe_all

def main(img):
    #cap = cv2.VideoCapture("D:/finalwork mediapipe/videos/video_fr11.mp4")
    #cap = cv2.VideoCapture(0)
    p_time = 0
    #w, h = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    #scale = fps_scale(w, h)

    frame_count = 0
    frame_number = 1

    #while True:
        #success, img = cap.read() #получает кадры видео

    #if not success:
        # if cv2.waitKey(2) & 0xFF == ord('q'):
        #     break
        #if (cv2.getWindowProperty('webcam', cv2.WND_PROP_VISIBLE) < 1) or (cv2.waitKey(1) & 0xFF == ord('q')):  # если метод waitKey(1) получает сигнал и становится равен true, то останавливаемся
            #break
        #continue

        #c_time = time.time()
        #fps = 1 / (c_time - p_time)
        #p_time = c_time

        # if (round(p_time, 0) % 60 == 0):
        #     img = face_rec(img)

        # img = landmarks_face(img, True) # Ключевые точки лица
        # img = people_count(img, w, h) # Подсчет человек
        # img = eyes_move(img, w, h, False) # Движние глаз
        # img = head_pose(img, False) # Поворот головы
        # img = mouth_open(img, w, h) # Открытие рта

    image = cv2.imread(img)
    h, w = image.shape[:2]

    if frame_count % frame_number == 0:
        #print(frame_count)
        img, result_dict = mediapipe_all(img, w, h, False)
        print(result_dict)
        ##img = face_rec(img)
        frame_count += 1
    else:
         # # print(current_frame)
         frame_count += 1

        
        #colorBackgroundText(img, f"FPS: {int(fps)}", FONT, scale[0], (scale[1],scale[2]), scale[3], (0,255,255), (0,0,0), scale[4], scale[4])

        #cv2.imshow('webcam', img)

        #cv2.waitKey(1)


    #cap.release()
    #cv2.destroyAllWindows()

    #if __name__ == "__main__":
       #main()