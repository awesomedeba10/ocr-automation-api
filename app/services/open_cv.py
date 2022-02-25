import cv2 as cv
import numpy as np

class CVImage:

    def __init__(self, image):
        self.img_path = image
        self.image = cv.imread(image)
        self.color_blue = (255, 0, 0)
        self.color_white = (255, 255, 255)
        self.color_green = (0, 255, 0)
        self.color_red = (0, 0, 255)
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

    def write_targeted_image(self, destination, image):
        cv.imwrite(destination, image)

    def initdocument(self, doc):
        self.userdoc = cv.imread(doc)
        return self

    def match_keypoints(self, goodPercent = 25):
        docKp, docDes = self.__detectAndComputeOrb(self.userdoc)
        templateKp, templateDes = self.__detectAndComputeOrb(self.image)
        bf = cv.BFMatcher(cv.NORM_HAMMING)
        matches = bf.match(docDes, templateDes)
        matches.sort(key=lambda d: d.distance)
        good = matches[:int(len(matches)*(goodPercent/100))]

        srcPoints = np.float32([docKp[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dstPoints = np.float32([templateKp[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, _ = cv.findHomography(srcPoints, dstPoints, cv.RANSAC, 5.0)
        h, w, c = self.image.shape
        imgScan = cv.warpPerspective(self.userdoc, M, (w,h))
        imgScan = cv.resize(imgScan, (w, h))
        return imgScan

    def drawLabelsonDoc(self, image, ROIs, alpha = 0.5, label=True):
        image_mask = np.zeros_like(image)
        for label, roi in ROIs.items():
            left, top, right, bottom = roi
            cv.rectangle(image_mask, (left, top), (right, bottom), self.color_blue, cv.FILLED)
            # cv.rectangle(image_mask, (right, top), (right + (self.unitCharlength*(len(label)+1)), bottom), self.color_blue, cv.FILLED)
            if label:
                cv.putText(image_mask, label, (right + self.unitCharlength, top + 9), cv.FONT_HERSHEY_SIMPLEX, 0.35, self.color_white, 1)
            labeledImage = cv.addWeighted(image, alpha, image_mask, 1 - alpha, 0)
        return labeledImage

    def getCroppedImage(self, image, ROIs):
        img_data = {}
        for label, roi in ROIs.items():
            left, top, right, bottom = roi
            img_data[label] = image[top:bottom, left:right]

        return img_data

    def __createOrb(self, maxCount = 5000):
        return cv.ORB_create(maxCount)

    def __detectAndComputeOrb(self, imageFile):
        orb = self.__createOrb(6000)
        return orb.detectAndCompute(imageFile, None)
