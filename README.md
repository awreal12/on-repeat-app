An interactive dashboard for exploring your own Spotify listening history, built with Python, pandas, Plotly and Streamlit.

<!-- TODO: add a screenshot or GIF here -->

Live demo (synthetic data): add your Streamlit Community Cloud link

What it shows
Hours listened, plays, unique artists, skip rate
Top artists and tracks
Listening hours by month
A weekday × hour heatmap of when you listen
Get your data
Spotify → Account → Privacy settings → request Extended streaming history
Wait for the email (can take a few days) and download the zip
Upload the Streaming_History_Audio_*.json files in the app sidebar

Your data is processed locally and never leaves your machine. The data/ folder is gitignored, so you won't accidentally publish your listening history.

pip install -r requirements.txt
streamlit run app.py
