import unittest
import sqlite3
from contextlib import closing

class TestSQLInjection(unittest.TestCase):

    def setUp(self):
        # Setup in-memory database for testing
        self.connection = sqlite3.connect(':memory:')
        self.create_tables()
        self.insert_test_data()

    def tearDown(self):
        # Close the database connection after each test
        self.connection.close()

    def create_tables(self):
        with closing(self.connection.cursor()) as cursor:
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            self.connection.commit()

    def insert_test_data(self):
        with closing(self.connection.cursor()) as cursor:
            cursor.execute('''
                INSERT INTO users (username, password) VALUES
                ('user1', 'pass1'),
                ('user2', 'pass2')
            ''')
            self.connection.commit()

    def test_sql_injection_prevention(self):
        # Test to ensure SQL injection is prevented
        malicious_input = "'; DROP TABLE users; --"
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute('SELECT * FROM users WHERE username = ?', (malicious_input,))
                self.connection.commit()
            except sqlite3.OperationalError as e:
                self.fail(f"SQL Injection occurred: {e}")

        # Verify that the users table still exists
        with closing(self.connection.cursor()) as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone()
            self.assertIsNotNone(table_exists, "Users table should still exist")

    def test_safe_query_execution(self):
        # Test safe query execution using parameterized queries
        username = 'user1'
        password = 'pass1'
        with closing(self.connection.cursor()) as cursor:
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            self.assertIsNotNone(user, "User should be found with correct credentials")

    def test_unsuccessful_login(self):
        # Test unsuccessful login with incorrect credentials
        username = 'user1'
        password = 'wrongpass'
        with closing(self.connection.cursor()) as cursor:
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            self.assertIsNone(user, "User should not be found with incorrect credentials")

if __name__ == '__main__':
    unittest.main()