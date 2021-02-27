import os
from datetime import datetime

import numpy as np
import pandas as pd
import requests


BASE_DATA_ADDRESS = "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
COLS = dict(
    death="cumDailyNsoDeathsByDeathDate",
    new_death="newDeaths28DaysByDeathDate",
    dose1="cumPeopleVaccinatedFirstDoseByPublishDate",
    dose2="cumPeopleVaccinatedSecondDoseByPublishDate",
)
FIRST_DOSE = dict(
    dose1=datetime(2020, 12, 8),
    dose2=datetime(2020, 12, 29)
)
VAC_PUBLISH = datetime(2021, 1, 10)


def download(date=None):
    if date is None:
        data_release = ""
    else:
        data_release = "&release=" + pd.Timestamp(date).strftime("Y%-%m-%d")
    data_format = "&format=csv"
    data_cols = "".join(f"&metric={col}" for col in COLS.values())
    data_address = BASE_DATA_ADDRESS + data_cols + data_format + data_release
    response = requests.get(data_address)
    filename = response.headers["Content-Disposition"].split('"')[1]
    with open(os.path.join(DATA_DIR, filename), 'wb') as f:
        f.write(response.content)


def smooth_initial_vaccine(df, dose="dose1"):
    """Vaccine figures aren't published until many weeks after first vaccinations, so exponentially smooth."""
    first = FIRST_DOSE[dose]
    num_days = (VAC_PUBLISH - first).days + 1
    smooth_data = np.logspace(0, np.log10(df.loc[VAC_PUBLISH, dose]), num=num_days)
    df.loc[first:VAC_PUBLISH, dose] = smooth_data
    return df


def merge_latest_deaths(df):
    """Use the very latest 28-days data to estimate most recent deaths."""
    week_ratio = df["new_death"].iloc[-12:-5].mean() / df["new_death"].iloc[-19:-12].mean()
    df["new_death"].iloc[-5:] = df["new_death"].iloc[-12:-7] * week_ratio  # Synthesise recent 5 days as incomplete
    prev_idx = df.index[-22]
    for idx in df.index[-21:]:
        if np.isnan(df.loc[idx, "death"]):
            df.loc[idx, "death"] = df.loc[prev_idx, "death"] + df.loc[idx, "new_death"]
        prev_idx = idx
    df = df.drop("new_death", axis=1)
    return df


def load(date=None):
    """Load raw data from disk and apply cleaning methods."""
    if date is None:
        filename = sorted(os.listdir(DATA_DIR))[-1]
    else:
        filename = f"overview_{date}.csv"
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(filepath)
    df.index = pd.to_datetime(df["date"])
    df = df.sort_index()
    df = df[COLS.values()]
    df.columns = list(COLS.keys())
    df = smooth_initial_vaccine(df, "dose1")
    df = smooth_initial_vaccine(df, "dose2")
    df = merge_latest_deaths(df)
    df = df.replace(np.nan, 0)
    df = df.astype(int)
    return df
