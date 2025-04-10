import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from sentiment_analyser import SentimentAnalyzer

class TestSentimentAnalyzer(unittest.TestCase):

    analyzer = None

    @classmethod
    def setUpClass(cls):
        print("Setting up SentimentAnalyzer tests...")
        cls.analyzer = SentimentAnalyzer()
        print("Setup complete.")

    @classmethod
    def tearDownClass(cls):
        print("\nTearing down SentimentAnalyzer tests...")
        if hasattr(cls, 'analyzer') and cls.analyzer is not None:
             del cls.analyzer
             cls.analyzer = None
        print("Teardown complete.")

    def test_positive_sentiment(self):
        text = "The company's earnings beat expectations."
        score = self.analyzer.analyze_sentiment(text)
        self.assertGreater(score, 0.1, f"Score {score} is not sufficiently positive for: '{text}'")

    def test_negative_sentiment(self):
        text = "Stocks plummeted after the news."
        score = self.analyzer.analyze_sentiment(text)
        self.assertLess(score, -0.1, f"Score {score} is not sufficiently negative for: '{text}'")

    def test_neutral_sentiment(self):
        text = "Nothing happened with the Amazon stock today"
        score = self.analyzer.analyze_sentiment(text)
        self.assertAlmostEqual(score, 0, delta=0.2, msg=f"Score {score} is not close enough to zero for neutral: '{text}'")

    def test_empty_string_sentiment(self):
        text = ""
        score = self.analyzer.analyze_sentiment(text)
        self.assertAlmostEqual(score, 0, delta=0.2, msg=f"Score {score} for empty string is not close to zero")

if __name__ == "__main__":
    unittest.main()