FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app HOME=/home/census
WORKDIR /app
COPY requirements-web.txt requirements-snowflake.txt ./
RUN pip install --no-cache-dir -r requirements-web.txt \
    && useradd --uid 10001 --create-home census \
    && install -d -m 700 -o census -g census /var/lib/census
# Explicit allowlist: no development .env, Git history, tests or diagnostic evidence.
COPY census_agent ./census_agent
COPY census_catalog ./census_catalog
COPY census_web ./census_web
COPY scripts/snowflake_probe.py ./scripts/snowflake_probe.py
COPY data/semantic_catalog.json ./data/semantic_catalog.json
RUN python -c "from pathlib import Path; from census_catalog.catalog import Catalog; Catalog.prepare_index(Path('data/semantic_catalog.json'), Path('data/semantic_search_index.jsonl'))"
COPY web_app.py ./
COPY deploy/streamlit.toml ./.streamlit/config.toml
USER 10001:10001
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"
CMD ["python", "-m", "streamlit", "run", "web_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
