import io
import requests
from PIL import Image, UnidentifiedImageError

from app.api.src.model_files.ml_predict import Network, predict_plant


def predict(image_url: str):
    try:
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()  # Ensure the request was successful

        imgdata = response.content

        # Validate image data by trying to open it
        try:
            image = Image.open(io.BytesIO(imgdata))
            image.verify()  # Verify that it is, in fact, an image
        except UnidentifiedImageError as e:
            print(e)
            raise ValueError("Unidentified image data")

        model = Network()
        result, remedy = predict_plant(model, imgdata)
        return result, remedy
    except (requests.RequestException, ValueError) as e:
        # Handle or log the error appropriately
        print(f"Error downloading or identifying image: {e}")
        return None, None