# Unemployment in India, 2016 to 2021

This project looks at how unemployment in India changed over time and between states, and how much COVID-19 affected it. It has two parts:

1. a **Jupyter notebook** with the full analysis (this is the main part)
2. a small **dashboard** (`index.html`) that shows the same results as interactive charts

## What's in this folder

```
unemployment-analysis/
├── notebook/
│   └── unemployment_analysis.ipynb   <- the analysis
├── data/
│   └── unemployment.csv              <- the data I used
├── screenshots/                      <- pictures of the dashboard (used below)
├── index.html                        <- the dashboard
└── README.md
```

## The data

It comes from the Kaggle dataset **"Unemployment in India"**. I used the monthly "Total" file (`Unemployment_Rate_M_Total.txt`), which has one row per state per month from **January 2016 to August 2021**.

Columns: region, date, estimated unemployment rate (%), estimated number employed, and estimated labour participation rate (%).

A few things I did to it:

- The original file has a title line above the column names, so I removed that and saved a tidy copy as `data/unemployment.csv`.
- The file also contains rows for "India" as a whole. I kept those out of the state averages so the country total isn't counted as if it were another state. That leaves **27 states**.
- Some states don't have every month. Sikkim has 33 months, Meghalaya 44 and Tripura 47 (the others have 67 or 68). Keep that in mind when comparing them.

## How to run the notebook

1. Make sure you have Python 3, then install the packages:
   ```
   pip install pandas matplotlib seaborn jupyter
   ```
2. Open the notebook:
   ```
   jupyter notebook notebook/unemployment_analysis.ipynb
   ```
3. Run all the cells from the top. It finds `data/unemployment.csv` by itself.

The notebook already has its results saved, so you can also just read it on GitHub without running anything.

**What's in the notebook**

1. Loading the data, checking its shape and missing values, and fixing the types
2. Averages by state, the monthly trend, and averages by calendar month
3. Line chart of unemployment over time for a few states
4. Bar chart of the 10 states with the highest average unemployment
5. Heatmap of how unemployment, employment and labour participation relate
6. Before vs after the lockdown (split at 25 March 2020)
7. Conclusions

Every chart has a short note under it explaining what it shows.

## How to open the dashboard

The data is built into `index.html`, so there's nothing to upload or set up.

- **On your computer:** double-click `index.html`. It needs an internet connection because the chart library is loaded online.
- **Online:** put the folder on GitHub, then go to vercel.com/new, import the repo, choose the "Other" preset and leave the build command empty. If the project is inside a subfolder of a bigger repo, set the Root Directory to that folder.

## What the dashboard shows

**Overview.** The average unemployment rate across states by month, with the lockdown marked. The yellow line is unemployment, the teal line is labour participation. Both stay fairly steady for years, then unemployment jumps and participation drops at the same time in spring 2020.

![Overview](screenshots/1-overview.png)

**Compare states.** Click any states to compare them. Here Maharashtra, Delhi and Tamil Nadu are selected. They all spike after the lockdown, but by very different amounts: Tamil Nadu reaches 49.8%, while Maharashtra only reaches about 21%. Delhi and Tamil Nadu also have a second jump around May 2021.

![Compare states](screenshots/2-compare-states.png)

**Top 10 states and the heatmap.** On the left, the states with the highest average unemployment (Tripura, Haryana and Jammu & Kashmir are at the top). On the right, how the three measures relate. The numbers are all close to zero, so there is no strong link between them in this data.

![Top 10 and heatmap](screenshots/3-top10-and-heatmap.png)

**By calendar month.** All Januaries together, all Februaries, and so on. April and May look high, but the grey bars (which leave out 2020) are much lower. So the bump is from the lockdown, not a seasonal pattern.

![Calendar month](screenshots/4-calendar-month.png)

**Before vs after the lockdown.** The 10 states where the average went up the most. Haryana is the biggest jump (15.1% before, 28.5% after).

![Before vs after](screenshots/5-before-vs-after.png)

*The screenshots were taken from an earlier version of the dashboard, so some headings are worded slightly differently from the current page. The charts and numbers are the same.*

## What I found

- Before 2020, unemployment averaged about **7.4%** across states.
- After the lockdown it jumped to **22.2% in April and 23.2% in May 2020**, then fell back to about 11% by June.
- There was a smaller rise in May 2021 (13.8%), probably the second COVID wave.
- States were hit very differently. Tamil Nadu, Bihar and Delhi went over 40% for a month.
- The states with the highest averages overall (Tripura, Haryana, Jammu & Kashmir) are not exactly the ones that rose the most after the lockdown (Haryana, Puducherry, Rajasthan).
- Averaged over the whole "after" period, unemployment only went from 7.4% to 10.8%. That looks small next to the monthly chart because the "after" period runs to August 2021 and includes the recovery.

## Things to keep in mind

- State averages are **not weighted by population**, so a small state counts as much as a big one.
- Some states are missing months (see the data section).
- The "after lockdown" period mixes the worst months with the recovery, so a simple before/after average understates how bad April and May 2020 were.
- Correlation only shows that things move together, not that one causes the other.

## Tools

Python, pandas, matplotlib, seaborn and Jupyter for the analysis. The dashboard uses plain HTML, JavaScript and Chart.js.
