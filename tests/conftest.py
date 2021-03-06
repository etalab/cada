import factory
import pytest

from pytest_factoryboy import register

from cada import create_app
from cada.models import db, Advice, PARTS
from cada.search import es


@register
class AdviceFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Advice

    id = factory.Faker('word')
    administration = factory.Faker('company')
    type = factory.Faker('word')
    session = factory.Faker('date_time_this_decade', before_now=True, after_now=False)
    subject = factory.Faker('sentence', nb_words=4)
    part = factory.Faker('random_element', elements=PARTS.keys())
    content = factory.Faker('paragraph')


class TestConfig:
    TESTING = True
    MONGODB_DB = 'cada-test'
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.test_request_context('/'):
        db_name = app.config['MONGODB_DB']
        db.connection.drop_database(db_name)


@pytest.fixture()
def clean_es(app):
    with app.test_request_context('/'):
        es.initialize()
        es.cluster.health(index=es.index_name, wait_for_status='yellow', request_timeout=1)
    yield
    with app.test_request_context('/'):
        es.indices.delete(index=es.index_name, ignore=[400, 404])
