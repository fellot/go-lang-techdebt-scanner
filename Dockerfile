FROM python:3.11-slim-bullseye

# Install Go and required tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    golang \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Go tools
RUN go install github.com/fzipp/gocyclo/cmd/gocyclo@latest && \
    go install github.com/uudashr/gocognit/cmd/gocognit@latest && \
    go install github.com/boyter/scc@latest && \
    go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest && \
    go install golang.org/x/lint/golint@latest

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]