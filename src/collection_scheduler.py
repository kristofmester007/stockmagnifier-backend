import time
import schedule
import subprocess
import os

def run_collector():
    """Runs the collector.py script."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        collector_path = os.path.join(script_dir, "news_collector.py")
        subprocess.run(["python", collector_path], check=True)
        print(f"\n\n --- {time.strftime('%Y-%m-%d %H:%M:%S')}:\tCollection executed. --- ")
    except subprocess.CalledProcessError as e:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}:\tError executing news_collector.py: {e}.")
    except FileNotFoundError:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}:\tError: news_collector.py not found in the current directory.")

# Run the collector immediately when the script starts
run_collector()

# Schedule the collector to run every hour
schedule.every().hour.do(run_collector)

print(f"Scheduler started at {time.strftime('%Y-%m-%d %H:%M:%S')}")

while True:
    schedule.run_pending()
    time.sleep(1)