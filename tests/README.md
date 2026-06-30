# Chatbot Test Suite Guide

This directory contains utility scripts to benchmark latency, evaluate response quality, and load-test the streaming `/chat` endpoint.

---

## Prerequisite: Environment Setup

Before running the tests, ensure that:
1. The **Backend Server** is running (usually on `http://localhost:8000`).
2. You are in the project root directory `c:\Work\Projects\Chatbot`.
3. Your Python virtual environment is activated, or you run the commands using the virtual environment's python executable.

### How to activate python environment in PowerShell:
```powershell
.\chat-bot-env\Scripts\activate.ps1
```

If you don't want to activate it, you can prepend `.\chat-bot-env\Scripts\` to your python commands (as listed below).

### Install dependencies:
If dependencies are not installed, run:
```powershell
.\chat-bot-env\Scripts\python.exe -m pip install -r tests/requirements.txt
```

---

## 1. Latency Benchmarks
Measures Time to First Token (TTFT), Time Per Output Token (TPOT), and total request duration.

**Execution Command:**
```powershell
.\chat-bot-env\Scripts\python.exe tests/benchmark_latency.py
```

---

## 2. Quality & Correctness Evaluation
Evaluates the model against assertions (keyword checking, character length, compliance, and multi-turn memory) specified in the golden dataset file (`tests/eval_messages.json`).

**Execution Command:**
```powershell
.\chat-bot-env\Scripts\python.exe tests/evaluate_quality.py
```

---

## 3. Load Testing (Locust)
Simulates active concurrent users requesting stream completions to test throughput and latency degradation under load.

### Option A: Run Headlessly (Generates HTML Report File)
This runs the load test for **30 seconds** with **5 concurrent users**, and saves the result to `tests/locust_report.html`:
```powershell
.\chat-bot-env\Scripts\python.exe -m locust -f tests/locustfile.py --headless -u 5 -r 1 --run-time 30s --html tests/locust_report.html --host http://localhost:8000
```

### Option B: Run via Locust Web Interface
Start the Locust server:
```powershell
.\chat-bot-env\Scripts\python.exe -m locust -f tests/locustfile.py --host http://localhost:8000
```
Then open your web browser and navigate to:
[http://localhost:8089](http://localhost:8089)
Here, you can specify the number of users, ramp-up rate, and start/stop the load tests interactively.
