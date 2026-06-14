import time, signal, sys, logging
from sheets import SheetsClient
from main import process_niche

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_agent(once: bool = False):
    def signal_handler(sig, frame): sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    sheets_client = SheetsClient()
    while True:
        for niche in sheets_client.get_niches():
            try: process_niche(niche)
            except Exception as e: logger.error(f"Error: {e}")
            time.sleep(10)
        if once: break
        time.sleep(86400)

if __name__ == "__main__":
    run_agent()
