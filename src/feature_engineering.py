import pandas as pd

def preprocess_all(df_cyc, df_crime, df_coll):
    # Ensure risk column exists
    df_cyc["risk"] = df_cyc["risk"].astype(float)
    df_crime["risk"] = df_crime["risk"].astype(float)
    df_coll["risk"] = df_coll["risk"].astype(float)

    # Combine them
    df_all = pd.concat([df_cyc, df_crime, df_coll], ignore_index=True)

    # Drop weird coordinates
    df_all = df_all.dropna(subset=["lat", "lon"])

    return df_all
