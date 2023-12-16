# Laptop's News Microservice

This is a microservice designed to fetch and serve news articles using FastAPI, Requests, and BeautifulSoup. It provides a simple and efficient way to retrieve news articles about laptops.

## Features

- **FastAPI:** Utilizes the FastAPI framework for creating a fast and modern API with automatic documentation generation.
- **Requests:** Makes HTTP requests to external news sources to fetch the latest articles.
- **Beautiful Soup:** Parses and extracts relevant information from the HTML content of news articles.
- **Asynchronous:** Takes advantage of asynchronous programming for efficient handling of multiple requests.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/LLkaia/news-laptops-ms.git
    cd news-laptops-ms
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:

   - On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

   - On Unix or MacOS:

        ```bash
        source venv/bin/activate
        ```

4. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the FastAPI application:

    ```bash
    python main
    ```

2. Open your web browser and navigate to `http://localhost:8000/docs` to access the Swagger documentation. Here, you can test the different API endpoints and see example requests and responses.

## API Endpoints

- `/news/search`: Search articles about laptops.

    - Example:

        ```
          http://localhost:8000/news/search?find=acer+aspire+7+review
        ```
- `/news/search/{id}`: Show concrete article.

    - Example:

        ```
          http://localhost:8000/news/search/657c1690f253079b6f3ed074
        ```