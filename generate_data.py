import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# Generate 500 minutes of time-series data
timestamps = [datetime.now() - timedelta(minutes=i) for i in range(500)][::-1]

# Normal metrics
cpu_usage = np.random.normal(loc=30, scale=5, size=500)
memory_usage = np.random.normal(loc=45, scale=4, size=500)

# Inject synthetic spikes
cpu_usage[100:110] += np.random.uniform(45, 60, size=10)
memory_usage[100:110] += np.random.uniform(40, 50, size=10)
cpu_usage[300:308] += np.random.uniform(50, 65, size=8)

log_templates = [
    "INFO [service=auth] User authentication successful from IP: 192.168.1.10",
    "INFO [service=payment] Processed transaction ID tx_88291",
    "WARN [service=db] High query latency detected on route /api/v1/users",
    "ERROR [service=gateway] HTTP 500 failure from IP: 10.0.0.45 route /api/v1/checkout",
    "CRITICAL [service=auth] Connection timeout to database cluster"
]

log_messages = np.random.choice(log_templates, size=500, p=[0.5, 0.3, 0.1, 0.07, 0.03])

df = pd.DataFrame({
    'timestamp': timestamps,
    'cpu_usage': np.clip(cpu_usage, 0, 100),
    'memory_usage': np.clip(memory_usage, 0, 100),
    'log_message': log_messages
})

df.to_csv('data/server_telemetry.csv', index=False)
print("Saved sample dataset to data/server_telemetry.csv")