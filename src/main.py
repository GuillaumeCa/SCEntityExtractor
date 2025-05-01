import signal
import sys
from gui import SCEntityExtractorApp
from config import Config
from utils import check_tools

def handle_ctrl_c(sig, frame):
    print("\nCtrl+C detected! Exiting gracefully...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_ctrl_c)

    # Check required tools
    check_tools()

    # Load configuration
    config = Config()
    config.load()

    # Start the application
    app = SCEntityExtractorApp(config)
    app.run()

