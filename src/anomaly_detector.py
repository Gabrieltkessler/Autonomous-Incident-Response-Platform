import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from src.data_loader import TelemetryDataLoader

class MetricAnomalyDetector:
    """Uses Scikit-Learn IsolationForest to detect anomalies in telemetry data."""
    
    def __init__(self, contamination: float = 0.05):
        # Contamination estimates the proportion of outliers in the dataset (5%)
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_fitted = False

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fits the IsolationForest model and tags metric anomalies."""
        df_copy = df.copy()
        features = df_copy[['cpu_usage', 'memory_usage']]
        
        # Fit model and predict (-1 for anomalies, 1 for normal data)
        predictions = self.model.fit_predict(features)
        
        # Flag anomalies (True if anomaly, False if normal)
        df_copy['is_anomaly'] = predictions == -1
        df_copy['anomaly_score'] = self.model.decision_function(features)
        
        self.is_fitted = True
        return df_copy

    def plot_anomalies(self, df: pd.DataFrame, save_path: str = "data/anomalies_plot.png") -> None:
        """Plots CPU usage over time with detected anomalies highlighted."""
        if 'is_anomaly' not in df.columns:
            raise ValueError("DataFrame must contain 'is_anomaly' column. Run fit_predict first.")

        sns.set_theme(style="darkgrid")
        plt.figure(figsize=(12, 5))
        
        # Plot normal telemetry line
        plt.plot(df['timestamp'], df['cpu_usage'], label='CPU Usage (%)', color='gray', alpha=0.6)
        
        # Scatter overlay for detected anomalies
        anomalies = df[df['is_anomaly']]
        plt.scatter(
            anomalies['timestamp'], 
            anomalies['cpu_usage'], 
            color='red', 
            label=f'Detected Anomalies (Count: {len(anomalies)})', 
            s=40, 
            zorder=5
        )
        
        plt.title("Isolation Forest Telemetry Anomaly Detection", fontsize=14, pad=12)
        plt.xlabel("Timestamp", fontsize=10)
        plt.ylabel("CPU Usage (%)", fontsize=10)
        plt.legend(loc="upper right")
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=300)
        print(f"Anomaly plot saved to {save_path}")
        plt.show()

if __name__ == "__main__":
    # Load clean data using our existing data loader
    loader = TelemetryDataLoader("data/server_telemetry.csv")
    cleaned_df = loader.load_and_clean()
    
    # Run Anomaly Detection
    detector = MetricAnomalyDetector(contamination=0.05)
    flagged_df = detector.fit_predict(cleaned_df)
    
    print("\n--- Detected Anomaly Summary ---")
    anomaly_summary = flagged_df[flagged_df['is_anomaly']][['timestamp', 'cpu_usage', 'memory_usage', 'log_message']]
    print(anomaly_summary.head(10))
    print(f"\nTotal Anomalies Flagged: {flagged_df['is_anomaly'].sum()}")
    
    detector.plot_anomalies(flagged_df)