import pytest

import server

def test_dummy():
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.data != None

def test_sessionid_exists():
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    rv = client.get('/')
    assert rv.status_code == 200
    data = rv.headers['Set-Cookie']
    assert data != None

def test_get_login_page():
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    rv = client.get('/login')
    assert rv.status_code == 200
    heads = rv.headers['Set-Cookie']
    data = rv.data.decode('utf-8')
    assert heads != None
    assert data != None
    assert 'Nutzername' in data


def test_register():
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    rv = client.post('/register', data=dict(firstname='admin', lastname='admin', username='admin', password='admin'), follow_redirects=True)
    assert rv.status_code == 200


def test_login():

    # register user admin
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    rv = client.post('/register', data=dict(firstname='admin', lastname='admin', username='admin', password='admin'),follow_redirects=True)
    assert rv.status_code == 200

    # login user admin
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    rv = client.post('/login', data=dict(username='admin', password='admin'), follow_redirects=True)
    assert rv.status_code == 200
    data = rv.data.decode('utf-8')
    assert 'Sie haben sich sicher bei FIDO Demo angemeldet.' in data
