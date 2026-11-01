# Car Price Predictor

A small web app that guesses the selling price of a used car. You type in the brand, year, kilometres, fuel type, transmission, number of owners and seller type, and it gives you a price in rupees plus a rough range.

I built it for Task 3 of my data science internship. The model is trained on the CarDekho used car dataset from Kaggle (about 8,100 cars).

## How it works

I cleaned the data (removed duplicates, fixed the casing of values like "Petrol" and "petrol", filled in missing numbers), then worked out the car's age from its year and pulled the brand out of the car name. I trained three models: Linear Regression, Random Forest and Gradient Boosting. Random Forest did best, so that is the one the app uses.

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Random Forest | 129,804 | 245,273 | 0.73 |
| Gradient Boosting | 130,494 | 252,139 | 0.71 |
| Linear Regression | 167,713 | 312,830 | 0.55 |

So on average the prediction is off by about ₹130,000. That is fine for a rough idea, but it won't replace a proper valuation. The model doesn't know about things like condition, accidents or the exact trim level.

The page in `public/` is plain HTML, CSS and JavaScript. It sends the form to a small Flask API in `api/index.py`, which loads the saved model and returns the price.

## Project layout

```
api/
  index.py          Flask API (/api/meta and /api/predict)
  model.joblib      the trained model
  meta.json         dropdown options and scores
public/
  index.html        the page
train_model.py      cleans the data and trains the models
vercel.json         tells Vercel how to route /api
requirements.txt    packages the API needs
requirements-train.txt   packages for training
```

## Run it on your computer

```
pip install flask numpy scikit-learn joblib
python api/index.py
```

Then open http://127.0.0.1:3000 in your browser.

## Retrain the model

Only needed if you change the dataset or the training code. Put the CarDekho CSV in the project folder (named `cardekho.csv` or `car data.csv`) and run:

```
pip install -r requirements-train.txt
python train_model.py
```

This overwrites `api/model.joblib` and `api/meta.json`.

## Deploy on Vercel

1. Push the project to a GitHub repo.
2. On vercel.com choose Add New, then Project, import the repo and press Deploy. No settings need changing.

Make sure `api/model.joblib` and `api/meta.json` are in the repo, otherwise the page will say the model is not available. The CSV is left out on purpose (see `.gitignore`).

## Notes

- Prices are in Indian rupees because that is what the dataset uses.
- The scikit-learn version is pinned to 1.9.1 in both requirements files. A saved model only loads reliably on the version that created it, so keep them the same.
- Built with Python, pandas, scikit-learn, Flask and a bit of JavaScript.
