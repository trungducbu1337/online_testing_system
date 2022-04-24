import cv2
import numpy as np
import pytesseract
from blend_modes import divide
from pytesseract import Output
import re
from PIL import Image
import os


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_student_card(img, canny_threshold=(50, 60), gaussian_ksize=(3, 3), dilate_ksize=(9, 9), width_return=1265, height_return=800):
    """
    extract the student card from the img
    :param img: img to be extracted
    :param canny_threshold: threshold for edge detection
    :param gaussian_ksize: kernel size for gaussian blur
    :param dilate_ksize: kernel size for dilation
    :param width_return: the width of the returned img
    :param height_return: the height of the returned img
    :return: img contain only ID card
    """
    global img_transform_perspective
    width = 800
    height = 800
    center = (width // 2, height // 2)
    # find contour of the ID card
    dilate_kernel = np.ones(dilate_ksize)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blurr = cv2.GaussianBlur(img_gray, gaussian_ksize, 0)
    img_canny = cv2.Canny(img_blurr, canny_threshold[0], canny_threshold[1])
    img_dilate = cv2.dilate(img_canny, kernel=dilate_kernel, iterations=3)
    img_threshold = cv2.erode(img_dilate, dilate_kernel, iterations=3)
    contours, _ = cv2.findContours(img_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_cont, max_area = biggest_contour(contours)
    # transform perspective
    if max_cont.size != 0:
        max_cont = reorder(max_cont)
        pts1 = np.float32(max_cont)  # PREPARE POINTS FOR WARP
        pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])  # PREPARE POINTS FOR WARP
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        img_transform_perspective = cv2.warpPerspective(img, matrix, (width, height))  # transform perspective
    # correct the skew angle
    filename = "Student_ID_Card/{}.png".format(os.getpid())
    cv2.imwrite(filename, img_transform_perspective)
    orient_dict = pytesseract.image_to_osd(filename, output_type=Output.DICT)
    angle = orient_dict['rotate']
    if angle == 270:
        angle = -angle
    if angle != 0:
        m = cv2.getRotationMatrix2D(center, angle, 1.0)
        img_transform_perspective = cv2.warpAffine(img_transform_perspective, m, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    os.remove(filename)
    # return the ID card
    return cv2.resize(img_transform_perspective, (width_return, height_return), interpolation=cv2.INTER_AREA)


def biggest_contour(contours):
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        peri = cv2.arcLength(i, True)
        approx = cv2.approxPolyDP(i, 0.02 * peri, True)
        if area > max_area and len(approx) == 4:
            biggest = approx
            max_area = area
    return biggest, max_area


def reorder(my_points):
    my_points = my_points.reshape((4, 2))
    my_points_new = np.zeros((4, 1, 2), dtype=np.int32)
    add = my_points.sum(1)
    my_points_new[0] = my_points[np.argmin(add)]
    my_points_new[3] = my_points[np.argmax(add)]
    diff = np.diff(my_points, axis=1)
    my_points_new[1] = my_points[np.argmin(diff)]
    my_points_new[2] = my_points[np.argmax(diff)]
    return my_points_new


def draw_rectangle(img, max_contour, thickness):
    cv2.line(img, (max_contour[0][0][0], max_contour[0][0][1]), (max_contour[1][0][0], max_contour[1][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (max_contour[0][0][0], max_contour[0][0][1]), (max_contour[2][0][0], max_contour[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (max_contour[3][0][0], max_contour[3][0][1]), (max_contour[2][0][0], max_contour[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (max_contour[3][0][0], max_contour[3][0][1]), (max_contour[1][0][0], max_contour[1][0][1]), (0, 255, 0), thickness)
    return img


def de_shadow(image):
    # splitting the image into channels
    bA = image[:, :, 0]
    gA = image[:, :, 1]
    rA = image[:, :, 2]

    # dialting the image channels individually to spead the text to the background
    dilated_image_bB = cv2.dilate(bA, np.ones((7,7), np.uint8))
    dilated_image_gB = cv2.dilate(gA, np.ones((7,7), np.uint8))
    dilated_image_rB = cv2.dilate(rA, np.ones((7,7), np.uint8))

    # blurring the image to get the backround image
    bB = cv2.medianBlur(dilated_image_bB, 21)
    gB = cv2.medianBlur(dilated_image_gB, 21)
    rB = cv2.medianBlur(dilated_image_rB, 21)

    # blend_modes library works with 4 channels, the last channel being the alpha channel
    # so we add one alpha channel to our image and the background image each
    image = np.dstack((image, np.ones((image.shape[0], image.shape[1], 1))*255))
    image = image.astype(float)
    dilate = [bB,gB,rB]
    dilate = cv2.merge(dilate)
    dilate = np.dstack((dilate, np.ones((image.shape[0], image.shape[1], 1))*255))
    dilate = dilate.astype(float)

    # now we divide the image with the background image
    # without rescaling i.e scaling factor = 1.0
    blend = divide(image,dilate,1.0)
    blendb = blend[:, :, 0]
    blendg = blend[:, :, 1]
    blendr = blend[:, :, 2]
    blend_planes = [blendb,blendg,blendr]
    blend = cv2.merge(blend_planes)
    # blend = blend*0.85
    blend = np.uint8(blend)

    # returning the shadow-free image
    return blend


def extract_ID_num(ID_card_img, dilate_ksize=(3, 3)):
    """
    extract student ID number and the bounding box of the ID num
    :param ID_card_img: img contain only ID card
    :param dilate_ksize: kernel size for dilation
    :return: ID number of the student ID card and the bounding box of the ID num
    """
    bbox = 0, 0, 0, 0
    dilate_kernel = np.ones(dilate_ksize)
    img_stu_card = preprocess_img(ID_card_img)
    img_erode = cv2.erode(img_stu_card, dilate_kernel, iterations=9)
    img_dilate = cv2.dilate(img_erode, dilate_kernel, iterations=9)
    cur_img = cv2.bitwise_not(img_dilate)
    img_canny = cv2.Canny(cur_img, 0, 255)
    contours, hierarchy = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 2500:
            peri = cv2.arcLength(cont, True)
            approx = cv2.approxPolyDP(cont, 0.02 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)
            if x > 940 and y > 650 and w > 160 and h > 40:
                bbox = (x - 10, y - 10, w + 20, h + 20)
    if bbox == (0, 0, 0, 0):
        bbox = (949, 691, 235, 99)
    prep_img = img_stu_card[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]]
    filename = "Student_ID_Card/{}.png".format(os.getpid())
    cv2.imwrite(filename, prep_img)  # temporary save
    text_ID = pytesseract.image_to_string(Image.open(filename), lang='eng')
    os.remove(filename)
    stu_ID = find_ID_num(text_ID)
    return stu_ID, bbox


def extract_dob(ID_card_img, dilate_ksize=(3, 3)):
    """
    get date of birth and the bounding box of dob
    :param ID_card_img: img contain only ID card
    :param dilate_ksize: kernel size for dilation
    :return: date of birth and the bounding box of dob
    """
    bbox = 0, 0, 0, 0
    dilate_kernel = np.ones(dilate_ksize)
    img_stu_card = preprocess_img(ID_card_img)
    img_erode = cv2.erode(img_stu_card, dilate_kernel, iterations=9)
    img_dilate = cv2.dilate(img_erode, dilate_kernel, iterations=9)
    cur_img = cv2.bitwise_not(img_dilate)
    img_canny = cv2.Canny(cur_img, 0, 255)
    contours, hierarchy = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 2500:
            peri = cv2.arcLength(cont, True)
            approx = cv2.approxPolyDP(cont, 0.02 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)
            if x < 60 and 350 < y < 450 and w > 250:
                bbox = (x - 20, y - 20, w + 40, h + 40)
    if bbox == (0, 0, 0, 0):
        bbox = (17, 355, 338, 125)
    prep_img = img_stu_card[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]]
    filename = "Student_ID_Card/{}.png".format(os.getpid())
    cv2.imwrite(filename, prep_img)  # temporary save
    text_dob = pytesseract.image_to_string(Image.open(filename), lang='eng')
    os.remove(filename)
    stu_dob = find_dob(text_dob)
    return stu_dob, bbox


def extract_name(ID_card_img, dilate_ksize=(3, 3)):
    """
    get name and the bounding box of name
    :param ID_card_img: img contain only ID card
    :param dilate_ksize: kernel size for dilation
    :return: name and the bounding box of name
    """
    bbox = 0, 0, 0, 0
    dilate_kernel = np.ones(dilate_ksize)
    img_stu_card = preprocess_img(ID_card_img)
    img_erode = cv2.erode(img_stu_card, dilate_kernel, iterations=9)
    img_dilate = cv2.dilate(img_erode, dilate_kernel, iterations=9)
    cur_img = cv2.bitwise_not(img_dilate)
    img_canny = cv2.Canny(cur_img, 0, 255)
    contours, hierarchy = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 2500:
            peri = cv2.arcLength(cont, True)
            approx = cv2.approxPolyDP(cont, 0.02 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)
            if x < 60 and 250 < y < 350 and w > 250:
                bbox = (x - 20, y - 20, w + 350, h + 40)
    if bbox == (0, 0, 0, 0):
        bbox = (15, 250, 645, 120)
    prep_img = img_stu_card[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]]
    filename = "Student_ID_Card/{}.png".format(os.getpid())
    cv2.imwrite(filename, prep_img)  # temporary save
    text_name = pytesseract.image_to_string(Image.open(filename), lang='eng')
    os.remove(filename)
    name = find_name(text_name)
    return name, bbox


def preprocess_img(ID_card_img):
    """
    return a preprocessed image for OCR
    :param ID_card_img: img contain only ID card
    :return: a preprocessed image for OCR
    """
    img_stu_card = de_shadow(ID_card_img)
    gray = cv2.cvtColor(img_stu_card, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 5)
    return thresh


def find_dob(text):
    match = re.findall(r'\d{2}\/\d{2}\/\d{4,5}', text)
    result = ''.join(match)
    return result


def find_ID_num(text):
    list_of_numbers = re.findall(r'2\d{7}', text)
    result_number = ''.join(list_of_numbers)
    return result_number


def find_name(text):
    name = ''
    for item in text.split('\n'):
        if item.isupper():
            name += item + ' '
    name = name.rstrip(' ')
    return name
