import pandas as pd

def compute_unified_risk(cyc, crime, coll, km, lr):
    def predict(df):
        df["cluster_risk"] = km.predict(df[["lat", "lon"]])
        df["time_risk"] = lr.predict_proba(df[["hour"]])[:, 1]
        df["risk_score"] = (
            df["severity"] * 0.4 +
            df["time_risk"] * 0.3 +
            df["cluster_risk"] * 0.3
        )
        return df[["lat", "lon", "risk_score"]]

    all_data = pd.concat([predict(cyc), predict(crime), predict(coll)])
    return all_data.reset_index(drop=True)
