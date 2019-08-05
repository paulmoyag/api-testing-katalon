from sklearn.cluster import KMeans
from collections import Counter
import cv2 #for resizing image
import numpy as np

def get_centered_image():
        monkey_img = cv2.imread("C:/temp/200084505.png", 1)
        big_img_hsv = cv2.imread("C:/temp/200084505.png", 1)

        # define green value range
        big_img_hsv = cv2.cvtColor(big_img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(big_img_hsv, (36, 0, 0), (70, 255,255))

        # find the contours in the mask
        img, contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find the contour with max area
        cnt = sorted(contours, key=cv2.contourArea, reverse=True)[0]
        # cv2.drawContours(big_img, [cnt], 0, (0,0,255), 3)

        # Find the bounding box in that region
        x,y,w,h = cv2.boundingRect(cnt)
        rect = (x, y), (x + w, y + h)
        #cv2.rectangle(big_img,(x,y),(x+w,y+h),(0,255,0),2)

        # Put the monkey to that region
        img_height, img_width = monkey_img.shape[:2]

        # you like to put the monkey image to the center of this region
        center_x = int(round(x + w / 2))
        center_y = int(round(y + h / 2))
        # so the starting point should be
        start_x = int(round(center_x - img_width / 2))
        start_y = int(round(center_y - img_height / 2))

        mask_img = np.where(monkey_img==[0,0,0])

        # Grap information from original image
        crop_from_original = monkey_img[start_y: start_y + img_height, start_x: start_x+img_width ]
        return crop_from_original

def get_dominant_color(image, k=4, image_processing_size = None):
    """
    >>> get_dominant_color(my_image, k=4, image_processing_size = (25, 25))
    [56.2423442, 34.0834233, 70.1234123]
    """
    #resize image if new dims provided
    if image_processing_size is not None:
        image = cv2.resize(image, image_processing_size,
                            interpolation = cv2.INTER_AREA)

    #reshape the image to be a list of pixels
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    #cluster and assign labels to the pixels
    clt = KMeans(n_clusters = k)
    labels = clt.fit_predict(image)

    #count labels to find most popular
    label_counts = Counter(labels)

    #subset out most popular centroid
    dominant_color = clt.cluster_centers_[label_counts.most_common(1)[0][0]]

    return list(dominant_color)