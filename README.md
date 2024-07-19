# api_version_MC

This project template provides a starting point for building web applications using FastAPI, Uvicorn, and integrating frontend technologies like Tailwind CSS, Jinja templates, SocketIO, SQLAlchemy, and an administrative panel for API management.

## Features

-   **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
-   **Uvicorn**: An ASGI server implementation, using uvloop and httptools.
-   **Tailwind CSS**: Utility-first CSS framework for rapidly building custom designs.
-   **Jinja Templates**: A template engine for Python, used for generating HTML pages.
-   **SocketIO**: Enables real-time, bidirectional, and event-based communication between the browser and the server.
-   **SQLAlchemy**: The Python SQL toolkit and ORM for database access.
-   **Postgres**: Async and sync conection ready for Postgresql
-   **Nodemon**: A utility that will monitor for any changes in your source and automatically restart your server.
-   **Administrative Panel**: A built-in panel for managing API resources and configurations.
-   **Aiohttp**: An async http request package
-   **Extra**: Auto permission generator per endpoint and view, module arquitecture and auto add route following the file and folder content

## Getting Started

### Prerequisites

Ensure you have Python 3.8 or newer installed on your system. Also, make sure Node.js and npm are installed for handling frontend dependencies.

### Installation

1.  Clone the repository:

`git clone https://github.com/TheGuyInTheShell/fastapi-template.git cd your-project-directory` 

2.  Install backend dependencies:

`pip install -r conda.txt` 

3.  Install frontend dependencies:

`npm  install` 

### Running the Project

To run the backend server, execute:

`uvicorn app.main:app --reload` 

To start tailwind compilation, run:

`nodemon` 

This command utilizes Nodemon to watch for changes in your frontend files and automatically rebuild the css.

### Building for Production

Then, serve your FastAPI application with Uvicorn in production mode:

`gunicorn -k uvicorn.workers.UvicornWorker app.main:app` 

Ensure you have Gunicorn installed (`pip install gunicorn`) for serving the application in a production environment.

## Documentation

Refer to the FastAPI documentation for more details on routing, dependencies, security, etc.:  [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)

For integrating Tailwind CSS with Jinja templates, consult the Tailwind CSS documentation:  [https://tailwindcss.com/docs/guides/jinja](https://tailwindcss.com/docs/guides/jinja)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs, enhancements, or new features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
  

