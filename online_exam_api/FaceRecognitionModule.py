import cv2
import os
import face_recognition
import FaceDetectionModule
import numpy as np


class FaceRecognizer:
    def __init__(self, refer_path, detect_model=1, min_detect_con=0.6, min_recog_con=0.4):
        self.reference_path = refer_path
        self.detect_model = detect_model
        self.min_recog_con = min_recog_con
        self.min_detect_con = min_detect_con
        self.ref_img_list, self.name_list = self.__get_ref_img_list()
        self.known_face_encodes = self.__get_encoding()
        self.detector = FaceDetectionModule.FaceDetector(model=self.detect_model, minDetectionCon=self.min_detect_con)

    def __get_ref_img_list(self):  # get a list of reference img
        images = []
        names = []
        my_list = os.listdir(self.reference_path)
        for item in my_list:
            img = cv2.imread(f'{self.reference_path}/{item}')
            images.append(img)
            names.append(os.path.splitext(item)[0])
        return images, names

    def __get_encoding(self):  # get a list of encoded faces
        encode_list = []
        ref_img_list, name_list = self.__get_ref_img_list()
        for item in ref_img_list:
            cur_img = cv2.cvtColor(item, cv2.COLOR_BGR2RGB)
            cur_encode = face_recognition.face_encodings(cur_img)[0]
            encode_list.append(cur_encode)
        return encode_list

    def recognize(self, frame):  # return location of known and unknown faces
        img_small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        faces = self.detector.find_faces(img_small)
        face_loc = []
        known_face_loc = []
        known_face_names = []
        unknown_face_loc = []
        for face in faces:
            x, y, w, h = face[1]
            face_tuple = (y, x + w, y + h, x)
            face_loc.append(face_tuple)
        cur_frame_face_encodes = face_recognition.face_encodings(img_small, known_face_locations=face_loc)
        for encodeFace, faceLoc in zip(cur_frame_face_encodes, face_loc):
            face_dis = face_recognition.face_distance(self.known_face_encodes, encodeFace)
            match_idx = np.argmin(face_dis)
            if face_dis[match_idx] < self.min_recog_con:
                name = self.name_list[match_idx]
                known_face_loc.append(faceLoc)
                known_face_names.append(name)
            else:
                unknown_face_loc.append(faceLoc)
        return known_face_names, known_face_loc, unknown_face_loc

    @staticmethod
    def draw_bounding_box(frame, face_location_lst, known_face_names=None):
        if known_face_names is not None:
            color = (0, 255, 0)
            for face_loc, name in zip(face_location_lst, known_face_names):
                y1, x2, y2, x1 = face_loc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness=2)
                cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), color, cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 255, 255), thickness=2)
        else:
            color = (0, 0, 255)
            for face_loc in face_location_lst:
                y1, x2, y2, x1 = face_loc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness=2)
                cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), color, cv2.FILLED)
                cv2.putText(frame, 'Unknown', (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 255, 255), thickness=2)
        return frame
