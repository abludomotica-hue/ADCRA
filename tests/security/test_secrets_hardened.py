import os
import stat
import shutil
import tempfile
import unittest
from pathlib import Path

from adcra.infrastructure.secrets.secret_store import LocalSecureSecretStore


class TestSecretsHardened(unittest.TestCase):
    """
    ADCRA v2.1 Security & Secret Management Specification Tests.
    Verifies POSIX file permission enforcement (0600/0700), encryption, masking, and redaction.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.secret_dir = Path(self.temp_dir) / "secrets"
        self.store = LocalSecureSecretStore(storage_dir=self.secret_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_posix_permissions_hardened(self):
        """Verify storage directory is 0700 and secrets file is 0600."""
        self.store.set_secret("TEST_API_KEY", "super_secret_val_123")

        # Check directory permission
        dir_mode = stat.S_IMODE(os.stat(self.secret_dir).st_mode)
        self.assertEqual(dir_mode, 0o700)

        # Check file permission
        secrets_file = self.secret_dir / ".secrets.json"
        self.assertTrue(secrets_file.exists())
        file_mode = stat.S_IMODE(os.stat(secrets_file).st_mode)
        self.assertEqual(file_mode, 0o600)

    def test_encryption_at_rest(self):
        """Verify secrets file does NOT store plaintext keys."""
        raw_secret = "sensitive_production_token_xyz987"
        self.store.set_secret("PROD_TOKEN", raw_secret)

        secrets_file = self.secret_dir / ".secrets.json"
        with open(secrets_file, "r") as f:
            raw_content = f.read()

        self.assertNotIn(raw_secret, raw_content)
        # Verify store can retrieve the original plaintext
        self.assertEqual(self.store.get_secret("PROD_TOKEN"), raw_secret)

    def test_masked_secret_representation(self):
        """Verify masking displays first 3 and last 4 characters or clean stars."""
        key = "sk-proj-abc123456789xyz"
        self.store.set_secret("OPENAI_KEY", key)
        masked = self.store.get_masked_secret("OPENAI_KEY")

        self.assertIsNotNone(masked)
        self.assertTrue(masked.startswith("sk-") or masked.startswith("***"))
        self.assertNotIn("abc123456789", masked)

    def test_text_redaction(self):
        """Verify arbitrary text containing secrets is sanitized."""
        raw_key = "sk-live-998877665544332211"
        self.store.set_secret("LIVE_KEY", raw_key)

        log_message = f"Error calling OpenAI with key {raw_key} at endpoint https://api.openai.com/v1"
        sanitized = self.store.redact(log_message)

        self.assertNotIn(raw_key, sanitized)
        self.assertTrue("[REDACTED" in sanitized)

    def test_delete_secret(self):
        """Verify deletion removes key from memory and disk."""
        self.store.set_secret("EPHEMERAL_KEY", "temp_value")
        self.assertTrue(self.store.exists("EPHEMERAL_KEY"))

        deleted = self.store.delete_secret("EPHEMERAL_KEY")
        self.assertTrue(deleted)
        self.assertFalse(self.store.exists("EPHEMERAL_KEY"))
        self.assertIsNone(self.store.get_secret("EPHEMERAL_KEY"))


if __name__ == "__main__":
    unittest.main()
