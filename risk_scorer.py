"""
Risk scoring module for SafeRoute AI.
Uses KMeans clustering and Logistic Regression for risk assessment.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from typing import Tuple


class RiskScorer:
    """
    Calculates risk scores for locations using machine learning models.
    """
    
    def __init__(self, n_clusters: int = 3):
        """
        Initialize the risk scorer.
        
        Args:
            n_clusters: Number of risk clusters (low, medium, high)
        """
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.logistic = LogisticRegression(random_state=42, max_iter=1000)
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def fit(self, features_df: pd.DataFrame) -> 'RiskScorer':
        """
        Fit the risk scoring models on location features.
        
        Args:
            features_df: DataFrame with location features
            
        Returns:
            Self for method chaining
        """
        # Select features for modeling
        feature_cols = ['lighting_score', 'total_incidents', 
                       'high_severity_count', 'recent_incidents']
        X = features_df[feature_cols].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit KMeans to identify risk clusters
        cluster_labels = self.kmeans.fit_predict(X_scaled)
        
        # Calculate cluster risk scores based on average incident counts
        cluster_risks = []
        for cluster_id in range(self.n_clusters):
            cluster_mask = cluster_labels == cluster_id
            avg_incidents = features_df.loc[cluster_mask, 'total_incidents'].mean()
            cluster_risks.append(avg_incidents)
        
        # Sort clusters by risk (ascending) and create mapping
        cluster_order = np.argsort(cluster_risks)
        self.cluster_to_risk = {old: new for new, old in enumerate(cluster_order)}
        
        # Create synthetic labels for logistic regression (high risk = 1, low risk = 0)
        y = np.array([self.cluster_to_risk[label] for label in cluster_labels])
        y_binary = (y >= self.n_clusters - 1).astype(int)  # Top cluster = high risk
        
        # Fit logistic regression
        self.logistic.fit(X_scaled, y_binary)
        
        self.is_fitted = True
        return self
    
    def predict_risk_scores(self, features_df: pd.DataFrame) -> np.ndarray:
        """
        Predict risk scores for locations.
        
        Args:
            features_df: DataFrame with location features
            
        Returns:
            Array of risk scores (0-1, where 1 is highest risk)
        """
        if not self.is_fitted:
            raise ValueError("RiskScorer must be fitted before prediction")
        
        # Select features
        feature_cols = ['lighting_score', 'total_incidents', 
                       'high_severity_count', 'recent_incidents']
        X = features_df[feature_cols].values
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get cluster assignments
        cluster_labels = self.kmeans.predict(X_scaled)
        cluster_risks = np.array([self.cluster_to_risk[label] for label in cluster_labels])
        
        # Get probability of high risk from logistic regression
        risk_probs = self.logistic.predict_proba(X_scaled)[:, 1]
        
        # Combine cluster-based and probability-based scores
        # Normalize cluster risks to 0-1
        normalized_cluster_risks = cluster_risks / (self.n_clusters - 1)
        
        # Weight: 60% cluster, 40% probability
        final_scores = 0.6 * normalized_cluster_risks + 0.4 * risk_probs
        
        # Adjust for lighting (darker = higher risk)
        lighting_penalty = (1 - features_df['lighting_score'].values) * 0.2
        final_scores = np.clip(final_scores + lighting_penalty, 0, 1)
        
        return final_scores
    
    def get_risk_category(self, risk_score: float) -> str:
        """
        Convert risk score to category label.
        
        Args:
            risk_score: Risk score between 0 and 1
            
        Returns:
            Risk category: 'Low', 'Medium', or 'High'
        """
        if risk_score < 0.33:
            return 'Low'
        elif risk_score < 0.67:
            return 'Medium'
        else:
            return 'High'


def calculate_edge_risk(node1_risk: float, node2_risk: float) -> float:
    """
    Calculate risk for an edge (path segment) between two nodes.
    
    Args:
        node1_risk: Risk score of first node
        node2_risk: Risk score of second node
        
    Returns:
        Edge risk score (average of node risks)
    """
    return (node1_risk + node2_risk) / 2.0
