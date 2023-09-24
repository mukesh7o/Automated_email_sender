from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import SQLALCHEMY_DATABASE_URI,PROJECT_NAME
import logging
logger = logging.getLogger(PROJECT_NAME)
logger.propagate = False

db = SQLAlchemy()
base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=3600, connect_args={'connect_timeout': 60})
Session = sessionmaker(bind=engine)
session = Session()
