# Car Price Predictor (Vercel)

A responsive web app that predicts a used car's selling price.

* `public/index.html` is the responsive front end (static, served by Vercel).
* `api/index.py` is a Flask API running as a Vercel Python function. It loads a pre-trained model and answers `/api/meta` and `/api/predict`.
* `train_model.py` trains Linear Regression, Random Forest and Gradient Boosting on the CarDekho data and saves the best one to `api/model.joblib` and `api/meta.json`.

Vercel cannot run Streamlit (it needs a long-running server), so the model is trained once on your computer and Vercel only loads it.

> **The model is already trained** on your `cardekho.csv` (Random Forest, R² 0.73, MAE about ₹130,000) and saved in `api/`.
> You can skip step 1 and go straight to deploying. Only re-run `train_model.py` if you change the dataset or training code.

## 1. Train the model (on your computer, optional)

1. Download the CarDekho dataset from Kaggle and save it in this folder as `car data.csv` (or `CAR DETAILS FROM CAR DEKHO.csv`).
2. Run:
   ```bash
   pip install -r requirements-train.txt
   python train_model.py
   ```
   This prints MAE, RMSE and R² for each model and creates `api/model.joblib` and `api/meta.json`. **Both files must be committed.**

## 2. Try it locally (optional)

```bash
pip install -r requirements.txt
python app.py        # open http://localhost:3000
```

## 3. Deploy to Vercel

1. Push this folder to a GitHub repo. The CSV is git-ignored on purpose, and the trained model files are included.
   ```bash
   git init
   git add .
   git commit -m "Car price predictor"
   git branch -M main
   git remote add origin https://github.com/<your-username>/car-price-predictor.git
   git push -u origin main
   ```
2. On [vercel.com](https://vercel.com): **Add New** → **Project** → import the repo → **Deploy**. No build settings are needed.

Or with the CLI: `npm i -g vercel`, then `vercel` in this folder.

## Notes

* Re-run `train_model.py` and push again whenever you change the dataset or the training code.
* Use the same `scikit-learn` version for training and deploying, because a saved model only loads reliably on the version that created it. Both requirements files pin it to `1.9.1`.
* If the page says "Model not available", `api/model.joblib` and `api/meta.json` were not committed.
* The Vercel function limit is about 250 MB unzipped. If `train_model.py` warns the model file is large, lower `n_estimators` for the Random Forest.
