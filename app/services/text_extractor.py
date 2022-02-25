import sys
import keras_ocr
import cv2 as cv
import numpy as np

class TextExtractor:

    def __init__(self):
        self.pipeline = keras_ocr.pipeline.Pipeline()

    def build_data(self, data, return_string=False):
        detected_data = {}
        for label, roi in data.items():
            prediction_groups = self.pipeline.recognize([roi])
            predicted = [text for predictions in prediction_groups for text, box in predictions]
            if return_string is False:
                detected_data[label] = predicted
            else:
                detected_data[label] = ' '.join(predicted)

        return detected_data

    def adaptative_thresholding(self, img):
        img = cv.medianBlur(img, 5)
        return cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv.THRESH_BINARY,11,2)

    def noise_removal(self, img):
        kernel = np.ones((1, 1), np.uint8)
        img = cv.dilate(img, kernel, iterations=1)
        kernel = np.ones((1, 1), np.uint8)
        img = cv.erode(img, kernel, iterations=1)
        img = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)
        img = cv.medianBlur(img, 5)
        return img

    def thick_font(self, img):
        img = cv.bitwise_not(img)
        kernel = np.ones((3,3),np.uint8)
        img = cv.dilate(img, kernel, iterations=1)
        img = cv.bitwise_not(img)
        return img