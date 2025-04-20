from app.db.base import Base
from app.db.session import engine
from app.db.models import user, ticket, message  # Make sure all models are imported

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    create_tables()
