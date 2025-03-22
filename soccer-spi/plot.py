import pandas as pd
import plotly.express as px

df = pd.read_csv("data-20230101/spi_global_rankings.csv")

top_leagues = {
    "Barclays Premier League": "Premier League",
    "German Bundesliga": "Bundesliga",
    "Spanish Primera Division": "La Liga",
    "Italy Serie A": "Serie A",
    "French Ligue 1": "Ligue 1"
}

df = df[df['league'].isin(top_leagues.keys())]
df['league'] = df['league'].map(top_leagues)

fig = px.strip(df, x="league", y="spi", color="league", hover_data=["name", "league", "spi"])
trace_args = {
    "jitter": 0.6,
    "marker": {"size": 12, "line": {"width": 1, "color": "rgb(42,63,95)"}}
}
fig.for_each_trace(lambda t: t.update(trace_args))
fig.update_layout(
    title_text="<b>Club Strength Distribution in \"Top 5\" Leagues</b><br>"
               "<sup>According to fivethirtyeight.com \"Soccer Power Index\" (SPI), as of 1 Jan, 2023</sup>",
    height=600,
    width=900,
    paper_bgcolor="rgb(220,220,220)",
    plot_bgcolor="rgb(220,220,220)",
    showlegend=False
)
border_args = dict(showline=True, linewidth=1, linecolor="rgb(42,63,95)")
fig.update_yaxes(title_text="<b>SPI</b>", **border_args)
fig.update_xaxes(title_text="")
fig.add_annotation(
    text="Data visualisation by github.com/naspli",
    font={"size": 8, "color": "rgb(42,63,95)"},
    x=1.08,
    y=-0.16,
    showarrow=False,
    xanchor='right',
    xref="paper",
    yref="paper"
)

# import chart_studio.plotly as py
# py.plot(fig, filename='club-strength', auto_open=True)

fig.write_html("output-20230101/club-strength.html")
fig.show()
