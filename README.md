# Go Technical Debt Scanner API

A FastAPI service that analyzes Go repositories for technical debt and provides a comprehensive JSON report.

## Features

- Analyzes multiple types of technical debt in Go repositories
- Returns normalized debt scores (0-100) for each category
- Provides detailed metrics and recommendations
- RESTful API for easy integration with other tools

## Installation

### Prerequisites

- Python 3.8+
- Go 1.16+
- Required Go tools:
  - gocyclo
  - gocognit
  - scc
  - golangci-lint
  - golint
  - git

### Using Docker

```bash
docker build -t go-tech-debt-api .
docker run -p 8000:8000 go-tech-debt-api