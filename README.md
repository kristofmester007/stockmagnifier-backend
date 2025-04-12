# StockMagnifier - Stock Sentiment Analysis Application - Backend

StockMagnifier is a web application that provides sentiment analysis for the top 50 companies of the S&P 500 index.

This repository contains the backend service for the StockMagnifier application. It's built with Python and FastAPI, handling data collection, sentiment analysis, and providing API endpoints for the frontend application.

Given that news is gathered and analyzed hourly, it's advisable to run the backend continuously for a week to build up a robust historical dataset for accurate results.

## Key Functionalities

* **API Endpoints:** Provides RESTful APIs for:
    * Fetching the list of monitored stocks (`/stock`).
    * Retrieving detailed news, sentiment scores (individual, average, weighted), and daily trends for a specific stock ticker (`/data/{ticker}`).
    * Getting stock recommendations based on weighted sentiment analysis (`/recommendations`).
* **Data Collection:** Includes logic (`src/news_collector.py`) to fetch relevant news articles for the monitored stocks.
* **Sentiment Analysis:** Performs sentiment analysis (positive, negative, neutral scoring) on collected news content using a FinBERT model (via `src/sentiment_analyser.py`).
* **Collection Scheduling:** Includes logic (`src/collection_scheduler.py`) to automatically run the data collection and its analysis every hour.
* **Data Storage:** Stores the stock list, processed news/sentiment data, and recommendations in JSON file format within the `data/` directory.
* **Authentication:** Implements basic API key authentication for accessing endpoints.

## Setup & Running Locally

1.  **Prerequisites:** Ensure Python 3.11.4 is installed. (While versions above 3.8 *might* work, 3.11 is the tested and supported version.).
2.  **Clone Repository:** Clone this repository to your local machine.
3.  **Install Dependencies:** Make sure all necessary libraries are installed `pip install -r requirements.txt`
4.  **Run the Server:**
    * **Using Uvicorn (Recommended):** Uvicorn is an ASGI server needed to run FastAPI applications. Adjust host and port as needed. Use `--reload` for automatic code reloading during development.
        `python src\main.py --host 0.0.0.0 --port 8091 --reload`
    This script also starts up the collection scheduling concurrently.
    * **Using start.bat (Windows):** If you are on Windows, you can execute the provided batch file.

The API server should now be running, typically accessible at `http://localhost:8091` or `http://<your-ip>:8091`.

## Testing

To ensure the backend components function correctly, run the automated tests:
Execute the main test runner script:`python tests/main_tester.py`
This will run all tests covering the API endpoints, sentiment analyzer, and utility functions.

## Deployment (Docker)

To deploy the backend service using Docker:

1.  **Prerequisites:** Ensure Docker is installed and running on your deployment server.
2.  **Build the Docker Image:** Create the image using the `Dockerfile`: `docker build -t news-collector-app .`
3.  **Check Port Availability:** Ensure the target port (e.g., 8091) is not already in use on the host machine.
    * **Windows:** `netstat -ano | findstr :8091`
    * **Linux/macOS:** `sudo lsof -i :8091` or `ss -tulnp | grep 8091`
4.  **Free Port (If Necessary):** If the port is occupied, identify the Process ID (PID) from the previous command and terminate the process.
    * **Windows:** `taskkill /F /PID <PID>`
    * **Linux/macOS:** `sudo kill -9 <PID>`
5.  **Run the Docker Container:** Start the container, mapping the host port (e.g., 8091) to the container port (which should also be 8091, assuming the `Dockerfile` exposes it). Add `-d` to run in detached mode (in the background).
    `docker run -d -p 8091:8091 news-collector-app`
    The backend service should now be running inside the Docker container and accessible via the host machine's IP address on port 8091.

## Related Projects

You can also find the frontend related to this project at https://github.com/kristofmester007/stockmagnifier-frontend.

A deployed version of this project is available at: https://dbatx57diay0.cloudfront.net

## Copyright

Copyright © 2025 Kristóf Szabó. Developed as a BSc Thesis project at Eötvös Loránd University (ELTE).