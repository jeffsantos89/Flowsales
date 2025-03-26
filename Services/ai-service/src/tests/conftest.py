import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from myapp.models import Base, MyModel
from myapp import create_app

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db_engine(app):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(scope='function')
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def init_db(db_session):
    # Add initial data to the database for testing
    db_session.add(MyModel(name='Test'))
    db_session.commit()
    yield db_session
    db_session.query(MyModel).delete()
    db_session.commit()