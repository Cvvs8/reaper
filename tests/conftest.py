"""
Test configuration for pytest
"""
import sys
import os
import pytest

# Add the parent directory to the Python path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app


@pytest.fixture
def app():
    """Create app instance for testing"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()
