# Runbook: Database Connection Pool Exhaustion

## Incident Symptoms
- HTTP Status Code: 500
- Services Affected: /api/v1/checkout, /api/v1/users
- Typical Log Message: "CRITICAL Connection timeout to database cluster"

## Root Cause
High transaction volume causes active API workers to exhaust available database pool connections.

## Mitigation Steps
1. Scale the maximum connection pool limit in application configuration.
2. Restart application gateway service: `systemctl restart gateway`.
3. Flush dormant active sessions using management CLI.