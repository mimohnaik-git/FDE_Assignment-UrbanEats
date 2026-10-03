# Phase-3 API runtime; saved artifact only, no runtime training.
FROM python:3.12-slim@sha256:dddfd7e07f9d15aeeca61529320492139d21cac7f0070c00609243e51e4e0016
WORKDIR /app
COPY requirements.txt pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY artifacts/model ./artifacts/model
RUN useradd --create-home runtime && mkdir -p /app/runs /app/data && chown -R runtime /app
USER runtime
ENV TZ=Asia/Kolkata URBANEATS_MODEL_DIR=/app/artifacts/model URBANEATS_RUNS_DIR=/app/runs URBANEATS_SOURCE_FILE=/app/data/current_batch.json TEST_MODE=true
EXPOSE 8000
CMD ["uvicorn", "urbaneats.service:app", "--host", "0.0.0.0", "--port", "8000"]
