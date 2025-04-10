import asyncio
import subprocess
import uvicorn
import os
import argparse

async def run_scheduler():
    """Starts the collection_scheduler.py script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scheduler_path = os.path.join(script_dir, "collection_scheduler.py")
    await asyncio.create_subprocess_exec("python", scheduler_path)

async def run_api(host: str, port: int, reload: bool):
    """Runs the uvicorn server."""
    config = uvicorn.Config("api_handler:app", host=host, port=port, reload=reload)
    server = uvicorn.Server(config)
    await server.serve()

async def main(host: str, port: int, reload: bool):
    """Runs both the scheduler and the API concurrently."""
    await asyncio.gather(
        run_scheduler(),
        run_api(host, port, reload)
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the StockMagnifier API and scheduler.")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the API server to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8091, help="Port to listen on (default: 8091)")
    parser.add_argument("--reload", action='store_true', help="Enable auto-reloading (default: False)")
    args = parser.parse_args()

    asyncio.run(main(args.host, args.port, args.reload))