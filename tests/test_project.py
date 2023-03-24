import time
import unittest
from unittest import TestCase, mock

import psycopg2
from fastapi.testclient import TestClient

import main
client = TestClient(main.app)
DB_HOST = '172.22.0.2'
DB_NAME = 'example_db'
DB_USER = 'postgres'
DB_PASSWORD = 'example'
DB_PORT = '5432'


class TestUserAuthentication(TestCase):
    def setUp(self):
        self.conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )

    def tearDown(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM users")
        self.conn.commit()
        cur.close()
        self.conn.close()

    def test_create_user_success(self):
        # Arrange
        user = {'name': 'John Doe', 'email': 'houssem.khlifi@elyadata.com'}

        # Act
        response = client.put('/user', json=user)

        # Assert
        assert response.status_code == 200
        assert response.json() == user

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (user['email'],))
        db_user = cur.fetchone()
        cur.close()

        assert db_user is not None
        assert db_user[1] == user['name']
        assert db_user[2] == user['email']

    def test_create_user_duplicate_email(self):
        # Arrange
        user = {'name': 'John Doe', 'email': 'houssem.khlifi@elyadata.com'}

        cur = self.conn.cursor()
        cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (user['name'], user['email']))
        self.conn.commit()
        cur.close()

        # Act
        response = client.put('/user', json=user)

        # Assert
        assert response.status_code == 400
        assert response.json() == {'detail': 'User already exists'}

    def test_create_user_db_error(self):
        # Arrange
        user = {'name': 'John Doe', 'email': 'houssem.khlifi@elyadata.com'}

        with mock.patch('main.psycopg2.connect') as mock_conn:
            mock_conn.side_effect = psycopg2.OperationalError('mock error')

            # Act
            response = client.put('/user', json=user)

        # Assert
        assert response.status_code == 500
        assert 'mock error' in response.json()['detail']

    def test_verify_expired_code(self):
        # Arrange
        email = 'houssem.khlifi@elyadata.com'
        code = '1234'
        main.temp_db[email] = {'code': code, 'timestamp': time.time() - 61}

        # Act
        response = client.post('/verify', data={'email': email, 'code': code})

        # Assert
        assert response.status_code == 400
        assert 'has expired' in response.json()['detail']


if __name__ == '__main__':
    unittest.main()
