import cv2
import face_recognition
import time

def face_rec(img):
    known_image = face_recognition.load_image_file("D:/finalwork mediapipe/videos/photo_fr.jpg") #тут видимо должна быть первая фотка человека, чтобы сравнивать
    known_face_encoding = face_recognition.face_encodings(known_image)[0]

    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        
        matches = face_recognition.compare_faces([known_face_encoding], face_encoding)

        if True in matches:
            cv2.rectangle(img, (left, top), (right, bottom), (255, 170, 66), 2)
        else:
            cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
            print('--------------------------------')
            print(f'Другой человек {time.ctime(time.time())}')
            print('--------------------------------')

    return img