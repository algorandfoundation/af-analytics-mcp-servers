# Algorand Foundation Analytics - Multi-Container Platform (MCP) Servers

This repository hosts the **Model Context Platform (MCP)** servers utilized by the Algorand Foundation (AF) Business Intelligence (BI) team. These servers are essential for automating the data retrieval and processing required to generate our routine weekly and monthly reports.

---

## 💻 Server Descriptions and Responsibilities

This repository contains two primary server scripts, each responsible for specific reporting cycles:

| Server File | Analyst Name | Report Cycle | Description |
| :--- | :--- | :--- | :--- |
| `algo_insights_server.py` | **Paul** (Designated Lead) | **Monthly Reports** | Handles the more complex, deep-dive analytics required for the comprehensive monthly reports. |
| `weekly_kpis_server.py` | **Maria** (Designated Lead) | **Weekly KPIs** | Focuses on fast, reliable generation of key performance indicators for weekly reporting. |

---

## Getting Started

To successfully run and deploy these MCP servers, you must complete the following configuration steps:

### 1. Claude Desktop Setup

These servers are designed to be run within the **Claude Desktop** environment. Ensure you have the application installed and accessible.

### 2. Configuration Files

You must configure two key files to link the servers to the necessary paths and data sources:

* **`config.json`**
    * **Action:** Create this file in the root directory.
    * **Reference:** Use `config-example.json` as a guide.
    * **Purpose:** Configure local **file paths** and other application-specific settings required by the Claude environment. **Ensure all paths are correct for your local machine.**
* **`.env` File**
    * **Action:** Create this file in the root directory.
    * **Reference:** Use `.env-example` as a guide.
    * **Purpose:** Securely store **credentials and environment variables** (e.g., database connection strings, API keys) needed for the servers to access various data sources.

---

## 📂 Repository Structure

The repository is organized logically to separate concerns:

* **`docs/`**
    * **Purpose:** Stores specific configuration details for each MCP server's use case.
    * **Key Files:** Within subdirectories, you will find a file named **`queries.yaml`**. This file contains **predefined SQL queries** for report generation, along with a brief description and specific **variables** (like dates or IDs) that are dynamically updated at runtime.
* **`tools/`**
    * **Purpose:** Contains the independent Python modules (tools) that the MCP servers utilize. These are the **actionable functions** the server calls to fulfill a prompt (e.g., `execute_sql.py`, `generate_chart.py`).
* **`utils/`**
    * **Purpose:** A library of **common, reusable functions** (e.g., date parsing, database connection handlers) that are shared across both `algo_insights_server.py` and `weekly_kpis_server.py`.