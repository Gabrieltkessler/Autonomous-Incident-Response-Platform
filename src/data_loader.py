import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple

class TelemetryDataLoader:
    """Handles data ingestion, cleaning, and telemetry visualization."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df: pd.DataFrame = pd.DataFrame()

    def load_and_clean(self) -> pd.DataFrame:
        """Loads CSV data, formats timestamps, handles missing values, and sorts data."""
        self.df = pd.read_csv(self.filepath)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df = self.df.sort_values('timestamp').reset_index(drop=True)
        
        # Forward-fill any missing metric values to ensure clean time-series data
        self.df.ffill(inplace=True)
        return self.df

    def plot_telemetry(self, save_path: str = "data/telemetry_plot.png") -> None:
        """Generates line plots for CPU and Memory usage metrics."""
        if self.df.empty:
            raise ValueError("Dataframe is empty. Call load_and_clean() first.")
            
        sns.set_theme(style="darkgrid")
        plt.figure(figsize=(12, 5))
        
        plt.plot(self.df['timestamp'], self.df['cpu_usage'], label='CPU Usage (%)', color='#e74c3c', alpha=0.85)
        plt.plot(self.df['timestamp'], self.df['memory_usage'], label='Memory Usage (%)', color='#3498db', alpha=0.85)
        
        plt.title("System Telemetry: CPU & Memory Load Over Time", fontsize=14, pad=12)
        plt.xlabel("Timestamp", fontsize=10)
        plt.ylabel("Resource Utilization (%)", fontsize=10)
        plt.legend(loc="upper right")
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=300)
        print(f"Telemetry plot successfully saved to {save_path}")
        plt.show()

if __name__ == "__main__":
    loader = TelemetryDataLoader("data/server_telemetry.csv")
    cleaned_df = loader.load_and_clean()
    
    print("\n--- Data Pipeline Head ---")
    print(cleaned_df.head())
    print(f"\nTotal Records Ingested: {len(cleaned_df)}")
    
    loader.plot_telemetry()