from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "unemployment.csv"
LOCKDOWN = pd.Timestamp("2020-03-25")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DEFAULT_REGIONS = ["Maharashtra", "Delhi", "Tamil Nadu"]

COLUMNS = {
    "Region": "region",
    "Date": "date",
    "Estimated Unemployment Rate (%)": "unemployment",
    "Estimated Employed": "employed",
    "Estimated Labour Participation Rate (%)": "participation",
}


def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns=COLUMNS)[list(COLUMNS.values())]
    df["region"] = df["region"].str.strip()
    df["date"] = pd.to_datetime(df["date"].str.strip(), format="%d-%m-%Y")
    df = df[df["region"].str.lower() != "india"]
    df = df.dropna(subset=["unemployment"])
    df["period"] = df["date"].dt.to_period("M")
    return df.sort_values(["region", "date"]).reset_index(drop=True)


DF = load_data()
PERIODS = sorted(DF["period"].unique())


def num(value, digits=2):
    if value is None or pd.isna(value):
        return None
    return round(float(value), digits)


def nums(values, digits=2):
    return [num(v, digits) for v in values]


def short_label(period):
    return f"{MONTHS[period.month - 1]} {str(period.year)[2:]}"


def long_label(period):
    return f"{MONTHS[period.month - 1]} {period.year}"


def region_means():
    return DF.groupby("region")["unemployment"].mean().sort_values(ascending=False)


def overview():
    monthly = DF.groupby("period")[["unemployment", "participation"]].mean().reindex(PERIODS)
    before = DF[DF["date"] < LOCKDOWN]["unemployment"].mean()
    after = DF[DF["date"] >= LOCKDOWN]["unemployment"].mean()
    peak_period = monthly["unemployment"].idxmax()
    lock_index = next(i for i, p in enumerate(PERIODS) if p.to_timestamp() >= LOCKDOWN.replace(day=1))
    n_regions = DF["region"].nunique()
    first, last = long_label(PERIODS[0]), long_label(PERIODS[-1])
    lede = (
        f"Between {first} and {last}, the average unemployment rate across {n_regions} states "
        f"went from {before:.1f}% before the lockdown to {after:.1f}% after it. "
        f"The worst month was {long_label(peak_period)}, at {monthly['unemployment'].max():.1f}%."
    )
    return {
        "labels": [short_label(p) for p in PERIODS],
        "unemployment": nums(monthly["unemployment"]),
        "participation": nums(monthly["participation"]),
        "lock_index": lock_index,
        "lede": lede,
        "stats": {
            "before": num(before, 1),
            "after": num(after, 1),
            "peak": num(monthly["unemployment"].max(), 1),
            "peak_label": long_label(peak_period),
        },
    }


def compare(regions):
    known = [r for r in regions if r in set(DF["region"])]
    datasets = []
    for name in known:
        sub = DF[DF["region"] == name].groupby("period")["unemployment"].mean().reindex(PERIODS)
        datasets.append({"region": name, "values": nums(sub)})
    if known:
        peaks = DF[DF["region"].isin(known)].groupby("region")["unemployment"].max()
        top = peaks.idxmax()
        note = f"Of the states you picked, {top} gets the highest, peaking at {peaks.max():.1f}%."
    else:
        note = "Pick at least one state to see its line."
    return {"datasets": datasets, "note": note}


def top_regions(n=10):
    means = region_means()
    head = means.head(n)
    overall = DF["unemployment"].mean()
    note = (
        f"{head.index[0]} comes out on top at {head.iloc[0]:.1f}% on average. "
        f"For comparison, the average across every state and month is {overall:.1f}%."
    )
    return {"labels": list(head.index), "values": nums(head), "note": note}


def correlation():
    cols = [("unemployment", "Unemployment rate"), ("employed", "Employed"), ("participation", "Labour participation")]
    matrix = DF[[c for c, _ in cols]].corr()
    value = matrix.loc["unemployment", "participation"]
    strength = "weak" if abs(value) < 0.3 else "moderate" if abs(value) < 0.6 else "strong"
    note = (
        f"Unemployment and labour participation have a correlation of {value:.2f}, which is a {strength} link. "
        "Even a strong correlation wouldn't tell us that one causes the other."
    )
    return {
        "labels": [label for _, label in cols],
        "matrix": [[num(matrix.loc[a, b]) for b, _ in cols] for a, _ in cols],
        "note": note,
    }


def calendar_months():
    month = DF["date"].dt.month
    all_years = DF.groupby(month)["unemployment"].mean().reindex(range(1, 13))
    without_2020 = DF[DF["date"].dt.year != 2020].groupby(month[DF["date"].dt.year != 2020])["unemployment"].mean().reindex(range(1, 13))
    hi = int(all_years.idxmax())
    note = (
        f"{MONTHS[hi - 1]} looks highest at {all_years[hi]:.1f}%, but without 2020 it drops to {without_2020[hi]:.1f}%. "
        "So the bump comes from the lockdown, not from a seasonal pattern."
    )
    return {
        "labels": MONTHS,
        "all_years": nums(all_years),
        "without_2020": nums(without_2020),
        "note": note,
    }


def before_after(n=10):
    before = DF[DF["date"] < LOCKDOWN].groupby("region")["unemployment"].mean()
    after = DF[DF["date"] >= LOCKDOWN].groupby("region")["unemployment"].mean()
    table = pd.DataFrame({"before": before, "after": after}).dropna()
    table["change"] = table["after"] - table["before"]
    head = table.sort_values("change", ascending=False).head(n)
    first = head.index[0]
    note = (
        f"{first} had the biggest jump, going from {head.loc[first, 'before']:.1f}% to {head.loc[first, 'after']:.1f}%. "
        "The after period runs through the recovery, so these averages play down how bad April and May 2020 were."
    )
    return {
        "labels": list(head.index),
        "before": nums(head["before"]),
        "after": nums(head["after"]),
        "note": note,
    }


def dashboard():
    means = region_means()
    defaults = [r for r in DEFAULT_REGIONS if r in means.index] or list(means.index[:3])
    return {
        "overview": overview(),
        "regions": list(means.index),
        "defaults": defaults,
        "compare": compare(defaults),
        "top": top_regions(),
        "correlation": correlation(),
        "calendar": calendar_months(),
        "before_after": before_after(),
        "source": f"{len(DF):,} monthly records for {DF['region'].nunique()} states",
    }
