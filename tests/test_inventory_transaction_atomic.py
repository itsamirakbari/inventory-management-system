import unittest
from unittest.mock import patch

from db import create_inventory_transaction_with_stock_update


class FakeCursor:
    def __init__(self, product, fail_on_update=False):
        self.product = product
        self.fail_on_update = fail_on_update
        self.executed_queries = []
        self.lastrowid = 101
        self.rowcount = 0
        self.closed = False

    def execute(self, query, params=None):
        normalized_query = " ".join(query.split())
        self.executed_queries.append((normalized_query, params))

        if normalized_query.startswith("UPDATE products"):
            if self.fail_on_update:
                raise RuntimeError("Simulated stock update failure")
            self.rowcount = 1

    def fetchone(self):
        return self.product

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, product, fail_on_update=False):
        self.fake_cursor = FakeCursor(product, fail_on_update)
        self.transaction_started = False
        self.commit_count = 0
        self.rollback_count = 0
        self.closed = False

    def start_transaction(self):
        self.transaction_started = True

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


class InventoryTransactionAtomicTests(unittest.TestCase):
    def setUp(self):
        self.product = {
            "id": 7,
            "name": "Test Product",
            "sku": "TEST-007",
            "stock_quantity": 10
        }

    def run_transaction(
            self,
            transaction_type,
            quantity,
            product=None,
            fail_on_update=False
    ):
        connection = FakeConnection(
            self.product if product is None else product,
            fail_on_update=fail_on_update
        )

        with patch("db.get_connection", return_value=connection):
            result = create_inventory_transaction_with_stock_update(
                transaction_type=transaction_type,
                product_id=7,
                user_id=3,
                quantity=quantity,
                reason="purchase",
                transaction_reference="TEST-2026-0001",
                note="Automated test"
            )

        return connection, result

    def test_stock_out_commits_transaction_and_new_stock_together(self):
        connection, result = self.run_transaction("stock_out", 4)

        self.assertTrue(connection.transaction_started)
        self.assertEqual(connection.commit_count, 1)
        self.assertEqual(connection.rollback_count, 0)
        self.assertEqual(result["old_stock"], 10)
        self.assertEqual(result["new_stock"], 6)
        self.assertEqual(result["transaction_id"], 101)

        queries = connection.fake_cursor.executed_queries
        self.assertEqual(len(queries), 3)
        self.assertIn("FOR UPDATE", queries[0][0])
        self.assertTrue(queries[1][0].startswith("INSERT INTO inventory_transactions"))
        self.assertTrue(queries[2][0].startswith("UPDATE products"))
        self.assertEqual(queries[2][1], (6, 7))
        self.assertTrue(connection.fake_cursor.closed)
        self.assertTrue(connection.closed)

    def test_stock_in_increases_stock(self):
        connection, result = self.run_transaction("stock_in", 5)

        self.assertEqual(result["old_stock"], 10)
        self.assertEqual(result["new_stock"], 15)
        self.assertEqual(connection.commit_count, 1)
        self.assertEqual(connection.rollback_count, 0)

    def test_insufficient_stock_rolls_back_without_insert_or_update(self):
        connection = FakeConnection(self.product)

        with patch("db.get_connection", return_value=connection):
            with self.assertRaisesRegex(
                    ValueError,
                    "Not enough stock for this transaction"
            ):
                create_inventory_transaction_with_stock_update(
                    transaction_type="stock_out",
                    product_id=7,
                    user_id=3,
                    quantity=11,
                    reason="sale",
                    transaction_reference="TEST-2026-0002",
                    note="Automated test"
                )

        self.assertEqual(connection.commit_count, 0)
        self.assertEqual(connection.rollback_count, 1)
        self.assertEqual(len(connection.fake_cursor.executed_queries), 1)
        self.assertIn("FOR UPDATE", connection.fake_cursor.executed_queries[0][0])
        self.assertTrue(connection.closed)

    def test_update_failure_rolls_back_insert(self):
        connection = FakeConnection(self.product, fail_on_update=True)

        with patch("db.get_connection", return_value=connection):
            with self.assertRaisesRegex(
                    RuntimeError,
                    "Simulated stock update failure"
            ):
                create_inventory_transaction_with_stock_update(
                    transaction_type="stock_in",
                    product_id=7,
                    user_id=3,
                    quantity=3,
                    reason="purchase",
                    transaction_reference="TEST-2026-0003",
                    note="Automated test"
                )

        self.assertEqual(connection.commit_count, 0)
        self.assertEqual(connection.rollback_count, 1)
        self.assertEqual(len(connection.fake_cursor.executed_queries), 3)
        self.assertTrue(connection.closed)


if __name__ == "__main__":
    unittest.main()
