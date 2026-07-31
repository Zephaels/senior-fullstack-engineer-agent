import unittest

from retry_policy import MAX_ATTEMPTS, should_retry


class RetryPolicyTests(unittest.TestCase):
    def test_current_revision_uses_three_attempts(self):
        self.assertEqual(MAX_ATTEMPTS, 3)
        self.assertTrue(should_retry(2))
        self.assertFalse(should_retry(3))


if __name__ == "__main__":
    unittest.main()
