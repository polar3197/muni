FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy all application code first (including setup.py)
COPY ./ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install the package itself
RUN pip install -e .

ENV PYTHONPATH=/app

CMD ["python", "hello.py"]
