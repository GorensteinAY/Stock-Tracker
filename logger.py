import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Capture INFO, WARNING, and ERROR messages
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler("app.log"),  # Save logs to file
    ],
)

# Get the logger instance
logger = logging.getLogger("DynamoDBLogger")

# Create a log storage dictionary for tracking logs per ticker
log_storage = {}

class MemoryHandler(logging.Handler):
    """Custom handler to store logs in a dictionary per ticker."""
    def emit(self, record):
        message = self.format(record)
        ticker = getattr(record, "ticker", None)

        if ticker:
            if ticker not in log_storage:
                log_storage[ticker] = []
            log_storage[ticker].append(message)

# Add memory handler
memory_handler = MemoryHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
memory_handler.setFormatter(formatter)
logger.addHandler(memory_handler)

# Function to check if any warnings/errors exist for a specific ticker
def has_warnings_or_errors(ticker):
    if ticker in log_storage:
        for log in log_storage[ticker]:
            if "WARNING" in log or "ERROR" in log:
                return True
    return False
