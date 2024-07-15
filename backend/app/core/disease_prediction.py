from typing import Optional, Tuple

import requests

from PIL import Image
from app import crud
from io import BytesIO
import cv2
import numpy as np
from app.api.src.main import predict

from app.models.temperature import Temperature


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

    # cv2.imshow('Output Image', output_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    total_hot_area = sum(cv2.contourArea(contour) for contour in contours)
    hot_area_percentage = (total_hot_area / (image.shape[0] * image.shape[1])) * 100

    print(f"Hot area percentage: {hot_area_percentage}%")

    percentage_threshold = 16
    is_sick = hot_area_percentage > percentage_threshold

    return is_sick


def get_disease_prediction(image_url):
    result, remedy = predict(image_url)
    return result, remedy


def extract_temperatures(image_url):
    """
    Extracts temperature readings from a thermal image.

    :param image_url: URL of the thermal image.
    :return: List of temperatures extracted from the image.
    """
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))

        # Convert image to grayscale
        gray_image = image.convert("L")

        # Convert to OpenCV format
        open_cv_image = np.array(gray_image)

        # Apply thresholding
        _, thresh_image = cv2.threshold(open_cv_image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Apply dilation and erosion to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed_image = cv2.dilate(thresh_image, kernel, iterations=1)
        processed_image = cv2.erode(processed_image, kernel, iterations=1)

        # Convert back to PIL format
        processed_image_pil = Image.fromarray(processed_image)

        # Use Tesseract to extract text
        text = pytesseract.image_to_string(processed_image_pil, config='--psm 6')
        print(text)

        temperatures = []
        for word in text.split():
            try:
                temperatures.append(float(word))
            except ValueError:
                continue

        print(image_url)
        print(temperatures)
        return temperatures
    else:
        raise Exception(f"Failed to download image from {image_url}")


def is_plant_sick(thermal_image_url, optical_image_url, temperature_current: Temperature,
                  temperature_previous: Temperature, threshold=2.5, weight_thermal=0.5, weight_temp_diff=0.5) -> Tuple[
    bool, Optional[str]]:
    """
    Determine if the plant in the image is sick and predict the disease.

    :param thermal_image_url: URL of the thermal image.
    :param optical_image_url: URL of the optical image.
    :param temperature_current: Current temperature data.
    :param temperature_previous: Previous temperature data.
    :param threshold: Temperature difference threshold to determine sickness.
    :param weight_thermal: Weight of thermal image analysis in sickness determination.
    :param weight_temp_diff: Weight of temperature difference analysis in sickness determination.
    :return: Tuple containing is_sick (boolean) and disease (str or None).
    """
    # Analyze thermal image content
    is_sick_thermal = detect_sick_plant_thermal_image(thermal_image_url)

    # Analyze temperature difference
    is_sick_temp_diff = False
    if temperature_previous and temperature_current:
        temp_diff = abs(temperature_current.average - temperature_previous.average)
        if temp_diff > threshold:
            is_sick_temp_diff = True

    # Combine the results using weights
    combined_sickness_score = (weight_thermal * is_sick_thermal) + (weight_temp_diff * is_sick_temp_diff)

    # Determine final sickness status based on combined score
    is_sick = combined_sickness_score >= 0.5  # This threshold can be adjusted

    disease = None
    if is_sick:
        disease = get_disease_prediction(optical_image_url)

    return is_sick, disease
