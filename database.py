from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = "mysql+pymysql://root:yourpassword@localhost/task_app"

engine = create_engine(DB_URL)
sessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)