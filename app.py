"""
If you are in the same directory as this file (app.py), you can run run the app using gunicorn:
    
    $ gunicorn --bind 0.0.0.0:<PORT> app:app

gunicorn can be installed via:

    $ pip install gunicorn

"""
import os
from pathlib import Path
import logging
from flask import Flask, jsonify, request, abort
import sklearn
import pandas as pd
import joblib
import json
import comet_ml
from comet_ml import API
import pickle
import numpy as np
import xgboost as xgb

import ift6758


LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
PORT = os.environ.get("SERVING_PORT", "8890")

EXPECTED_KEY ="BDQ0IvlidYZwCjQubkQCX7cs0"

app = Flask(__name__)


@app.before_first_request
def before_first_request():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)
    """
    # TODO: setup basic logging configuration
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

    # TODO: any other initialization before the first request (e.g. load default model)
    #comet import default voting ens model
    comet_ml.init()

    if not Path(f'models/model_xgboost_final2.pkl').exists():
        api = API(api_key=EXPECTED_KEY)
        # Download a Registry Model: eg "Q6-Full-ens" registered model name
        api.download_registry_model("yasmine", "model-xgboost-final2", "1.0.0",
                            output_path="models", expand=True)

    logging.info('Default model loaded: Xgboost')

    global model
    model = joblib.load('models/model_xgboost_final2.pkl')
    
    pass


@app.route("/logs", methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""
    
    # TODO: read the log file specified and return the data
    #raise NotImplementedError("TODO: implement this endpoint")

    response = {}
    with open(LOG_FILE) as f:
        for line in f:
            response[line] = line

    return jsonify(response)  # response must be json serializable!


@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    global clf,model
    
    # Get POST json data
    json = request.get_json()
    app.logger.info(json)

    # TODO: check to see if the model you are querying for is already downloaded
    model_swap = json["model"]  #'model_xgboost_final2'
    workspace = json["workspace"]
    version = json["version"]
    api = API(api_key="BDQ0IvlidYZwCjQubkQCX7cs0")
    model_details = api.get_registry_model_details(workspace, model_swap, version)
    filename = model_details['assets'][0]['fileName']
    file_model_path = f"models/{filename}"

    if os.path.isfile(file_model_path):
        model = model_swap
        app.logger.info(f"{model} already stored")
        model_already_exists = True

    else:
        model = model_swap        
        app.logger.info(f"Downloading from COMET {model}")
        api.download_registry_model(workspace, model,version ,
                            output_path="models", expand=True)
        model_already_exists = False


    clf = joblib.load(file_model_path)
    app.logger.info(f"Classifier Swapped with {model}")
    response = {"new_classifier": model_swap,"model_already_exists":model_already_exists}
    
    app.logger.info(response)
    return jsonify(response)  # response must be json serializable!


@app.route("/predict", methods=["POST"])
def predict():
    # Get POST json data
    json1 = request.get_json()
    app.logger.info(json1)

    # TODO:
    #raise NotImplementedError("TODO: implement this enpdoint")
    r = json.dumps(json1)
    X_test =pd.read_json(r)
    model = joblib.load('models/model_xgboost_final2.pkl')
    predictions = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:,1]
    X_test["predictionIsGoal"] = predictions
    X_test["probaIsGoal"] = y_proba
    
    response = X_test[["probaIsGoal","predictionIsGoal"]]
    #response = None

    app.logger.info(response)
    return jsonify(response.to_json())  # response must be json serializable!

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8890, debug=True)