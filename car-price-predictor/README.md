# Car Price Predictor

Type in a used car's details and it tells you roughly what it should sell for. I made it for Task 3 of my data science internship.

It uses the CarDekho dataset from Kaggle, around 8,100 cars. You enter the brand, year, kilometres, fuel type, transmission, how many owners it's had and whether it's being sold by a dealer or an individual. Prices come out in rupees because that's what the dataset uses.

## What I did

First I cleaned the data: dropped duplicate rows, made values like "Petrol" and "petrol" the same thing, and filled in the few missing numbers. Then I worked out each car's age from its year and took the brand from the first word of the car name.

I tried Linear Regression, Random Forest and Gradient Boosting. Random Forest came out best (R² of 0.73, and it's off by about ₹130,000 on average), with Gradient Boosting very close behind at 0.71. Linear Regression was the worst at 0.55. The app uses the Random Forest.

It's only a rough estimate. The model has no idea about the car's condition, accident history or trim, so don't treat the number as a real valuation.

## How it's put together

The page in `public/index.html` is plain HTML, CSS and JavaScript. When you press the button it sends your details to a small Flask app in `api/index.py`, which loads the saved model (`api/model.joblib`) and sends back a price.

`train_model.py` is the script that cleans the data, trains the models and saves the best one.

## Running it on your own computer

```
pip install flask numpy scikit-learn joblib
python api/index.py
```

Then go to http://127.0.0.1:3000.

If you want to retrain it, put the CarDekho CSV in the folder (called `cardekho.csv` or `car data.csv`) and run:

```
pip install -r requirements-train.txt
python train_model.py
```

That replaces `api/model.joblib` and `api/meta.json`.

## Putting it on Vercel

Push the project to GitHub, then on vercel.com click Add New > Project, pick the repo and hit Deploy. You don't need to change any settings.

Make sure `model.joblib` and `meta.json` are in the repo. If they're missing the page says the model isn't available. The CSV is left out on purpose, check `.gitignore`.

One more thing: scikit-learn is pinned to 1.9.1 in both requirements files. A saved model only loads properly on the same version it was trained with, so if you change one, retrain.

Made with Python, pandas, scikit-learn, Flask and a bit of JavaScript.
