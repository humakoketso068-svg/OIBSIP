# Car Price Predictor

I wanted to see if I could predict what a used car sells for just from basic details like its age, mileage, fuel
type and brand. This project is how that went. I cleaned a real dataset, explored it, trained three models,
picked the best one, and then put it behind a small website so anyone can type in a car and get a price.

Everything is in Python (pandas, scikit-learn, matplotlib, seaborn) inside a Jupyter Notebook, and the website
is a small Flask app.

The data is the [Vehicle dataset from CarDekho](https://www.kaggle.com/datasets/nehalbirla/vehicle-dataset-from-cardekho)
from Kaggle. It has 4,340 used cars with the name, year, selling price (in rupees), kilometres driven, fuel type,
seller type, transmission and owner. It's saved in `data/cardekho.csv`.

## What's in the folder

- `car_price_prediction.ipynb` is where all the data work happens. Start here.
- `data/cardekho.csv` is the dataset.
- `model/` holds the trained model that the notebook saves at the end.
- `app.py` is the Flask app that loads the model and answers requests.
- `public/index.html` is the web page.
- `render.yaml` and `.vercelignore` are only for deploying.

## Walkthrough of what I did

The notebook follows these steps in order, and each one has its own section.

**1. Loading the data.** First I just read the CSV and looked at it. It has 8 columns and 4,340 rows.

**2. Cleaning it.** There were three things to check. There are no null values in this file, but I still wrote
the code to handle them in case the data changes. Duplicates were the big one: 763 rows were repeats, which is
about 18% of the file, and removing them left 3,577 cars. For the categories I made everything lowercase and
stripped spaces so things like "Petrol" and "petrol" can't turn into two different values. I also dropped the one
Electric car, because one example isn't enough for a model to learn from. That left 3,576 cars.

**3. Making new features.** The year column isn't very useful on its own, so I turned it into **car age**
(this year minus the year it was made). I also pulled the **brand** out of the car name by taking the first word,
and fixed a few oddities like "Maruti" (should be Maruti Suzuki) and "Land" (should be Land Rover). Brands with
fewer than 5 cars went into an "other" group.

**4. Exploring the data.** I made three charts: how the selling prices are spread out, price by fuel type, and
price against car age. The prices are heavily skewed. Half of the cars sell for between 2 and 6 lakh, but the most
expensive one is 89 lakh, so I used a log scale on some charts. Diesel cars sell for more than petrol ones, and
older cars are cheaper, although a 10 year old Maruti and a 10 year old Mercedes are obviously very different.

**5. Turning text into numbers.** Models can't use words, so I encoded the text columns. Owner has a natural
order (first, second, third...) so I used label encoding for it. Brand, fuel, seller type and transmission have no
order, so I used one-hot encoding. That gave 29 features.

**6. Checking correlations.** I plotted a heatmap of all the features against price. Manual transmission and car
age have the strongest negative link with price, and luxury brands like BMW and Mercedes have the strongest
positive link.

**7. Splitting the data.** I kept 20% of the cars aside for testing (716 cars) and trained on the rest (2,860),
so I could see how the models do on cars they haven't seen.

**8. Training the models.** I tried three, from simplest to most complex: Linear Regression, Random Forest and
Gradient Boosting.

**9. Comparing them.** I scored each one on the test cars using MAE (the average mistake in rupees), RMSE (like
MAE but big mistakes count more) and R² (how much of the price variation the model explains).

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | ₹176,244 | ₹347,469 | 0.586 |
| Random Forest | ₹145,347 | ₹319,963 | 0.649 |
| Gradient Boosting | ₹138,453 | ₹272,660 | 0.745 |

Gradient Boosting won on all three. An R² of 0.745 is decent but not amazing. On average it's off by about
₹1.4 lakh, and the dataset has no engine size, trim or condition, which would probably help.

**10. What matters most.** For the winning model I plotted the feature importances. Transmission and car age are
the biggest, followed by diesel fuel. Kilometres driven mattered less than I expected, and the number of owners
hardly mattered at all.

**11. Saving the model.** The last section saves the model and a small info file into `model/`, so the website
can use it without having to train anything.

## Trying it yourself

### Run the website on your computer

```
pip install -r requirements.txt
python app.py
```

Then open http://localhost:3000, fill in a car's details and press **Estimate price**. If `python` doesn't work
on Windows, try `py app.py`.

### Run the notebook

```
pip install -r requirements-train.txt
jupyter notebook car_price_prediction.ipynb
```

Run all the cells from the top. It takes under a minute and charts show up as it goes. If you use VS Code, pick
the Python you installed the packages into when it asks for a kernel. Running the notebook saves a fresh copy of
the model into `model/`.

## Putting it online

Put the project on GitHub first:

```
git init
git add .
git commit -m "car price predictor"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/car-price-predictor.git
git push -u origin main
```

**On Vercel:** go to vercel.com, click **Add New** then **Project**, import the repo and press **Deploy**. You
don't have to change any settings. Vercel finds `app.py` by itself and serves the page from the `public` folder.

**On Render:** go to render.com, click **New +** then **Blueprint**, pick the repo and click **Apply**. It reads
`render.yaml` for the settings. If you'd rather set it up by hand, make a Python web service with the build
command `pip install -r requirements.txt`, the start command `gunicorn app:app`, and an environment variable
`PYTHON_VERSION` set to `3.12.8`. On the free plan the site sleeps when nobody is using it, so the first visit
can take about a minute.

Two things to remember. The `model/` folder has to be pushed to GitHub, because the site can't run without it.
And the `scikit-learn` version needs to stay the same in both requirements files, since a saved model only loads
reliably on the version that made it.

## What I would do next

If I kept working on this I would try a log transform on the price since it's so skewed, tune the models properly
with cross-validation, and find a dataset with more details like engine size and trim level.
