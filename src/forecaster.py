import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from src.data_loader import TelemetryDataLoader

torch.manual_seed(42)

class CPUForecasterLSTM(nn.Module):
    """LSTM Neural Network for time-series CPU load forecasting."""
    def __init__(self, input_size: int = 1, hidden_size: int = 32, num_layers: int = 1):
        super(CPUForecasterLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

class TimeSeriesPipeline:
    """Handles dataset windowing, PyTorch model training, and forecasting."""
    def __init__(self, seq_length: int = 10):
        self.seq_length = seq_length
        self.scaler = MinMaxScaler()
        self.model = CPUForecasterLSTM()

    def create_sequences(self, data: np.ndarray):
        """Creates sliding sequence windows (past 10 steps -> predict next step)."""
        xs, ys = [], []
        for i in range(len(data) - self.seq_length):
            x = data[i:(i + self.seq_length)]
            y = data[i + self.seq_length]
            xs.append(x)
            ys.append(y)
        return torch.tensor(np.array(xs), dtype=torch.float32), torch.tensor(np.array(ys), dtype=torch.float32)

    def train_and_evaluate(self, df: pd.DataFrame, epochs: int = 50):
        """Scales data, trains the LSTM, and forecasts CPU metrics."""
        cpu_data = df['cpu_usage'].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(cpu_data)
        
        X, y = self.create_sequences(scaled_data)
        
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)

        self.model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.model(X_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()

        self.model.eval()
        with torch.no_grad():
            predictions = self.model(X_test).numpy()
            
        predictions_rescaled = self.scaler.inverse_transform(predictions)
        y_test_rescaled = self.scaler.inverse_transform(y_test.numpy())
        
        return y_test_rescaled, predictions_rescaled

    def plot_forecast(self, actual, predicted, save_path: str = "data/forecast_plot.png"):
        """Plots actual vs predicted CPU usage."""
        sns.set_theme(style="darkgrid")
        plt.figure(figsize=(12, 5))
        plt.plot(actual, label='Actual CPU Usage (%)', color='gray', alpha=0.7)
        plt.plot(predicted, label='PyTorch LSTM Forecast (%)', color='orange', linewidth=2)
        
        plt.title("PyTorch LSTM Time-Series CPU Load Forecast", fontsize=14, pad=12)
        plt.xlabel("Test Set Time Steps", fontsize=10)
        plt.ylabel("CPU Usage (%)", fontsize=10)
        plt.legend(loc="upper right")
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=300)
        print(f"Forecast plot saved to {save_path}")
        plt.show()

if __name__ == "__main__":
    loader = TelemetryDataLoader("data/server_telemetry.csv")
    df = loader.load_and_clean()
    
    pipeline = TimeSeriesPipeline(seq_length=10)
    actual, predicted = pipeline.train_and_evaluate(df, epochs=50)
    
    print("\n--- PyTorch Training Complete ---")
    print(f"Evaluated on {len(actual)} test time steps.")
    
    pipeline.plot_forecast(actual, predicted)