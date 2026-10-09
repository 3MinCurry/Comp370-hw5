import sys
from pathlib import Path

import pandas as pd
from bokeh.core.properties import value
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Select
from bokeh.plotting import figure

DEFAULT_DATA = Path.home() / "data" / "monthly_response_times.csv"
data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA

df = pd.read_csv(data_path, dtype={"zipcode": str, "month": str})
months = sorted(df["month"].unique())
series_by_zip = {
    zipcode: group.set_index("month")["avg_hours"].reindex(months)
    for zipcode, group in df.groupby("zipcode")
}

volume = (df[df["zipcode"] != "ALL"]
          .groupby("zipcode")["count"].sum()
          .sort_values(ascending=False))
zipcodes = sorted(volume.index)
default_zip1, default_zip2 = volume.index[0], volume.index[1]


def curve(zipcode):
    return {"month": months, "hours": series_by_zip[zipcode].tolist()}


all_source = ColumnDataSource(curve("ALL"))
zip1_source = ColumnDataSource(curve(default_zip1))
zip2_source = ColumnDataSource(curve(default_zip2))

zip1_select = Select(title="Zipcode 1", value=default_zip1, options=zipcodes)
zip2_select = Select(title="Zipcode 2", value=default_zip2, options=zipcodes)

plot = figure(
    x_range=months, width=950, height=450,
    title="Monthly average 311 response time (incidents created in 2024)",
    x_axis_label="Month incident was closed",
    y_axis_label="Average create-to-closed time (hours)",
    tools="pan,wheel_zoom,box_zoom,reset,save,hover",
    tooltips=[("month", "@month"), ("avg hours", "@hours{0.0}")],
)
plot.line("month", "hours", source=all_source, line_width=3, color="black",
          legend_label="All zipcodes")
plot.line("month", "hours", source=zip1_source, line_width=2, color="#1f77b4",
          legend_label=f"Zipcode 1: {default_zip1}")
plot.line("month", "hours", source=zip2_source, line_width=2, color="#d62728",
          legend_label=f"Zipcode 2: {default_zip2}")
plot.xaxis.major_label_orientation = 0.9
plot.legend.location = "top_left"
plot.legend.click_policy = "hide"


def update_zip1(attr, old, new):
    zip1_source.data = curve(new)
    plot.legend.items[1].label = value(f"Zipcode 1: {new}")


def update_zip2(attr, old, new):
    zip2_source.data = curve(new)
    plot.legend.items[2].label = value(f"Zipcode 2: {new}")


zip1_select.on_change("value", update_zip1)
zip2_select.on_change("value", update_zip2)

curdoc().add_root(column(zip1_select, zip2_select, plot))
curdoc().title = "NYC 311 response time by zipcode"
