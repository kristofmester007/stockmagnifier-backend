import unittest
import os
import sys
from datetime import datetime, timezone, timedelta
import io
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from news_collector import _calculate_weighted_average, _calculate_average_daily_sentiments

def get_relative_date_iso(days_ago):
    date = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return date.isoformat(timespec='seconds').replace('+00:00', 'Z')

class TestUtils(unittest.TestCase):

    def test_calculate_weighted_average_empty_list(self):
        news_list = []
        result = _calculate_weighted_average(news_list)
        self.assertEqual(result, 0)

    def test_calculate_weighted_average_valid_data(self):
        news_list = [
            {"date": get_relative_date_iso(0), "sentiment-score": 0.5},
            {"date": get_relative_date_iso(1), "sentiment-score": 0.8},
            {"date": get_relative_date_iso(2), "sentiment-score": -0.2},
            {"date": get_relative_date_iso(3), "sentiment-score": 0.4},
            {"date": get_relative_date_iso(4), "sentiment-score": 0.6},
            {"date": get_relative_date_iso(5), "sentiment-score": -0.7},
            {"date": get_relative_date_iso(6), "sentiment-score": 0.9},
            {"date": get_relative_date_iso(7), "sentiment-score": 0.3},
        ]
        result = _calculate_weighted_average(news_list)

        expected_weight = 0.0
        expected_sum = 0.0
        scores = [0.5, 0.8, -0.2, 0.4, 0.6, -0.7, 0.9]
        for i in range(7):
             weight = 1.0 - (i * 0.15)
             expected_weight += weight
             expected_sum += scores[i] * weight
        expected_avg = expected_sum / expected_weight if expected_weight else 0
        self.assertAlmostEqual(result, expected_avg, places=7)

    def test_calculate_weighted_average_invalid_date(self):
        news_list = [
            {"date": "invalid-date", "sentiment-score": 0.5},
            {"date": get_relative_date_iso(0), "sentiment-score": 0.6},
        ]
        with io.StringIO() as buf, patch('sys.stdout', buf):
            result = _calculate_weighted_average(news_list)
            output = buf.getvalue()

        self.assertIn("Warning: Invalid date format", output)
        self.assertAlmostEqual(result, 0.6, places=7)

    def test_calculate_weighted_average_mixed_data(self):
        news_list = [
            {"date": get_relative_date_iso(0), "sentiment-score": 0.5},
            {"date": "invalid-date", "sentiment-score": 0.8},
            {"date": get_relative_date_iso(2), "sentiment-score": -0.2},
            {"date": get_relative_date_iso(8), "sentiment-score": 0.4},
        ]
        with io.StringIO() as buf, patch('sys.stdout', buf):
            result = _calculate_weighted_average(news_list)
            output = buf.getvalue()

        self.assertIn("Warning: Invalid date format", output)
        expected_weight = 1.0 + 0.7
        expected_sum = (0.5 * 1.0) + (-0.2 * 0.7)
        expected_avg = expected_sum / expected_weight if expected_weight else 0
        self.assertAlmostEqual(result, expected_avg, places=7)

    def test_calculate_average_daily_sentiments_empty_list(self):
        news_list = []
        result = _calculate_average_daily_sentiments(news_list)
        self.assertEqual(result, [0] * 7)

    def test_calculate_average_daily_sentiments_valid_data(self):
        today_date_str = get_relative_date_iso(0)[:10]

        news_list = [
            {"date": f"{today_date_str}T10:00:00Z", "sentiment-score": 0.5},
            {"date": f"{today_date_str}T12:00:00Z", "sentiment-score": 0.6},
            {"date": get_relative_date_iso(1), "sentiment-score": 0.8},
            {"date": get_relative_date_iso(2), "sentiment-score": -0.2},
            {"date": get_relative_date_iso(4), "sentiment-score": 0.4},
            {"date": get_relative_date_iso(7), "sentiment-score": 0.9},
        ]
        result = _calculate_average_daily_sentiments(news_list)

        expected = [
            (0.5 + 0.6) / 2,
            0.8,
            -0.2,
            0,
            0.4,
            0,
            0,
        ]
        self.assertEqual(len(result), len(expected))
        for i in range(len(expected)):
            self.assertAlmostEqual(result[i], expected[i], places=7)

    def test_calculate_average_daily_sentiments_invalid_date(self):
        news_list = [
            {"date": "invalid-date", "sentiment-score": 0.5},
            {"date": get_relative_date_iso(0), "sentiment-score": 0.7},
        ]
        with io.StringIO() as buf, patch('sys.stdout', buf):
            result = _calculate_average_daily_sentiments(news_list)
            output = buf.getvalue()

        self.assertIn("Warning: Invalid date format", output)
        expected = [0.7, 0, 0, 0, 0, 0, 0]
        self.assertEqual(len(result), len(expected))
        for i in range(len(expected)):
            self.assertAlmostEqual(result[i], expected[i], places=7)

    def test_calculate_average_daily_sentiments_mixed_data(self):
        news_list = [
            {"date": get_relative_date_iso(0), "sentiment-score": 0.5},
            {"date": "invalid-date", "sentiment-score": 0.6},
            {"date": get_relative_date_iso(1), "sentiment-score": 0.8},
            {"date": get_relative_date_iso(7), "sentiment-score": -0.2},
        ]
        with io.StringIO() as buf, patch('sys.stdout', buf):
            result = _calculate_average_daily_sentiments(news_list)
            output = buf.getvalue()

        self.assertIn("Warning: Invalid date format", output)
        expected = [0.5, 0.8, 0, 0, 0, 0, 0]
        self.assertEqual(len(result), len(expected))
        for i in range(len(expected)):
            self.assertAlmostEqual(result[i], expected[i], places=7)

if __name__ == "__main__":
    unittest.main()