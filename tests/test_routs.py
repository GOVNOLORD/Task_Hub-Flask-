import pytest
from app import app
from models import db, User, Project, Task


@pytest.fixture(scope='function')
def setup_test_database():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    db.create_all()
    yield
    db.session.remove()
    db.drop_all()


def test_home_page(setup_test_database):
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200


def test_create_task(setup_test_database):
    client = app.test_client()
    response = client.post('/create_task', data={'title': 'New Task'})
    assert response.status_code == 200


def test_view_project(setup_test_database):
    client = app.test_client()
    response = client.get('/project/1')
    assert response.status_code == 200


def test_delete_task(setup_test_database):
    client = app.test_client()
    response = client.post('/delete_task/1')
    assert response.status_code == 302
