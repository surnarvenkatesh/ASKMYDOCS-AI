"""
Root conftest for the backend test suite.

Ensures tests never accidentally hit a real external LLM/embedding
provider by forcing safe local defaults unless explicitly overridden.
"""
import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("LLM_PROVIDER", "ollama")
