from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression

def build_risk_models(crime_df):
    km = KMeans(n_clusters=6, random_state=42)
    km.fit(crime_df[["lat", "lon"]])

    lr = LogisticRegression()
    lr.fit(crime_df[["hour"]], crime_df["severity"])

    return km, lr
