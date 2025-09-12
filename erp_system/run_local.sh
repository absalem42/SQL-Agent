#!/bin/bash
# Local development script
cd /home/mohamoha/Python/SQL-Agent/erp_system

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export PYTHONPATH="/home/mohamoha/Python/SQL-Agent/erp_system/backend"
export GOOGLE_API_KEY="$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)"

# Start Streamlit locally
streamlit run frontend/streamlit_app.py \
    --server.port 8502 \
    --server.fileWatcherType auto \
    --server.runOnSave true
