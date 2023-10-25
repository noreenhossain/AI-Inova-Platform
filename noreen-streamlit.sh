#!/bin/bash
source /home/noreen.hossain@cerevel.com/AI-Inova-Platform/env39/bin/activate
export XDG_SESSION_TYPE=x11
set DISPLAY=:0
streamlit run gpt_streamlit.py --server.address 0.0.0.0 --server.port 8765