import requests
import cv2
import FaceDetectionModule

base_url = 'http://127.0.0.1:5000'


def webcam():
    detector = FaceDetectionModule.FaceDetector(minDetectionCon=0.8)
    ret_bin_frames = []
    count = 0
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return []
    while True:
        # read frame from webcam
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        # detect faces in the frame
        faces = detector.find_faces(frame)
        display = detector.drawBoundingBox(frame, faces)
        if count % 10 == 0 and len(ret_bin_frames) < 20:
            if faces[0][2] > 0.9:
                ret_bin_frames.append(cv2.imencode('.jpg', frame)[1].tobytes())
        cv2.imshow('Webcam', display)
        if cv2.waitKey(16) & 0xFF == ord('q'):
            break
    return ret_bin_frames


def get_attendance_info(bin_images):
    ret_info = []
    for img in bin_images:
        my_img = {'image' : img}
        response = requests.post(base_url + '/attendance', files=my_img)
        ret_info.append(response.json())
    return ret_info


def get_stu_id_info(stu_id_path):
    stu_id = {'image' : open(stu_id_path, 'rb')}
    response = requests.post(base_url + '/studentID', files=stu_id)
    print(response.json())


if __name__ == '__main__':
    bin_img_lst = webcam()
    for item in get_attendance_info(bin_img_lst):
        print(item)