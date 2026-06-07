# backend/Dockerfile
# Tells Docker how to build and run the FastAPI backend

# Start from official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer)
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn scikit-learn xgboost shap pandas numpy python-dotenv

# Copy the entire project into the container
COPY . .

# Expose port 8000 so the outside world can reach the API
EXPOSE 8000

# Command to start the API when container runs
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]