import cv2 as cv
import numpy as np

class CVImage:

    def __init__(self, image):
        self.img_path = image
        self.image = cv.imread(image)
        self.color_blue = (255, 0, 0)
        self.color_white = (255, 255, 255)
        self.unitCharlength = 8

    def draw_frame(self, location):
        left, top, right, bottom = location

        cv.rectangle(self.image, (left, top), (right, bottom), self.color_blue, 1)
        return self

    def draw_labeled_frame(self, location, label):
        left, top, right, bottom = self.location = location

        cv.rectangle(self.image, (left, top), (right, bottom), self.color_blue, 1)
        cv.rectangle(self.image, (right, top), (right + (self.unitCharlength*(len(label)+1)), bottom), self.color_blue, cv.FILLED)
        cv.putText(self.image, label, (right + self.unitCharlength, top + 10), cv.FONT_HERSHEY_SIMPLEX, 0.33, self.color_white, 1)
        return self

    def make_transparent(self, alpha = 0.5):
        # Not Working still now
        image_copy = self.image.copy()
        image_mask = np.zeros_like(image_copy)
        left, top, right, bottom = self.location
        cv.rectangle(image_mask, (left, top), (right, bottom), self.color_blue, 1)
        cv.rectangle(image_mask, (right, top), (right + (self.unitCharlength*6), bottom), self.color_blue, cv.FILLED)
        self.image = cv.addWeighted(image_mask, alpha, self.image, 1 - alpha, 0)
        return self

    def write_image(self, destination):
        cv.imwrite(destination, self.image)