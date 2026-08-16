FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
# xgboost's wheel unconditionally depends on nvidia-nccl-cu12 (~340MB,
# multi-GPU support) even though this backend only calls .predict() on a
# pre-trained CPU model. Installed with --no-deps to skip that download
# entirely; numpy/scipy (its actual runtime needs) come from the other
# packages below.
RUN grep -v '^xgboost' requirements.txt > requirements.no-xgb.txt \
    && pip install --no-cache-dir --default-timeout=180 -r requirements.no-xgb.txt \
    && pip install --no-cache-dir --default-timeout=180 --no-deps xgboost==2.1.1

COPY backend/app ./app
COPY ml/artifacts ./ml/artifacts
COPY data/processed ./data/processed

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
