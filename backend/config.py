# backend/config.py
import os

class Config:
    """Base configuration with default settings."""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # API Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # NASA API Configuration
    NASA_API_KEY = os.environ.get('NASA_API_KEY', 'DEMO_KEY')
    NASA_BASE_URL = 'https://api.nasa.gov/neo/rest/v1/neo/'
    
    # Redis Configuration (for rate limiting and caching)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # ML Model Configuration
    ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), 'ml_models')
    
    # Physics Configuration
    DEFAULT_ASTEROID_DENSITY = 2000  # kg/m³
    EARTH_RADIUS_KM = 6371
    SAFE_MISS_DISTANCE_KM = 10000
    
    # Analysis Configuration
    HAZARD_CORRIDOR_SIMULATIONS = 20
    TRAJECTORY_POINTS = 100
    MAX_PROPAGATION_DAYS = 365
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT = "200 per day, 50 per hour"
    RATE_LIMIT_ANALYSIS = "10 per minute"
    RATE_LIMIT_PDF = "5 per minute"

class ProductionConfig(Config):
    """Production configuration with secure settings."""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    
    # Stricter rate limiting in production
    RATE_LIMIT_DEFAULT = "1000 per day, 100 per hour"
    RATE_LIMIT_ANALYSIS = "20 per minute"
    
    # Required security settings
    SECRET_KEY = os.environ['SECRET_KEY']  # Must be set in production
    
    # CORS settings for production
    ALLOWED_ORIGINS = [
        "https://your-planetary-defense-app.com",
        "https://www.your-planetary-defense-app.com"
    ]

class DevelopmentConfig(Config):
    """Development configuration with relaxed settings."""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = False
    
    # More permissive rate limiting for development
    RATE_LIMIT_DEFAULT = "1000 per day, 200 per hour"
    RATE_LIMIT_ANALYSIS = "50 per minute"
    
    # CORS settings for development
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5000"
    ]

class TestingConfig(Config):
    """Testing configuration."""
    FLASK_ENV = 'testing'
    DEBUG = False
    TESTING = True
    
    # Disable rate limiting for tests
    RATE_LIMIT_DEFAULT = "10000 per day"
    RATE_LIMIT_ANALYSIS = "1000 per minute"
    
    # Test-specific settings
    TEST_ASTEROID_ID = "99942"
    TEST_HAZARD_SIMULATIONS = 5

def get_config():
    """Get appropriate configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()

# Current configuration
current_config = get_config()