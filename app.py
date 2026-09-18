import streamlit as st
import pandas as pd
import json
from src.data_loader import TelemetryDataLoader
from src.anomaly_detector import MetricAnomalyDetector
from src.agent import IncidentResponseAgent

st.set_page_config(page_title="AI Incident Response Platform", layout="wide")

st.title("🚨 AI-Driven Incident Response Platform")
st.markdown("Real-time telemetry, anomaly detection, RAG runbooks, and FastMCP diagnostics.")

# Sidebar Controls
st.sidebar.header("Control Panel")
refresh_data = st.sidebar.button("Refresh Telemetry Data")

# Initialize Pipeline Components
@st.cache_resource
def load_agent():
    return IncidentResponseAgent()

agent = load_agent()

# Tab Layout
tab1, tab2, tab3 = st.tabs(["📊 Metric Telemetry & ML", "🔍 Log Parser & RAG Search", "🤖 Incident Agent Console"])

with tab1:
    st.subheader("System Telemetry & IsolationForest Anomalies")
    loader = TelemetryDataLoader("data/server_telemetry.csv")
    df = loader.load_and_clean()
    
    detector = MetricAnomalyDetector()
    df_analyzed = detector.fit_predict(df)
    
    # Count anomalies directly using the model's output column
    if 'is_anomaly' in df_analyzed.columns:
        anomaly_count = (df_analyzed['is_anomaly'] == 1).sum()
    elif 'anomaly' in df_analyzed.columns:
        anomaly_count = (df_analyzed['anomaly'] == -1).sum()
    else:
        anomaly_count = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Telemetry Logs", len(df_analyzed))
    col2.metric("Anomalies Detected", int(anomaly_count))
    col3.metric("Avg CPU Utilization", f"{df_analyzed['cpu_usage'].mean():.1f}%")
    
    # Telemetry Chart
    st.line_chart(df_analyzed.set_index('timestamp')[['cpu_usage', 'memory_usage']])

with tab2:
    st.subheader("Interactive Log Entity Extraction")
    user_log = st.text_area(
        "Enter Raw Server Log:",
        "ERROR [service=gateway] HTTP 500 failure from IP: 10.0.0.45 route /api/v1/checkout"
    )
    
    if st.button("Parse Log & Search RAG"):
        parsed = agent.parser.parse_log(user_log)
        st.json(parsed)
        
        search_query = f"{parsed['severity']} {parsed['failing_route']} failure"
        rag_doc = agent.vector_store.search(search_query, top_k=1)
        
        st.subheader("Matched Knowledge Base Runbook")
        st.markdown(rag_doc[0]['content'])

with tab3:
    st.subheader("Agent Diagnostic Execution")
    incident_log = st.text_input(
        "Simulate Active Incident Log:",
        "CRITICAL Connection timeout to database cluster route /api/v1/checkout"
    )
    
    if st.button("Trigger AI Incident Agent"):
        with st.spinner("Processing Incident Pipeline..."):
            report = agent.process_incident(incident_log)
            st.success("Incident Processing Complete!")
            st.json(report)