"""
Unit test file for aider upgrade.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from aicode.aider_control import aider_install, aider_upgrade


class AiderUpgradeTester(unittest.TestCase):
    """Test class for aider upgrade functionality."""

    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(str(self.temp_dir), ignore_errors=True)

    def test_aider_upgrade(self):
        """Test that aider can be upgraded."""
        # First, install aider
        aider_install(self.temp_dir)
        # Now try to upgrade
        result = aider_upgrade(self.temp_dir)
        # Check if the upgrade was successful
        self.assertEqual(result, 0, "Aider upgrade failed")


if __name__ == "__main__":
    unittest.main()
