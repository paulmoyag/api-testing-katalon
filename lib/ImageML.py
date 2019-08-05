from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
import cv2
from collections import Counter
from skimage.color import rgb2lab, deltaE_cie76
import config
import os

temp_path = config.DEFAULT_CONFIG['temp_path']
black = [0,0,0, 255]
white = [255,255,255,255]
gray = [255,255,255,0]
white_1 =  [254, 254, 254]

def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

def get_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def get_colors(path,image, number_of_colors, show_chart):
    modified_image = cv2.resize(get_image(path+'/'+image), (400, 400), interpolation = cv2.INTER_AREA)
    modified_image = modified_image.reshape(modified_image.shape[0]*modified_image.shape[1], 3)
    clf = KMeans(n_clusters = number_of_colors)
    labels = clf.fit_predict(modified_image)
    counts = Counter(labels)
    center_colors = clf.cluster_centers_

    # We get ordered colors by iterating through the keys
    ordered_colors = [center_colors[i] for i in counts.keys()]
    hex_colors = [RGB2HEX(ordered_colors[i]) for i in counts.keys()]
    rgb_colors = [ordered_colors[i] for i in counts.keys()]

    y = 0
    for x in ordered_colors:
        if [int(x[0]), int(x[1]), int(x[2])] in [black, white, gray, white_1]:
            ordered_colors = np.delete(ordered_colors, y, 0)
            counts.pop(y)
            hex_colors.pop(y)
        y+=1

    file, ext = os.path.splitext(image)
    if (show_chart):
        plt.figure(figsize = (8, 6))
        plt.pie(counts.values(), labels = hex_colors, colors = hex_colors)
        plt.savefig(path+'/'+file+'_pie'+ext)

    return file+'_pie'+ext
