# Invoice Processing Application

This is an invoice processing application that utilizes the Marker library for PDF conversion and the Ollama client for generating well-formatted tables, summaries, and financial analyses of invoices.

## Prerequisites

Before running the application, make sure you have the following prerequisites installed:

- Python 3.x
- pip (Python package installer)

## Installation

1. Clone the repository:
git clone https://github.com/your-username/invoice-processing.git

2.Install the required dependencies:
pip install -r requirements.txt

Note: The `marker` and `ollama` packages may not be available on the Python Package Index (PyPI) and might require additional setup or installation from specific sources. Please refer to their respective documentation for installation instructions.

## Configuration

The application reads the Ollama host and model information from a YAML configuration file named `config.yaml`. Make sure to update the configuration file with the appropriate values before running the application.

Here's an example of the `config.yaml` file:

```yaml
ollama:
host: 'http://hostname:11434'
model: 'command-r-plus:latest'
```
To run the invoice processing application, use the following command:

streamlit run app.py


