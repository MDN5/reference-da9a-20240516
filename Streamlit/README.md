# Streamlit Application

This simplified Streamlit application serves as a basic learning tool for building Streamlit apps, offering functionality for both Gemini and OpenAI services.

## Getting Started

### Prerequisites

- [Anaconda](https://www.anaconda.com/products/distribution)
- [Python](https://www.python.org/downloads/) (>= 3.12)

### Installation

1. Create a new virtual environment and activate it:

   ```
   conda create -p ./venv python=3.12
   conda activate ./venv
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Create a config.yaml file in the same directory as your Python script with the following content:

   ```
   api:
   active: OpenAI  # Change to "Gemini" to use Gemini
   keys:
      openai: YOUR_OPENAI_API_KEY
      google: YOUR_GOOGLE_API_KEY
   models:
   openai: gpt-4-turbo
   google: gemini-pro
   ```

### Running the Application

```bash
# Eg: streamlit run <filename.py> --server.port 8080
streamlit run app.py --server.port 8080
```

Replace `<filename.py>` with your Python script containing the Streamlit application. Access the application in your web browser at `http://localhost:8080`.
