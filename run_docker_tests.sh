#!/bin/bash
# Simple test runner script for Docker environments
cd /app
export PYTHONPATH=/app:$PYTHONPATH
python -m pytest tests/ -v --tb=short
