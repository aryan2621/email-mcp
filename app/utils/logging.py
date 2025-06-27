import logging
import os
from datetime import datetime

def setup_logging():
    """Configure file-only logging to avoid JSON-RPC interference."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f'{log_dir}/gmail_mcp_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_filename)]
    )
    return logging.getLogger('gmail-mcp') 