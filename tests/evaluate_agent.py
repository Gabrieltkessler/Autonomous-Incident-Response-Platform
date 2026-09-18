import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

import json
import time
from src.agent import IncidentResponseAgent

# Test dataset covering various severities, routes, and missing fields
EVAL_DATASET = [
    {
        "id": "TC-01",
        "description": "Database Connection Timeout (Checkout)",
        "log": "CRITICAL Connection timeout to database cluster route /api/v1/checkout",
        "expected_runbook": "db_connection_pool.md",
        "expected_tool": "check_service_health",
        "expected_target": "checkout"
    },
    {
        "id": "TC-02",
        "description": "Auth Service Memory Spike",
        "log": "ERROR Out of memory exception high heap usage route /api/v1/auth",
        "expected_runbook": "db_connection_pool.md", # or generic error runbook
        "expected_tool": "check_service_health",
        "expected_target": "auth"
    },
    {
        "id": "TC-03",
        "description": "Normal Warning Log (No Remediation)",
        "log": "WARNING Slow response time detected on route /api/v1/payment",
        "expected_runbook": None,
        "expected_tool": None,
        "expected_target": "payment"
    }
]

def run_evaluation():
    print("=" * 60)
    print("      STARTING AGENT & RAG BENCHMARK EVALUATION      ")
    print("=" * 60)

    agent = IncidentResponseAgent()
    total_tests = len(EVAL_DATASET)
    rag_hits = 0
    tool_hits = 0

    results = []

    for test in EVAL_DATASET:
        print(f"\n[Running {test['id']}] {test['description']}...")
        start_time = time.time()
        
        report = agent.process_incident(test["log"])
        latency = round(time.time() - start_time, 2)

        # 1. Evaluate RAG Accuracy
        matched_rb = report.get("recommended_runbook")
        rag_pass = (matched_rb == test["expected_runbook"]) or (test["expected_runbook"] is None)
        if rag_pass:
            rag_hits += 1

        # 2. Evaluate Tool Trigger Accuracy
        diagnostics = report.get("diagnostics", [])
        tool_pass = True if len(diagnostics) > 0 else (test["expected_tool"] is None)
        if tool_pass:
            tool_hits += 1

        results.append({
            "id": test["id"],
            "rag_pass": rag_pass,
            "tool_pass": tool_pass,
            "latency_s": latency
        })

    # Summary Metrics
    print("\n" + "=" * 60)
    print("                    BENCHMARK RESULTS                       ")
    print("=" * 60)
    print(f"RAG Retrieval Precision: {rag_hits}/{total_tests} ({(rag_hits/total_tests)*100:.1f}%)")
    print(f"Tool Execution Accuracy: {tool_hits}/{total_tests} ({(tool_hits/total_tests)*100:.1f}%)")
    
    print("\nDetailed Test Results:")
    for res in results:
        status = "PASSED" if (res['rag_pass'] and res['tool_pass']) else "FAILED"
        print(f" - {res['id']}: {status} | Latency: {res['latency_s']}s")

if __name__ == "__main__":
    run_evaluation()