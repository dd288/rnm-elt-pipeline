# Helper functions for data transformations
import pandas as pd
from datetime import timedelta
import pandas as pd

# Helper functions for data transformations
# Helper functions for data transformations
def getID(location_str):
    try:
        if isinstance(location_str, str) and '/' in location_str:
            return int(location_str.split('/')[-1].replace("'}", "").strip())
        return ""
    except ValueError:
        return "error"



def dateTimeFormat(date_str):
    return pd.to_datetime(date_str).strftime('%Y-%m-%d %H:%M:%S')

# Silver transformations
# Silver transformations
def silver_characters(df):
    df = (
        df.drop(columns=["episode", "url"])
        .assign(
            origin=df.origin.apply(lambda loc: getID({} if loc == 'unknown' else loc)),
            location=df.location.apply(lambda loc: getID({} if loc == 'unknown' else loc))
        )
        .assign(created=df.created.apply(lambda dt: dateTimeFormat(dt)))
        .rename(columns={"origin": "origin_id", "location": "location_id"})
    )
    return df

def silver_locations(df):
    df =(
        df.drop(columns=["residents", "url"])
        .assign(created=df.created.apply(lambda _df: dateTimeFormat(_df)))
    )
    return df

def silver_episodes(df):
    df = (
        df.drop(columns=["url"])
        .assign(air_date=df.air_date.apply(lambda _df: dateTimeFormat(_df)))
        .assign(created=df.created.apply(lambda _df: dateTimeFormat(_df)))
    )
    return df
