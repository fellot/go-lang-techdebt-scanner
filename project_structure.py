"""
go-tech-debt-scan/
│
├── main.py                     # FastAPI application entry point
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
│
├── api/
│   ├── __init__.py
│   ├── models.py               # Pydantic models for API
│   ├── routes.py               # API routes
│   └── services.py             # Service layer for scanning
│
├── scanner/                    # Core scanning logic (reused from CLI version)
│   ├── __init__.py
│   ├── repo_scanner.py         # Repository traversal
│   ├── go_tools.py             # Go tools integration
│   └── git_analyzer.py         # Git history analysis
│
├── metrics/                    # Metric collectors (reused from CLI version)
│   ├── __init__.py
│   ├── complexity.py
│   ├── duplication.py
│   ├── test_quality.py
│   ├── dependencies.py
│   ├── churn.py
│   └── readability.py
│
└── scoring/                    # Scoring logic (reused from CLI version)
    ├── __init__.py
    ├── normalizer.py
    ├── aggregator.py
    └── thresholds.py
"""