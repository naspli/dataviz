import os
from datetime import timedelta

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


# TODO: add "estimate of those who will die due to existing infection"
# TODO: add "estimate of those who will avoid infection in worst case due to herd immunity"
# TODO: include dose2 in calculations, currently pretty irrelevant


SAVE_DIR = os.path.join(os.path.dirname(__file__), "saved")

# source: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/951928/
#           uk-covid-19-vaccines-delivery-plan-final.pdf
# manually intrapolated "very high" and "med high" categories from "high" for smoothness as this data is very
# sparse and the reality is on your 70th birthday your risk of death doesn't 8-tuple
PRIORITY = pd.DataFrame(
    [
        [5000000, 0.55],
        [5000000, 0.22],
        [5000000, 0.11],
        [17000000, 0.11],
        [21000000, 0.01]
    ],
    index=["very high", "high", "med high", "medium", "low"],
    columns=["population", "death_ratio"]
)
TOTAL_POPULATION = 67000000

# source: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/961287/
#           Greenbook_chapter_14a_v7_12Feb2021.pdf
DEATH_RATE = 0.009

# source: https://www.gov.uk/government/publications/covid-19-vaccination-uptake-plan/uk-covid-19-vaccine-uptake-plan
VACCINE_UPTAKE = 0.9

# source: forgotten where I saw these, this is efficacy for DEATHS not against infection, which is much lower
REDUCTION_RATE = {
    "dose1": 0.95,
    "dose2": 0.985
}
EFFECTIVE_DAYS = 14


def process(df):
    """Process the death and vaccine data with statistics to generate at-risk population and immunity time-series"""
    total_mortality_risk = int(TOTAL_POPULATION * DEATH_RATE)
    df["at_risk"] = total_mortality_risk - df["death"]
    df["immune"] = 0
    dose1_eff = np.flip(np.linspace(0, REDUCTION_RATE["dose1"], EFFECTIVE_DAYS, endpoint=False))
    min_vaccines = 0
    for priority in PRIORITY.index:
        max_vaccines = int(VACCINE_UPTAKE * PRIORITY.loc[priority, "population"]) + min_vaccines
        dose1 = df["dose1"].clip(lower=min_vaccines, upper=max_vaccines) - min_vaccines
        immune = dose1.shift(EFFECTIVE_DAYS)
        immune += dose1.diff().rolling(EFFECTIVE_DAYS, min_periods=EFFECTIVE_DAYS).apply(lambda x: np.sum(x * dose1_eff))
        immune = immune.replace(np.nan, 0)
        immunity_rate = immune / PRIORITY.loc[priority, "population"]
        at_risk = (df["at_risk"] * PRIORITY.loc[priority, "death_ratio"]).astype(int)
        df["immune"] += (at_risk * immunity_rate).astype(int)
        min_vaccines = max_vaccines
    df["at_risk"] -= df["immune"]
    df = df.drop(["dose1", "dose2"], axis=1)
    return df


def plot(df):
    fig = plt.figure(figsize=(14, 9), dpi=100, tight_layout=True)
    immune_label = f"Estimated Reduction In Maximum Deaths Due To Vaccination [@ Mortality Efficacy {int(100*REDUCTION_RATE['dose1'])}%]"
    at_risk_label = f"Estimated Maximum Deaths At Full Population Exposure [@ Average Mortality Rate {100*DEATH_RATE:.3g}%, Demographically Adjusted]"
    ax = fig.add_subplot(111)
    ts = df.index.to_pydatetime()
    ax.bar(ts, df["immune"], bottom=df["death"]+df["at_risk"], width=1.0, color="tab:cyan", alpha=0.7, label=immune_label)
    ax.bar(ts, df["at_risk"], bottom=df["death"], width=1.0, color="tab:orange", alpha=0.7, label=at_risk_label)
    ax.bar(ts, df["death"], width=1.0, color="tab:red", alpha=0.7, label="Actual Cumulative Deaths")
    ax.set_title("Coronavirus (COVID-19) in the UK: Actual Deaths vs Maximum Possible Deaths vs Reduction Due To Vaccination")
    ax.set_ylabel("# Deaths")
    ax.grid(True)
    ax.autoscale(enable=True, tight=True)
    ax.legend(loc="upper left")
    latest_date = (ts[-1] + timedelta(days=1)).strftime("%Y-%m-%d")
    credit_text = f"Raw Data Source: coronavirus.gov.uk as of {latest_date}. Source Code: github.com/Meta95/dataviz. This is a work in progress and some values are estimated or inferred."
    fig.text(0.5, 0.002, credit_text, ha='center', va="bottom", fontdict=dict(size=8, style='italic', color='grey'))
    fig.savefig(os.path.join(SAVE_DIR, f"plot_{latest_date}.png"))