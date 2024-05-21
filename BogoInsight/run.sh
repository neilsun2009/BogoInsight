conda activate bogo
nohup \
streamlit run BogoInsight.py \
--server.headless true \
--server.address 0.0.0.0 \
--server.port 8501 \
> output.log 2>&1 &