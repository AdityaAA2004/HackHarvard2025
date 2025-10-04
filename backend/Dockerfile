FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Update system and install security patches
RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000


# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]