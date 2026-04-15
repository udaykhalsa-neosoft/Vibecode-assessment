import unittest
import tempfile
import os
from app import app
from utils.db import init_db


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a blank, temporary database before each test."""
        self.db_fd, self.db_path = tempfile.mkstemp()

        app.config['TESTING'] = True
        app.config['DB_PATH'] = self.db_path

        self.client = app.test_client()

        with app.app_context():
            init_db()

    def tearDown(self):
        """Destroy the temporary database after each test."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
