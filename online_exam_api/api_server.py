from flask import Flask, request
from flask_restful import Api, Resource
from PIL import Image
from datetime import datetime
from detect_student_card_ultis import extract_student_card, extract_name, extract_dob, extract_ID_num
import FaceRecognitionModule
import numpy as np
import cv2

app = Flask(__name__)
api = Api(app)

recognizer = FaceRecognitionModule.FaceRecognizer('reference_images', detect_model=0)


class AttendanceChecking(Resource):
    def post(self):
        # open the pillow img
        file = request.files['image']
        raw_img = Image.open(file.stream)
        # convert pillow img to opencv img
        rgb_img = np.array(raw_img)
        bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
        # extract attendance info
        known_face_names, known_face_loc, unknown_face_loc = recognizer.recognize(bgr_img)
        now = datetime.now()
        date_time = now.strftime('%H:%M:%S')
        return {'Arrival time' : date_time,
                'Known faces names' : known_face_names,
                'Known faces location' : known_face_loc,
                'Unknown faces location' : unknown_face_loc}


class ExtractStudentInfo(Resource):  # TODO: need fixing
    def post(self):
        # open the pillow img
        file = request.files['image']
        raw_img = Image.open(file.stream)
        # convert pillow img to opencv img
        rgb_img = np.array(raw_img)
        bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
        # extract student info
        stu_id_img = extract_student_card(bgr_img)
        name, name_bbox = extract_name(stu_id_img)
        dob, dob_bbox = extract_dob(stu_id_img)
        id_num, id_bbox = extract_ID_num(stu_id_img)
        return {
            'Name' : name,
            'Name location' : name_bbox,
            'Date of birth' : dob,
            'Dob location' : dob_bbox,
            'ID number' : id_num,
            'ID number location' : id_bbox
        }


api.add_resource(AttendanceChecking, '/attendance')
api.add_resource(ExtractStudentInfo, '/studentID')

if __name__ == '__main__':
    app.run(debug=True)
