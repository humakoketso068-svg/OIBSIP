
import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from flask import Flask, jsonify, request, send_from_directory

HERE = Path(__file__).parent
MODEL_DIR = HERE / "model"   # saved by the notebook
PUBLIC = HERE / "public"

app = Flask(__name__)

# load the model once at startup
try:
    MODEL = joblib.load(MODEL_DIR / "model.joblib")
    META = json.loads((MODEL_DIR / "meta.json").read_text())
except Exception as exc:
    # probably means the notebook wasn't run yet
    print("Could not load the model:", exc)
    MODEL, META = None, None


def _unavailable():
    return jsonify(error="Model not available. Run car_price_prediction.ipynb to create model/model.joblib and model/meta.json."), 503


@app.get("/")
def home():
    return send_from_directory(PUBLIC, "index.html")


@app.get("/api/meta")
def meta():
    if MODEL is None:
        return _unavailable()
    keys = ["best", "brands", "fuels", "sellers", "transmissions", "median_km", "mae", "r2", "results", "importance"]
    return jsonify({k: META[k] for k in keys})


@app.post("/api/predict")
def predict():
    if MODEL is None:
        return _unavailable()

    data = request.get_json(silent=True) or {}
    this_year = datetime.now().year

    # get the inputs from the request
    try:
        year = int(data["year"])
        km = float(data["km"])
        owner = int(data["owner"])
        cats = {
            "brand": str(data["brand"]).lower(),
            "fuel": str(data["fuel"]).lower(),
            "seller_type": str(data["seller_type"]).lower(),
            "transmission": str(data["transmission"]).lower(),
        }
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Missing or invalid fields."), 400

    if not (1995 <= year <= this_year) or not (0 <= km <= 1_000_000) or owner not in (1, 2, 3, 4):
        return jsonify(error="Year, kilometres or owners out of range."), 400

    options = {"brand": META["brands"], "fuel": META["fuels"],
               "seller_type": META["sellers"], "transmission": META["transmissions"]}
    for key, value in cats.items():
        if value not in options[key]:
            return jsonify(error=f"Unknown {key}: {value}"), 400

    
    numeric = {"car_age": this_year - year, "km_driven": km, "owner": owner}
    chosen = {f"{key}_{value}" for key, value in cats.items()}
    row = [numeric[c] if c in numeric else (1.0 if c in chosen else 0.0) for c in META["columns"]]

    price = max(float(MODEL.predict(np.array([row], dtype=float))[0]), 0.0)
    mae = META["mae"]  # used as a rough +/- range
    return jsonify(price=price, low=max(price - mae, 0.0), high=price + mae, model=META["best"], r2=META["r2"])


if __name__ == "__main__":
    # for running locally, Render uses gunicorn and Vercel finds app on its own
    app.run(debug=True, port=3000)
