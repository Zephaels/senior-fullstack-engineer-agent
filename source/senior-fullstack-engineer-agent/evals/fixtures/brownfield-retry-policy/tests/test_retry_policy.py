import unittest

from retry_policy import MAX_ATTEMPTS, should_retry


class RetryPolicyTests(unittest.TestCase):
    def test_default_behavior_is_preserved(self):
        self.assertEqual(MAX_ATTEMPTS, 3)
        self.assertTrue(should_retry(2))
        self.assertFalse(should_retry(3))

    def test_caller_can_supply_a_bounded_attempt_count(self):
        self.assertTrue(should_retry(4, max_attempts=5))
        self.assertFalse(should_retry(5, max_attempts=5))

    def test_negative_max_attempts_is_rejected(self):
        with self.assertRaises(ValueError):
            should_retry(0, max_attempts=-1)


if __name__ == "__main__":
    unittest.main()
