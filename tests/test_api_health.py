"""Health endpoints must report real readiness without changing database state."""

import os
import unittest
from contextlib import contextmanager
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.app.api import health
from src.app.api.main import app


class Result:
    def __init__(self, value=None, rows=None):
        self.value = value
        self.rows = rows or []

    def scalar_one(self):
        return self.value

    def scalar_one_or_none(self):
        return self.value

    def mappings(self):
        return self

    def all(self):
        return self.rows


class FakeEngine:
    def __init__(self, database, queries, missing_gold=False):
        self.database = database
        self.queries = queries
        self.missing_gold = missing_gold
        self.disposed = False

    @contextmanager
    def begin(self):
        yield self

    def execute(self, sql):
        query = str(sql)
        self.queries.append(query)
        if "to_regclass('public.demo_session')" in query:
            return Result("demo_session")
        if "FROM public.demo_session" in query:
            return Result("uploaded_db")
        if "FROM unnest(ARRAY[" in query:
            return Result(rows=[{"table_name": "fact_sales", "present": not self.missing_gold}])
        if "SELECT EXISTS" in query:
            return Result(True)
        return Result(1)

    def dispose(self):
        self.disposed = True


class HealthTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_live_does_not_need_database(self):
        with patch.object(health, "create_db_engine", side_effect=RuntimeError("offline")):
            response = self.client.get("/api/health/live")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_ready_and_legacy_route_return_503_on_database_failure(self):
        with patch.dict(os.environ, {"DB_NAME": "base"}):
            with patch.object(health, "create_db_engine", side_effect=RuntimeError("secret")):
                for route in ("/api/health/ready", "/api/health"):
                    response = self.client.get(route)
                    self.assertEqual(response.status_code, 503)
                    self.assertEqual(response.json()["checks"]["control_database"], "failed")
                    self.assertNotIn("secret", response.text)

    def test_ready_uses_uploaded_database_and_selects_only(self):
        calls, queries, engines = [], [], []

        def factory(database, connect_timeout):
            calls.append((database, connect_timeout))
            engine = FakeEngine(database, queries)
            engines.append(engine)
            return engine

        with patch.dict(os.environ, {"DB_NAME": "base"}):
            with patch.object(health, "create_db_engine", side_effect=factory):
                response = self.client.get("/api/health/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["database"], "uploaded_db")
        self.assertEqual(response.json()["session"], "uploaded")
        self.assertEqual(calls, [("base", 3), ("uploaded_db", 3)])
        self.assertTrue(all(engine.disposed for engine in engines))
        self.assertFalse(any("CREATE " in query.upper() for query in queries))

    def test_missing_gold_table_is_not_ready(self):
        def factory(database, connect_timeout):
            return FakeEngine(database, [], missing_gold=(database == "uploaded_db"))

        with patch.dict(os.environ, {"DB_NAME": "base"}):
            with patch.object(health, "create_db_engine", side_effect=factory):
                response = self.client.get("/api/health/ready")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["checks"]["gold"], "failed")
        self.assertEqual(response.json()["missing_gold_tables"], ["fact_sales"])


if __name__ == "__main__":
    unittest.main()
