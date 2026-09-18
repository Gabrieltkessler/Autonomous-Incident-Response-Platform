# Runbook: High CPU Latency & Resource Spikes

## Incident Symptoms
- Resource Metric: CPU usage exceeds 85%
- Services Affected: /api/v1/users
- Typical Log Message: "WARN High query latency detected"

## Root Cause
Unindexed database queries or runaway background jobs consuming compute resources.

## Mitigation Steps
1. Identify high-CPU processes using `top` or process monitoring.
2. Kill rogue background threads.
3. Verify database query indexes are active.