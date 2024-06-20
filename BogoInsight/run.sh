#!/bin/bash
if ! pgrep -f BogoInsight.py > /dev/null
then
	cd "$(dirname "$0")"
	nohup \
	/home/$(whoami)/miniconda3/envs/bogo/bin/python /home/$(whoami)/miniconda3/envs/bogo/bin/streamlit run BogoInsight.py	\
	--server.headless true \
	--server.address 0.0.0.0 \
	--server.port 8501 \
	--browser.gatherUsageStats false \
	> output.log 2>&1 &
fi
