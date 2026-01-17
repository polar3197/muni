FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements (cached layer)
COPY ./src/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy setup.py and install package in editable mode
COPY setup.py .
COPY src/ /app/src/
RUN pip install --no-cache-dir -e .

# Python path handles imports
ENV PYTHONPATH=/app

CMD ["uvicorn", "src.api.api:app", "--host", "0.0.0.0", "--port", "8000"]
