import requests

from app import crud
from io import BytesIO
import cv2
import numpy as np


def detect_sick_plant_thermal_image(image_url):
    response = requests.get(image_url)
    image_bytes = BytesIO(response.content)
    image_array = np.asarray(bytearray(image_bytes.read()), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)

    threshold = np.percentile(image, 80)
    _, binary_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5, 5), np.uint8)
    binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(output_image, contours, -1, (0, 255, 0), 2)

    cv2.imshow('Output Image', output_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    total_hot_area = sum(cv2.contourArea(contour) for contour in contours)
    hot_area_percentage = (total_hot_area / (image.shape[0] * image.shape[1])) * 100

    print(f"Hot area percentage: {hot_area_percentage}%")

    percentage_threshold = 5
    is_sick = hot_area_percentage > percentage_threshold

    return is_sick


def get_disease_prediction(image_url):
    pass


def is_plant_sick(image_url):
    is_sick = detect_sick_plant_thermal_image(image_url)
    if is_sick:
        get_disease_prediction(image_url)
