
import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from flask import Flask, jsonify, request, send_from_directory

HERE = Path(__file__).parent
PUBLIC = HERE.parent / "public"

app = Flask(__name__)


try:
    MODEL = joblib.load(HERE / "model.joblib")
    META = json.loads((HERE / "meta.json").read_text())
    LOAD_ERROR = None
except Exception as exc:  
    MODEL, META, LOAD_ERROR = None, None, str(exc)


def _unavailable():
    return jsonify(error="Model not available. Run train_model.py and commit api/model.joblib and api/meta.json."), 503


@app.get("/api/meta")
def meta():
    if MODEL is None:
        return _unavailable()
    keys = ["best", "brands", "fuels", "sellers", "transmissions", "median_km", "mae", "r2", "results"]
    return jsonify({k: META[k] for k in keys})


@app.post("/api/predict")
def predict():
    if MODEL is None:
        return _unavailable()

    data = request.get_json(silent=True) or {}
    this_year = datetime.now().year
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
    mae = META["mae"]
    return jsonify(price=price, low=max(price - mae, 0.0), high=price + mae, model=META["best"], r2=META["r2"])



@app.get("/")
def home():
    return send_from_directory(PUBLIC, "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=3000)
