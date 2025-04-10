from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio

script_dir = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]
)

API_KEY = "twetArxt5425AgesR"  # IMPORTANT: DO NOT DO THIS IN PRODUCTION!

async def verify_api_key(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/data/{ticker}")
async def get_ticker_news(
    ticker: str = Path(..., title="Stock ticker symbol"),
    api_key: str = Query(..., title="API Key"),
):
    """
    Retrieves news data for a specific stock ticker.
    """
    await verify_api_key(api_key)

    
    filepath = os.path.join(script_dir,"..", "data","news_data", f"{ticker.lower()}_news.json")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="News data not found for this ticker")

    try:
        loop = asyncio.get_event_loop()
        with open(filepath, "r") as f:
            content = await loop.run_in_executor(None, f.read)
        data = json.loads(content)
        return data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format in news data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/stock")
async def get_stock_list(api_key: str = Query(..., title="API Key")):
    """
    Retrieves the stock list from stocklist.json.
    """
    await verify_api_key(api_key)

    filepath = os.path.join(script_dir, "..", "data", "stocklist.json")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Stock list file not found")

    try:
        loop = asyncio.get_event_loop()
        with open(filepath, "r") as f:
            content = await loop.run_in_executor(None, f.read)
        data = json.loads(content)
        return data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format in stock list")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/recommendations")
async def get_recommendations(api_key: str = Query(..., title="API Key")):
    """
    Retrieves the recommendations from recommendations.json.
    """
    await verify_api_key(api_key)

    filepath = os.path.join(script_dir, "..", "data", "recommendations.json")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Recommendations file not found")

    try:
        loop = asyncio.get_event_loop()
        with open(filepath, "r") as f:
            content = await loop.run_in_executor(None, f.read)
        data = json.loads(content)
        return data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format in stock list")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")