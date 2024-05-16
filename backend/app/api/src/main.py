#from torch.functional import split
from app.api.src.model_files.ml_predict import predict_plant, Network
import base64


# @app.route('/', methods=['POST'])
def predict(image):
    # key_dict = request.get_json()
    # image = key_dict["image"]
    imgdata = base64.b64decode(image)
    model = Network()
    result, remedy = predict_plant(model, imgdata)
    # plant = result.split("___")[0]

    # disease = " ".join((result.split("___")[1]).split("_"))
    response = {
        "disease": result,
        "remedy": remedy,
    }

    # response = jsonify(response)
    return response
