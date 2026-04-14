# Awesome LLM Apps

## Overview
Awesome LLM Apps is a local-first chat harvesting system designed to extract, process, and store chat messages efficiently. The system utilizes a sovereign architecture, ensuring data integrity and reliability through robust embedding and indexing mechanisms.

## Project Structure
```
awesome-llm-apps
├── data
│   ├── faiss_index        # Directory containing FAISS index files for vector embeddings
│   └── store.db           # SQLite database file for persistent storage
├── src
│   ├── __init__.py        # Marks the directory as a Python package
│   ├── config.py          # Configuration constants (DIM, paths, model names)
│   ├── embedder.py        # Handles chunking and embedding of text
│   ├── harvester.py       # Implements chat harvesting logic using Selenium
│   ├── store.py           # Logic for SQLite database and FAISS index interactions
│   └── utils.py           # Utility functions for data processing and validation
├── tests
│   ├── test_embedder.py   # Unit tests for embedder.py
│   ├── test_harvester.py  # Unit tests for harvester.py
│   └── test_store.py      # Unit tests for store.py
├── main.py                # Entry point for the application
├── pyproject.toml         # Project configuration file
└── requirements.txt       # List of required Python packages
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
   cd awesome-llm-apps
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have the necessary environment for running the Selenium browser automation (e.g., ChromeDriver).

## Usage
To run the application, execute the following command:
```
python main.py
```

## Features
- **Local-First Architecture**: Ensures data sovereignty and integrity.
- **Robust Embedding and Indexing**: Utilizes FAISS for efficient vector storage and querying.
- **Automated Chat Harvesting**: Extracts messages from chat pages and normalizes them for processing.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.