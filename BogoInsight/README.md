# BogoInsight

BogoInsight is a data analysis project that includes data gathering, manipulation and visualization on various topics.

This project is bulit upon Streamlit.

## File structure

- `crawlers/` data crawling scripts
- `data/` crawled data
- `database/` db related logic (unused)
- `models/` db data models (unused)
- `pages/` Streamlit pages
- `services/` db services (unused)
- `utils/` utility functions
- `app.js` Node.js proxy for Streamlit app, a workaround for publishing on cPanel
- `BogoInsight.py` entrypoint for Streamlit app
- `loader.cjs` cPanel Node.js entrypoint
- `run.sh` entrypoint for production

## Usage

Development:

```cmd
streamlit run BogoInsight.py
```

Production:

```cmd
bash run.sh
```