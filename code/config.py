import os


DEBUG = False
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///data.db") # Uses sqlite in case if DATABASE_URL is not set
