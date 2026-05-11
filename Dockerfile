FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY data ./data
COPY streamlit_app.py ./

RUN pip install --no-cache-dir streamlit -e '.[dev,sqlite]'
RUN mkdir -p outputs reports

CMD ["python", "-m", "langgraph_agent_lab.cli", "run-scenarios", "--config", "configs/lab.yaml", "--output", "outputs/metrics.json"]
