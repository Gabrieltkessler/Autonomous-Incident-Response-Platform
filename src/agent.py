import json
import ollama
from src.log_parser import LogEntityExtractor
from src.rag_indexer import RunbookVectorStore
from src.mcp_server import check_service_health, fetch_live_metrics, restart_service

class IncidentResponseAgent:
    """AI Agent powered by local LLM tool-calling (Ollama llama3.1)."""
    
    def __init__(self, model_name: str = "llama3.1:latest"):
        self.model_name = model_name
        self.parser = LogEntityExtractor()
        self.vector_store = RunbookVectorStore()
        self.vector_store.load_and_index_runbooks()
        
        # Registry mapping tool names to actual Python callables
        self.tool_registry = {
            "check_service_health": check_service_health,
            "fetch_live_metrics": fetch_live_metrics,
            "restart_service": restart_service
        }

    def process_incident(self, raw_log: str) -> dict:
        """Processes an incident using Ollama tool-calling."""
        print(f"\n[Step 1/3] Parsing Raw Infrastructure Log...")
        parsed_entity = self.parser.parse_log(raw_log)
        
        print("\n[Step 2/3] Querying Vector Store for Diagnostic Runbook...")
        search_query = f"{parsed_entity['severity']} {parsed_entity['failing_route']} failure"
        rag_results = self.vector_store.search(search_query, top_k=1)
        matched_runbook = rag_results[0]['source'] if rag_results else "None Found"
        runbook_content = rag_results[0]['content'] if rag_results else ""

        print(f"\n[Step 3/3] Invoking {self.model_name} with FastMCP Tools...")
        
        # System prompt providing log and runbook context
        system_prompt = (
            f"You are an automated SRE incident response agent.\n"
            f"Parsed Log Data: {json.dumps(parsed_entity)}\n"
            f"Relevant Runbook Document:\n{runbook_content}\n\n"
            f"Use the provided tools to inspect service health and remediate the issue if necessary."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Investigate and remediate this incident: {raw_log}"}
        ]

        # Available Python functions passed directly as tools
        tools = [check_service_health, fetch_live_metrics, restart_service]

        # Call Ollama LLM
        response = ollama.chat(
            model=self.model_name,
            messages=messages,
            tools=tools
        )

        executed_diagnostics = []
        action_taken = "No destructive action required."

        # Handle tool calls triggered by the LLM
        tool_calls = response.get("message", {}).get("tool_calls", [])
        if tool_calls:
            for call in tool_calls:
                func_name = call["function"]["name"]
                func_args = call["function"]["arguments"]
                
                # Normalize service name if LLM hallucinated a long string
                if "service_name" in func_args:
                    if "checkout" in func_args["service_name"].lower() or "checkout" in parsed_entity.get("failing_route", ""):
                        func_args["service_name"] = "checkout"
                    elif "database" in func_args["service_name"].lower() or "db" in func_args["service_name"].lower():
                        func_args["service_name"] = "database"
                
                if func_name in self.tool_registry:
                    print(f"  -> LLM Triggered Tool: {func_name}({func_args})")
                    result = self.tool_registry[func_name](**func_args)
                    
                    if func_name == "restart_service":
                        action_taken = result
                    else:
                        executed_diagnostics.append(result)

            # If the LLM checked health and found high overload/degradation, auto-trigger restart if LLM skipped second call
            if "checkout" in parsed_entity.get("failing_route", "") and action_taken == "No destructive action required.":
                if any("DEGRADED" in d or "HIGH" in d for d in executed_diagnostics) or parsed_entity['severity'] == "CRITICAL":
                    action_taken = restart_service("checkout")

        return {
            "parsed_log": parsed_entity,
            "recommended_runbook": matched_runbook,
            "diagnostics": executed_diagnostics,
            "action_taken": action_taken,
            "llm_reasoning": response.get("message", {}).get("content", "")
        }

if __name__ == "__main__":
    agent = IncidentResponseAgent()
    sample_log = "CRITICAL Connection timeout to database cluster route /api/v1/checkout"
    report = agent.process_incident(sample_log)
    
    print("\n==========================================")
    print("      LLM INCIDENT RESPONSE REPORT        ")
    print("==========================================")
    print(json.dumps(report, indent=2))