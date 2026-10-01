# on-repeat
# app

import pandas as pd
import plotly.express as px
import streamlit as st

from data import demo_data, load_json_files

st.set_page_config(page_title="My Spotify Wrapped, Any Time", page_icon="🎧", layout="wide")

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
GREEN = "#1db954"

st.title("🎧 My Listening History")

with st.sidebar:
    st.header("Data")
    uploads = st.file_uploader(
        "Upload your Streaming_History_Audio_*.json files", type="json", accept_multiple_files=True
    )
    use_demo = st.toggle("Use demo data", value=not uploads)

try:
    if uploads and not use_demo:
        df = load_json_files(uploads)
    else:
        df = demo_data()
        st.info("Showing synthetic demo data. Upload your own files in the sidebar to see yours.")
except Exception as e:
    st.error(f"Couldn't read that data: {e}")
    st.stop()

if df.empty:
    st.warning("No music plays found in that data.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    years = sorted(df["year"].unique())
    chosen_years = st.multiselect("Years", years, default=years)
    hide_skips = st.checkbox("Hide skipped tracks", value=False)

view = df[df["year"].isin(chosen_years)]
if hide_skips:
    view = view[~view["skipped"]]

# Headline numbers
c1, c2, c3, c4 = st.columns(4)
c1.metric("Hours listened", f"{view['minutes'].sum() / 60:,.0f}")
c2.metric("Plays", f"{len(view):,}")
c3.metric("Unique artists", f"{view['artist'].nunique():,}")
c4.metric("Skip rate", f"{df.loc[df['year'].isin(chosen_years), 'skipped'].mean():.0%}")

left, right = st.columns(2)

with left:
    st.subheader("Top artists")
    top_artists = view.groupby("artist")["minutes"].sum().nlargest(10).div(60).reset_index()
    fig = px.bar(top_artists, x="minutes", y="artist", orientation="h",
                 labels={"minutes": "Hours", "artist": ""}, color_discrete_sequence=[GREEN])
    fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Top tracks")
    top_tracks = (view.groupby(["track", "artist"]).size().nlargest(10).reset_index(name="plays"))
    top_tracks["label"] = top_tracks["track"] + " · " + top_tracks["artist"]
    fig = px.bar(top_tracks, x="plays", y="label", orientation="h",
                 labels={"plays": "Plays", "label": ""}, color_discrete_sequence=[GREEN])
    fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Listening over time")
monthly = view.groupby("month")["minutes"].sum().div(60).reset_index()
fig = px.area(monthly, x="month", y="minutes", labels={"month": "", "minutes": "Hours"},
              color_discrete_sequence=[GREEN])
fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig, use_container_width=True)

st.subheader("When you listen")
heat = (view.groupby(["weekday", "hour"])["minutes"].sum().div(60)
        .unstack("hour").reindex(WEEKDAYS).fillna(0))
fig = px.imshow(heat, aspect="auto", color_continuous_scale="Greens",
                labels={"x": "Hour of day", "y": "", "color": "Hours"})
fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig, use_container_width=True)