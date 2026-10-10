import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine

from app.config import Settings


@pytest.mark.parametrize("prefix", ["postgres://", "postgresql://", "postgresql+psycopg://"])
def test_provider_database_urls_use_installed_driver(prefix):
    suffix = "test_user:test%40password@db.example.com:5432/opportunityos?sslmode=require"
    settings = Settings(_env_file=None, DATABASE_URL=prefix + suffix)
    assert settings.DATABASE_URL == "postgresql+psycopg://" + suffix
    engine = create_engine(settings.DATABASE_URL)
    try:
        assert engine.dialect.driver == "psycopg"
        assert engine.url.query["sslmode"] == "require"
    finally:
        engine.dispose()


def test_sqlite_url_remains_available_for_local_development():
    settings = Settings(_env_file=None, DATABASE_URL="sqlite:///./local.db")
    assert settings.DATABASE_URL == "sqlite:///./local.db"


@pytest.mark.parametrize("origins", [
    "https://app.example.com/, https://www.example.com",
    '["https://app.example.com/", "https://www.example.com"]',
    ["https://app.example.com/", "https://www.example.com"],
])
def test_frontend_origins_accept_supported_environment_formats(origins):
    settings = Settings(_env_file=None, CORS_ORIGINS=origins)
    assert settings.CORS_ORIGINS == ["https://app.example.com", "https://www.example.com"]


def test_production_rejects_wildcard_cors():
    with pytest.raises(ValidationError, match="explicit frontend origins"):
        Settings(
            _env_file=None,
            APP_ENV="production",
            JWT_SECRET="configuration-tests-only-private-secret-123456",
            CORS_ORIGINS="*",
        )


def test_backend_can_start_before_frontend_domain_is_assigned():
    settings = Settings(
        _env_file=None,
        APP_ENV="production",
        JWT_SECRET="configuration-tests-only-private-secret-123456",
        CORS_ORIGINS="[]",
    )
    assert settings.CORS_ORIGINS == []


@pytest.mark.parametrize("secret", ["", "short", Settings.model_fields["JWT_SECRET"].default])
def test_production_rejects_development_or_short_secrets(secret):
    with pytest.raises(ValidationError, match="private JWT_SECRET"):
        Settings(_env_file=None, APP_ENV="production", JWT_SECRET=secret, CORS_ORIGINS=[])
