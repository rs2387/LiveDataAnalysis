# LiveDataAnalysis

A Python application for real-time data ingestion, sentiment analysis, and visualisation. The project fetches live and historical data via an API and WebSocket, performs sentiment scoring using a trained vocabulary model, stores results in a local SQLite database, and renders dynamic graphs for analysis.

---

## Features

- **Live data fetching** — Pulls data in real time via a configurable API and WebSocket client (`api.py`)
- **Sentiment analysis** — Classifies text using a custom vocabulary-based model trained on `vocabTraining.csv`
- **Persistent storage** — Saves results to a local SQLite database (`database.db`) managed by `database.py`
- **Data visualisation** — Generates graphs and charts from stored results using `graph.py`
- **Modular architecture** — Clean separation of concerns across API, database, sentiment, and visualisation layers

---

## Project Structure

```
LiveDataAnalysis/
├── app.py               # Main application entry point
├── api.py               # API client for fetching live data
├── database.py          # Database setup and query helpers
├── database.db          # SQLite database (auto-generated)
├── sentiment.py         # Sentiment analysis logic
├── testSentiment.py     # Unit tests for sentiment module
├── graph.py             # Graphing and visualisation utilities
├── vocabTraining.csv    # Training vocabulary for the sentiment model
├── storage/             # Directory for storing output files
└── .gitignore
```

---

## Getting Started

### Prerequisites

- Python 3.2+
- pip

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/rs2387/LiveDataAnalysis.git
   cd LiveDataAnalysis
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```



### Running the App

```bash
python app.py
```

This will start the data pipeline — fetching live data, running sentiment analysis, saving to the database, and generating graphs.

---


## Configuration

API endpoints or data sources can be configured in `api.py`. Update the relevant URL or authentication parameters before running.

---

## How It Works

1. `app.py` orchestrates the pipeline
2. `api.py` fetches live data from an external source
3. `sentiment.py` scores the fetched text using vocabulary trained from `vocabTraining.csv`
4. `database.py` persists the results to `database.db`
5. `graph.py` reads from the database and renders visualisations, saved to `storage/`

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## License

This project does not currently specify a license. Please contact the repository owner for usage permissions.
