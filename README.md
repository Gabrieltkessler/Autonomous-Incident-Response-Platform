# 🚨 AI-Driven Incident Response Platform

An autonomous, full-stack monitoring and remediation system built with Python, Streamlit, FAISS, SpaCy, FastMCP, and local LLMs via Ollama. Fully containerized with Docker & Docker Compose.

---

## 📌 Project Overview

Modern cloud infrastructure generates thousands of raw telemetry logs per minute, leading to alert fatigue and delayed incident resolution. This platform automates the end-to-end incident lifecycle:
1. **Ingests & Parses** multi-service server telemetry logs.
2. **Detects Anomalies** using machine learning algorithms to isolate high-severity metric spikes.
3. **Retrieves Runbooks (RAG)** using FAISS vector indexing to pull relevant incident mitigation protocols.
4. **Executes Diagnostics & Fixes** via FastMCP tool-calling backed by a local `llama3.1` model.
5. **Serves an Interactive Dashboard** built on Streamlit for real-time operator visibility.

---

## 🏗️ Architecture & Pipeline

[ Telemetry Logs ] ──> [ SpaCy Log Parser ] ──> [ ML Anomaly Detector ]
│
▼
[ FastMCP Tools ] <── [ Ollama (Llama 3.1) ] <── [ FAISS Vector Store ]

---

## 🛠️ Tech Stack

* **Language & Frameworks:** Python 3.10, Streamlit
* **AI & NLP:** Ollama (`llama3.1`), SpaCy (`en_core_web_sm`), FAISS Vector Database
* **Agentic Tools:** Model Context Protocol (FastMCP)
* **DevOps & Infrastructure:** Docker, Docker Compose, PowerShell

---

## 🚀 Quickstart (Docker Deployment)

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* [Git](https://git-scm.com/) installed.

### Installation & Run

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/Gabrieltkessler/ai-incident-response-platform.git](https://github.com/Gabrieltkessler/ai-incident-response-platform.git)
   cd ai-incident-response-platform

Launch via Docker Compose:

Bash
docker-compose up --build -d

Access the Dashboard:
Open your browser and navigate to http://localhost:8501.

Evaluation & Testing:
python -m pytest tests/