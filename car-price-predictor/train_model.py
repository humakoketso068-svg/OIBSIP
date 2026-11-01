"""Train the car price models locally and export what the Vercel API needs.

Run once on your computer (and again whenever the dataset changes):

    pip install -r requirements-train.txt
    python train_model.py

Needs the CarDekho CSV in this folder, saved as "car data.csv" or
"CAR DETAILS FROM CAR DEKHO.csv". Writes api/model.joblib and api/meta.json,
which you commit and deploy.
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

HERE = Path(__file__).parent
CANDIDATES = ["car data.csv", "CAR DETAILS FROM CAR DEKHO.csv", "cardekho.csv"]
THIS_YEAR = pd.Timestamp.today().year
CAT_COLS = ["brand", "fuel", "seller_type", "transmission"]


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Same cleaning and feature engineering as the notebook."""
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={"car_name": "name", "kms_driven": "km_driven", "fuel_type": "fuel"})
    df = df.drop_duplicates().dropna(subset=["selling_price"]).reset_index(drop=True)

    for col in ["name", "fuel", "seller_type", "transmission"]:
        df[col] = df[col].astype(str).str.strip().str.lower()

    if not pd.api.types.is_numeric_dtype(df["owner"]):
        owner_map = {"first owner": 1, "second owner": 2, "third owner": 3,
                     "fourth & above owner": 4, "test drive car": 0}
        df["owner"] = df["owner"].astype(str).str.strip().str.lower().map(owner_map)
    df["owner"] = df["owner"].fillna(df["owner"].median())
    df["km_driven"] = df["km_driven"].fillna(df["km_driven"].median())

    # One CarDekho version prices cars in lakhs; convert to rupees.
    if df["selling_price"].median() < 1000:
        df["selling_price"] = df["selling_price"] * 100_000

    df["car_age"] = THIS_YEAR - df["year"]
    df["brand"] = df["name"].str.split().str[0].replace({"maruti": "maruti suzuki", "vw": "volkswagen"})
    counts = df["brand"].value_counts()
    df["brand"] = df["brand"].replace(dict.fromkeys(counts[counts < 5].index, "other"))
    return df[["selling_price", "car_age", "km_driven", "owner"] + CAT_COLS]


def main() -> None:
    csv = next((HERE / c for c in CANDIDATES if (HERE / c).exists()), None)
    if csv is None:
        sys.exit(f"Dataset not found. Save the CarDekho CSV here as one of: {CANDIDATES}")

    df = clean(pd.read_csv(csv))
    X = pd.get_dummies(df.drop(columns="selling_price"), columns=CAT_COLS, drop_first=True, dtype=int)
    y = df["selling_price"]
    columns = list(X.columns)

    # Plain numpy arrays: the API builds its input the same way, with no pandas needed at runtime.
    X_tr, X_te, y_tr, y_te = train_test_split(X.values.astype(float), y.values, test_size=0.2, random_state=42)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=3, random_state=42),
    }
    results = {}
    for name, model in models.items():
        model.fit(X_tr, y_tr)
        pred = model.predict(X_te)
        results[name] = {
            "mae": float(mean_absolute_error(y_te, pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_te, pred))),
            "r2": float(r2_score(y_te, pred)),
        }
        print(f"{name:18s} MAE {results[name]['mae']:>12,.0f}  RMSE {results[name]['rmse']:>12,.0f}  R2 {results[name]['r2']:.3f}")

    best = max(results, key=lambda n: results[n]["r2"])
    print("\nBest model:", best)

    out = HERE / "api"
    out.mkdir(exist_ok=True)
    joblib.dump(models[best], out / "model.joblib", compress=3)
    meta = {
        "best": best,
        "results": results,
        "columns": columns,
        "brands": sorted(df["brand"].unique().tolist()),
        "fuels": sorted(df["fuel"].unique().tolist()),
        "sellers": sorted(df["seller_type"].unique().tolist()),
        "transmissions": sorted(df["transmission"].unique().tolist()),
        "median_km": int(df["km_driven"].median()),
        "mae": results[best]["mae"],
        "r2": results[best]["r2"],
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    size_mb = (out / "model.joblib").stat().st_size / 1e6
    print(f"Saved api/model.joblib ({size_mb:.1f} MB) and api/meta.json")
    if size_mb > 50:
        print("Warning: the model file is large; lower n_estimators in this script to keep the deploy small.")


if __name__ == "__main__":
    main()
