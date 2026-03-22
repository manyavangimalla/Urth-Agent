# Urth Agent

Urth Agent is an environmental risk assessment application that leverages the Model Context Protocol (MCP). It aggregates and analyzes data from various sources (such as NASA FIRMS for wildfires, OpenAQ for air quality, and Open-Meteo for climate risk) to provide real-time environmental insights and risk reports for different regions.

## Features

- **Environmental Risk Assessments**: Generates comprehensive reports on wildfire risks, air quality, and climate conditions.
- **Interactive Map Data**: Provides fire hotspot coordinates for visualization.
- **Historical Trends**: Analyzes and visualizes environmental trends over time.
- **Alert System**: Capability to send automated alerts based on severe environmental conditions.
- **RESTful API**: Flask-based backend serving analysis, map data, and trend information.

## Project Structure

- `run.py`: The main Flask application providing REST APIs for data analysis, map rendering, and trends.
- `alerts.py`: Handles alert sending mechanisms based on assessed risk levels.
- `urth_agent.html`: The frontend user interface for the application.
- `01_basic_server.py`, `mcp` related files: Additional MCP server/client tool implementations.

## Getting Started

### Prerequisites

- Python 3.8+
- An active virtual environment (recommended)
- Environment variables configured in a `.env` file (e.g. for API keys and alerts)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/manyavangimalla/Urth-Agent.git
   cd Urth-Agent
   ```

2. Activate the virtual environment:
   ```bash
   # On Windows
   venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install flask flask-cors mcp
   # Add any other missing requirements if necessary
   ```

### Running the Application

1. If you serve an MCP agent on another port, ensure it is running (the app attempts to connect to `http://127.0.0.1:8000/mcp`).
2. Start the Flask backend:
   ```bash
   python run.py
   ```
   The backend will start running on `http://localhost:5000`.

3. Open `urth_agent.html` in your web browser to access the frontend interface.

## API Endpoints

- `POST /analyze`: Generates a full environmental risk assessment for a specified region.
- `POST /fire-map`: Returns fire hotspot coordinates for rendering on a map.
- `POST /trends`: Retrieves historical environmental trends given coordinates and a timeframe.
- `POST /send-alert`: Triggers an automated alert based on current environmental risk data.

## Technologies Used

- **Python & Flask**: Backend server and API.
- **Model Context Protocol (MCP)**: Tool calling and context delivery.
- **Frontend**: HTML/JS dashboard `urth_agent.html`.
