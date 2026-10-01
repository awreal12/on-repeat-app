# Data

"""Loading and cleaning Spotify streaming history."""
import json
import numpy as np
import pandas as pd

# Extended history uses the first set of names, the basic account-data export uses the second.
COLUMN_MAP = {
    "ts": "played_at",
    "endTime": "played_at",
    "ms_played": "ms_played",
    "msPlayed": "ms_played",
    "master_metadata_track_name": "track",
    "trackName": "track",
    "master_metadata_album_artist_name": "artist",
    "artistName": "artist",
    "master_metadata_album_album_name": "album",
    "skipped": "skipped",
}


def normalize(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records).rename(columns=COLUMN_MAP)
    df = df.loc[:, ~df.columns.duplicated()]
    for col in ("played_at", "ms_played", "track", "artist"):
        if col not in df.columns:
            raise ValueError(f"Couldn't find a '{col}' field. Is this a Spotify streaming history file?")
    df = df.dropna(subset=["track", "artist"])  # podcasts/videos have no track name
    df["played_at"] = pd.to_datetime(df["played_at"], utc=True, errors="coerce")
    df = df.dropna(subset=["played_at"])
    df["played_at"] = df["played_at"].dt.tz_localize(None)
    df["minutes"] = df["ms_played"] / 60000
    if "skipped" not in df.columns:
        df["skipped"] = df["ms_played"] < 30_000  # fall back to "under 30s"
    df["skipped"] = df["skipped"].fillna(df["ms_played"] < 30_000).astype(bool)
    df["year"] = df["played_at"].dt.year
    df["month"] = df["played_at"].dt.to_period("M").dt.to_timestamp()
    df["hour"] = df["played_at"].dt.hour
    df["weekday"] = df["played_at"].dt.day_name()
    return df.sort_values("played_at").reset_index(drop=True)


def load_json_files(files) -> pd.DataFrame:
    """`files` is a list of file-like objects (e.g. Streamlit uploads)."""
    records = []
    for f in files:
        records.extend(json.load(f))
    return normalize(records)


def demo_data(n: int = 20000, seed: int = 7) -> pd.DataFrame:
    """Synthetic listening history so the dashboard can be demoed without personal data."""
    rng = np.random.default_rng(seed)
    artists = {
        "Neon Harbor": ["Glass Skyline", "Afterglow", "Midnight Drive"],
        "The Paper Kites Club": ["Warm Static", "Porch Light", "Slow Boats"],
        "DJ Cobalt": ["Pulse", "Gridlock", "Overdrive", "Lowtide"],
        "Maple & Rye": ["Hometown", "Cold Coffee"],
        "Atlas Bloom": ["Orbit", "Tidal", "Northbound"],
        "Velvet Echo": ["Satin", "Ghost Notes"],
    }
    weights = np.array([0.30, 0.22, 0.18, 0.12, 0.10, 0.08])
    names = list(artists)
    start = pd.Timestamp("2023-01-01").value // 10**9
    end = pd.Timestamp("2025-12-31").value // 10**9
    ts = pd.to_datetime(rng.integers(start, end, n), unit="s")
    # Bias listening toward evenings and commute hours
    hours = rng.choice(24, n, p=_hour_probs())
    ts = ts.normalize() + pd.to_timedelta(hours, unit="h") + pd.to_timedelta(rng.integers(0, 3600, n), unit="s")
    picked = rng.choice(len(names), n, p=weights)
    artist = [names[i] for i in picked]
    track = [rng.choice(artists[a]) for a in artist]
    skipped = rng.random(n) < 0.22
    ms = np.where(skipped, rng.integers(2_000, 29_000, n), rng.integers(150_000, 260_000, n))
    records = [
        {"ts": t.isoformat(), "ms_played": int(m), "master_metadata_track_name": tr,
         "master_metadata_album_artist_name": ar, "skipped": bool(s)}
        for t, m, tr, ar, s in zip(ts, ms, track, artist, skipped)
    ]
    return normalize(records)


def _hour_probs() -> np.ndarray:
    p = np.array([2, 1, 1, 1, 1, 2, 4, 7, 8, 5, 4, 4, 5, 5, 5, 5, 6, 8, 9, 10, 10, 9, 6, 4], dtype=float)
    return p / p.sum()