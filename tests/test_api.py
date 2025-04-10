import unittest
import os
import sys
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from api_handler import app
import api_handler

TEST_API_KEY = "twetArxt5425AgesR"
INVALID_API_KEY = "invalidKey123"

test_script_dir = os.path.dirname(os.path.abspath(__file__))
temp_root_dir = os.path.join(test_script_dir, "temp_test_root")
temp_src_dir = os.path.join(temp_root_dir, "src")
temp_data_dir = os.path.join(temp_root_dir, "data")
temp_news_data_dir = os.path.join(temp_data_dir, "news_data")

mock_stocklist_data = [{"ticker": "AAPL", "name": "Apple Inc."}, {"ticker": "GOOGL", "name": "Alphabet Inc."}]
mock_recommendations_data = {"top_5_best": [{"ticker": "AAPL", "weighted_average": 0.8}], "top_5_worst": []}
mock_aapl_news_data = {"ticker": "AAPL", "total_news": 1, "average_sentiment": 0.5, "news": [{"id": "123", "summary": "Good news", "date": "2025-04-08T12:00:00Z", "sentiment-score": 0.5}]}

class TestAPI(unittest.TestCase):

    client = None
    original_api_script_dir = None

    @classmethod
    def setUpClass(cls):
        if os.path.exists(temp_root_dir):
            for root, dirs, files in os.walk(temp_root_dir, topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                    except OSError:
                        pass
                for name in dirs:
                     try:
                        os.rmdir(os.path.join(root, name))
                     except OSError:
                         pass
            if os.path.exists(temp_root_dir):
                try:
                    os.rmdir(temp_root_dir)
                except OSError:
                    pass

        os.makedirs(temp_root_dir, exist_ok=True)
        os.makedirs(temp_src_dir, exist_ok=True)
        os.makedirs(temp_data_dir, exist_ok=True)
        os.makedirs(temp_news_data_dir, exist_ok=True)

        stocklist_path = os.path.join(temp_data_dir, "stocklist.json")
        recomm_path = os.path.join(temp_data_dir, "recommendations.json")
        aapl_news_path = os.path.join(temp_news_data_dir, "aapl_news.json")

        with open(stocklist_path, "w") as f:
            json.dump(mock_stocklist_data, f)
        with open(recomm_path, "w") as f:
            json.dump(mock_recommendations_data, f)
        with open(aapl_news_path, "w") as f:
            json.dump(mock_aapl_news_data, f)

        cls.original_api_script_dir = api_handler.script_dir
        api_handler.script_dir = temp_src_dir

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        if cls.original_api_script_dir:
             api_handler.script_dir = cls.original_api_script_dir

        if os.path.exists(temp_root_dir):
            for root, dirs, files in os.walk(temp_root_dir, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass # Ignore potential errors during cleanup
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    try:
                        os.rmdir(dir_path)
                    except OSError:
                         pass # Ignore potential errors during cleanup
            try:
                os.rmdir(temp_root_dir)
            except OSError:
                 pass # Ignore potential errors during cleanup

    def test_get_ticker_news_success(self):
        response = self.client.get("/data/aapl", params={"api_key": TEST_API_KEY})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_aapl_news_data)

    def test_get_ticker_news_invalid_key(self):
        response = self.client.get("/data/aapl", params={"api_key": INVALID_API_KEY})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid API Key"})

    def test_get_ticker_news_missing_key(self):
        response = self.client.get("/data/aapl")
        self.assertEqual(response.status_code, 422)

    def test_get_ticker_news_not_found(self):
        response = self.client.get("/data/googl", params={"api_key": TEST_API_KEY})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "News data not found for this ticker"})

    def test_get_ticker_news_corrupted_json(self):
        corrupted_path = os.path.join(temp_news_data_dir, "corrupt_news.json")
        with open(corrupted_path, "w") as f:
            f.write("{invalid json:")
        response = self.client.get("/data/corrupt", params={"api_key": TEST_API_KEY})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Invalid JSON format", response.json()["detail"])

    def test_get_stock_list_success(self):
        response = self.client.get("/stock", params={"api_key": TEST_API_KEY})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_stocklist_data)

    def test_get_stock_list_invalid_key(self):
        response = self.client.get("/stock", params={"api_key": INVALID_API_KEY})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid API Key"})

    def test_get_stock_list_missing_key(self):
        response = self.client.get("/stock")
        self.assertEqual(response.status_code, 422)

    def test_get_stock_list_file_not_found(self):
        original_path = os.path.join(temp_data_dir, "stocklist.json")
        renamed_path = os.path.join(temp_data_dir, "stocklist_renamed.json")
        if os.path.exists(original_path):
            os.rename(original_path, renamed_path)
        response = self.client.get("/stock", params={"api_key": TEST_API_KEY})
        if os.path.exists(renamed_path):
            os.rename(renamed_path, original_path)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Stock list file not found"})

    def test_get_stock_list_corrupted_json(self):
        original_path = os.path.join(temp_data_dir, "stocklist.json")
        original_content = ""
        try:
            # Ensure file exists before reading
            if os.path.exists(original_path):
                with open(original_path, "r") as f:
                    original_content = f.read()
            # Write corrupted data regardless, test expects this file to exist
            with open(original_path, "w") as f:
                f.write("{invalid json:")
            response = self.client.get("/stock", params={"api_key": TEST_API_KEY})
            self.assertEqual(response.status_code, 500)
            self.assertIn("Invalid JSON format", response.json()["detail"])
        finally:
             if original_content and os.path.exists(original_path):
                  with open(original_path, "w") as f:
                       f.write(original_content)

    def test_get_recommendations_success(self):
        response = self.client.get("/recommendations", params={"api_key": TEST_API_KEY})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_recommendations_data)

    def test_get_recommendations_invalid_key(self):
        response = self.client.get("/recommendations", params={"api_key": INVALID_API_KEY})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid API Key"})

    def test_get_recommendations_missing_key(self):
        response = self.client.get("/recommendations")
        self.assertEqual(response.status_code, 422)

    def test_get_recommendations_file_not_found(self):
        original_path = os.path.join(temp_data_dir, "recommendations.json")
        renamed_path = os.path.join(temp_data_dir, "recommendations_renamed.json")
        if os.path.exists(original_path):
            os.rename(original_path, renamed_path)
        response = self.client.get("/recommendations", params={"api_key": TEST_API_KEY})
        if os.path.exists(renamed_path):
            os.rename(renamed_path, original_path)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Recommendations file not found"})

    def test_get_recommendations_corrupted_json(self):
        original_path = os.path.join(temp_data_dir, "recommendations.json")
        original_content = ""
        try:
            # Ensure file exists before reading
            if os.path.exists(original_path):
                with open(original_path, "r") as f:
                     original_content = f.read()
            # Write corrupted data regardless
            with open(original_path, "w") as f:
                 f.write("{invalid json:")
            response = self.client.get("/recommendations", params={"api_key": TEST_API_KEY})
            self.assertEqual(response.status_code, 500)
            self.assertIn("Invalid JSON format", response.json()["detail"])
        finally:
            if original_content and os.path.exists(original_path):
                 with open(original_path, "w") as f:
                      f.write(original_content)

if __name__ == "__main__":
    unittest.main()