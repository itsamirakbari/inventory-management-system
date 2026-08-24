import unittest
from unittest.mock import patch

import mysql.connector

from db import execute


class FakeCursor:
    def __init__(self, error=None, rowcount=1):
        self.error = error
        self.rowcount = rowcount
        self.closed = False

    def execute(self, query, params=None):
        if self.error:
            raise self.error

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.commit_count = 0
        self.rollback_count = 0
        self.closed = False

    def cursor(self, dictionary=False):
        return self.fake_cursor

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1

    def is_connected(self):
        return not self.closed

    def close(self):
        self.closed = True


class ExecuteTests(unittest.TestCase):
    def test_success_commits_and_closes_connection(self):
        cursor = FakeCursor(rowcount=2)
        connection = FakeConnection(cursor)

        with patch("db.get_connection", return_value=connection):
            affected_rows = execute(
                "UPDATE products SET is_active = %s WHERE id = %s",
                (False, 7)
            )

        self.assertEqual(affected_rows, 2)
        self.assertEqual(connection.commit_count, 1)
        self.assertEqual(connection.rollback_count, 0)
        self.assertTrue(cursor.closed)
        self.assertTrue(connection.closed)

    def test_database_error_rolls_back_before_connection_is_closed(self):
        database_error = mysql.connector.IntegrityError(
            msg="Simulated foreign key restriction"
        )
        cursor = FakeCursor(error=database_error)
        connection = FakeConnection(cursor)

        with patch("db.get_connection", return_value=connection):
            with self.assertRaises(mysql.connector.IntegrityError) as error:
                execute("DELETE FROM products WHERE id = %s", (7,))

        self.assertIs(error.exception, database_error)
        self.assertEqual(connection.commit_count, 0)
        self.assertEqual(connection.rollback_count, 1)
        self.assertTrue(cursor.closed)
        self.assertTrue(connection.closed)


if __name__ == "__main__":
    unittest.main()
