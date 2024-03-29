import os
import logging

read_local_mock_articles = os.getenv("READ_LOCAL_MOCK_ARTICLES", 'false').lower() == 'true'
use_mul_process = os.getenv("USE_MUL_PROCESS", 'false').lower() == 'true'
num_processes = int(os.getenv("NUM_PROCESSES", "5"))
mock_data_file_path = os.getenv("MOCK_DATA_FILE_PATH", "mock_data/mock_data.json")
articles_dir = os.getenv("ARTICLES_DIR", "articles")
num_pages = int(os.getenv("NUM_PAGES", "3"))
log_level = getattr(logging, os.getenv("LOG_LEVEL", 'INFO'))
flask_host = os.getenv("HOST", "0.0.0.0")
flask_port = int(os.getenv("PORT", "6060"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

