import random
from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("ServerDiagnostics")

@mcp.tool()
def check_service_health(service_name: str) -> str:
    """Checks the live operational status of a specific microservice."""
    statuses = ["HEALTHY", "DEGRADED", "CRITICAL_OVERLOAD"]
    status = random.choice(statuses) if service_name in ["gateway", "checkout", "users"] else "UNKNOWN_SERVICE"
    return f"Service '{service_name}' status: {status} (Active Connections: {random.randint(50, 500)})"

@mcp.tool()
def restart_service(service_name: str) -> str:
    """Restarts a targeted application service container."""
    return f"SUCCESS: Service '{service_name}' container restarted successfully. Connection pool reset."

@mcp.tool()
def fetch_live_metrics(metric_type: str) -> str:
    """Fetches real-time server telemetry metrics (cpu, memory, disk)."""
    if metric_type.lower() == "cpu":
        return f"Current CPU Utilization: {random.randint(80, 99)}% (High Spike Detected)"
    elif metric_type.lower() == "memory":
        return f"Current Memory Utilization: {random.randint(60, 85)}%"
    return f"Metric '{metric_type}' normal."

if __name__ == "__main__":
    mcp.run()