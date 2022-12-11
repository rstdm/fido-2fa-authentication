import pytest

import server

def test_dummy():
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    rv = client.get('/')
    assert rv.data != None

def test_sessionid_exists():
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    rv = client.get('/')
    data = rv.headers['Set-Cookie']
    assert data != None

def test_get_login_page():
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    rv = client.get('/login')
    heads = rv.headers['Set-Cookie']
    data = rv.data.decode('utf-8')

    assert heads != None
    assert data != None
    assert 'Nutzername' in data


def test_login():
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    rv = client.post('/login', data=dict(username='admin', password='admin'), follow_redirects=True)
    assert rv.status_code == 200
    data = rv.data.decode('utf-8')
    assert 'Sie haben sich sicher bei FIDO Demo angemeldet.' in data

