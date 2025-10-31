"""
Application Configuration
=========================

This module manages all application settings using environment variables.

What This Does:
- Defines default configuration values (database URL, secret keys, etc.)
- Loads overrides from .env file (if exists)
- Validates settings using Pydantic
- Provides single 'settings' object used throughout the app


How It Works:
1. Settings class defines all config with defaults
2. Pydantic reads .env file and overrides defaults
3. Import 'settings' anywhere: from app.config import settings


Why Pydantic BaseSettings?
==========================

BaseSettings extends pydantic.BaseModel with automatic environment variable loading:

What BaseModel Provides (core Pydantic):
    ✓ Type validation (ensures DATABASE_URL is a string, DEBUG is a bool, etc.)
    ✓ Data parsing (converts "True" → True, "42" → 42)
    ✓ Field validation (custom validators, constraints)
    ✓ Serialization (model_dump(), model_dump_json())

What BaseSettings Adds (pydantic-settings package):
    ✓ Automatic environment variable reading (os.getenv for each field)
    ✓ Automatic .env file loading (no manual file parsing)
    ✓ Type conversion from env vars (string "8000" → int 8000)
    ✓ Priority handling (env vars > .env file > defaults)
    ✓ Secrets support (Docker secrets, AWS Secrets Manager, etc.)
    ✓ Nested model support (complex configurations)

Without BaseSettings, you'd write:
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://...')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'  # Manual conversion!
    PORT = int(os.getenv('PORT', '8000'))  # Manual type casting!
    
With BaseSettings, Pydantic does all of this automatically! ✨

Inheritance Chain:
    Settings → BaseSettings → BaseModel → object
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json


# ═══════════════════════════════════════════════
# Settings Class - All Application Configuration
# ═══════════════════════════════════════════════

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    Pydantic automatically:
    - Reads .env file (if present)
    - Overrides defaults with env vars
    - Validates types (raises error if DATABASE_URL isn't a string)
    - Converts values (string "True" → boolean True)
    """
    
    # ═══════════════════════════════════════════════
    # Application Settings
    # ═══════════════════════════════════════════════
    
    APP_NAME: str = "Mini Issue Tracker"  # Shown in API docs at /docs
    VERSION: str = "1.0.0"                # API version for client compatibility
    ENVIRONMENT: str = "development"      # "development", "staging", or "production"
    DEBUG: bool = True                    # If True: logs SQL queries, shows detailed errors
    
    # ═══════════════════════════════════════════════
    # Database Configuration
    # ═══════════════════════════════════════════════
    
    # PostgreSQL connection string
    # Format: postgresql://username:password@host:port/database_name
    # Default uses Docker service name "db" (from docker-compose.yml)
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/issue_tracker"
    
    # ═══════════════════════════════════════════════
    # Security Settings - JWT Authentication
    # ═══════════════════════════════════════════════
    
    # Secret key used to sign JWT tokens (MUST change in production!)
    # Generate secure key: python -c "import secrets; print(secrets.token_urlsafe(32))"
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    
    ALGORITHM: str = "HS256"              # JWT signing algorithm (HMAC with SHA-256)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # JWT tokens expire after 30 minutes
    
    # ═══════════════════════════════════════════════
    # CORS Settings - Cross-Origin Resource Sharing
    # ═══════════════════════════════════════════════
    
    # JSON string of allowed frontend URLs that can call this API
    # Must be JSON string because env vars can only be strings
    # Default allows local development frontends (Vite on 5173, React on 3000)
    BACKEND_CORS_ORIGINS: str = '["http://localhost:5173", "http://localhost:3000"]'
    
    @property
    def cors_origins(self) -> List[str]:
        """
        Converts CORS origins from JSON string to Python list.
        
        Why a property?
        - Environment variables are always strings
        - We need a list for FastAPI's CORS middleware
        - This converts "['url1', 'url2']" → ['url1', 'url2']
        
        Returns:
            List of allowed origin URLs
        
        Example:
            settings.BACKEND_CORS_ORIGINS = '["http://localhost:5173"]'
            settings.cors_origins → ["http://localhost:5173"]  (actual list)
        """
        try:
            return json.loads(self.BACKEND_CORS_ORIGINS)  # Parse JSON string to list
        except json.JSONDecodeError:
            # Fallback if JSON is invalid (safety net)
            return ["http://localhost:5173"]
    
    # ═══════════════════════════════════════════════
    # Pydantic Configuration
    # ═══════════════════════════════════════════════
    
    # Pydantic v2 configuration using model_config

    model_config = SettingsConfigDict(
        env_file=".env",           # Read environment variables from .env file
        env_file_encoding="utf-8", # Encoding for the .env file
        case_sensitive=True        # DATABASE_URL ≠ database_url (must match exactly)
    )


# ═══════════════════════════════════════════════
# Global Settings Instance
# ═══════════════════════════════════════════════

# Single instance of settings used throughout the application
"""When you create settings = Settings(), Pydantic checks multiple sources in the order:
1. Constructor arguments    ← Highest priority (overrides everything)(passed as a param in the settings instance)
2. Environment variables    ← System environment(set with export)
3. .env file               ← Dotenv file(Pydantic only checks this if configured to do so)
4. Default values          ← Lowest priority (fallback only)"""

settings = Settings()