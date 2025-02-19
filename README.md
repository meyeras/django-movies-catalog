# Movies Catalog

Welcome to the **Movies Catalog** project! This Django application is designed to manage a catalog of movies. It includes features for populating the database with sample data, cleaning up the database, and managing user access through the Django admin panel.

---

## Table of Contents
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Run the Development Server](#run-the-development-server)
  - [Create a Superuser](#create-a-superuser)
  - [Populate the Database](#populate-the-database)
  - [Clean Up the Database](#clean-up-the-database)
  - [Movies Catalog - Django REST API](#-movies-catalog---django-rest-api)
  - [Deployment options](#-deployment-options)
- [License](#license)

---

## Setup Instructions

### Prerequisites
Before setting up the project, ensure you have the following installed:
- Python 3.8+
- pip (Python package manager)
- virtualenv (optional but recommended)

### Installation
1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv env
   ```

3. **Activate the Virtual Environment:**
   - On Windows:
     ```bash
     .\env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source env/bin/activate
     ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply Migrations:**
   ```bash
   python manage.py migrate
   ```

---

## Usage

### Run the Development Server
Start the Django development server:
```bash
python manage.py runserver
```
Access the application in your browser at `http://127.0.0.1:8000/`.


### Create a Superuser
To manage the application via the Django admin panel, create a superuser:
```bash
python manage.py createsuperuser
```
Follow the prompts to set up your superuser credentials.

### Populate the Database
To populate the database with sample data, use the following command:
```bash
python manage.py movies_sample.json
```
Ensure the `movies_sample.json` file is located in the appropriate directory.

### Clean Up the Database
To remove all entries from the database, run:
```bash
python manage.py clean_db
```
This script will delete all movie-related data from the database.

---
### 🎥 Movies Catalog - Django REST API

This project provides a REST API to manage and browse movies.

#### 📌 API Usage Guide

This project provides a REST API for interacting with the movie catalog. You can explore the available endpoints using **Swagger UI** at:

🔗 **[Swagger API Documentation](http://localhost:8000/swagger/)**

#### 🔑 Authentication & Authorization

1. **Register a New User**  
   - Send a `POST` request to `/api/register/` with your username and password.

2. **Login to Get Access Token**  
   - Send a `POST` request to `/api/login/` with your username and password.  
   - The response will contain an **access token**.
   - 
3**Refresh Access Token**  
   - Send a `POST` request to `/api/token/refresh` with your previous token.  
   - The response will contain an **access token**.

4**Use the Token for Authorization**  
   - Copy the access token and include it in the "Authorize" section of Swagger.  
   - The token should be prefixed with `Bearer ` (including the space).  
   - Example:  
     ```
     Bearer your_access_token_here
     ```

#### 🎬 Available API Endpoints

##### 🔍 Public Endpoints (Require Authentication)
- **Get All Movies**: `GET /api/movies/`
- **Get movies using query**:`GET /api/movies/q=searchTerm`
- **Get Movie Details**: `GET /api/movies/{id}/`

##### 🔧 Admin Endpoints (Require Admin Privileges)
- **Add a New Movie**: `POST /api/movies/`
- **Delete a Movie**: `DELETE /api/movies/{id}/`

Ensure you have the correct authorization token before making requests. Happy coding! 🚀


### 🚀 Deployment Options

This project can be deployed using multiple methods. Below is an option to containerize the application using Docker.

#### 🐳 Deploy with Docker

You can containerize the application using the provided `Dockerfile`. Follow these steps to build and run the application inside a Docker container:

1. **Ensure Docker is Installed**  
   - Install [Docker](https://docs.docker.com/get-docker/) if you haven’t already.

2. **Build the Docker Image**  
   Run the following command in the project root directory (where the `Dockerfile` is located):
   ```sh
   docker build -t movies-catalog .
   ```

3. **Run the Container**  
   Start the application with:
   ```sh
   docker run -p 8000:8000 movies-catalog
   ```
   This will make the application accessible at `http://localhost:8000/`.

4.**Production Deployment**  
   For a production environment, you can provide an environment file to configure the application settings dynamically.

   The application supports the connection to a remote Postgresql database and AWS S3 bucket for media storage.

   The application assumes the server has all the permissions required (IAM Role) to access the database and the remote storage.
   If you are interested in direct access using AWS credentials, add them in .settings.py:

        `AWS_ACCESS_KEY_ID =os.environ.get("AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY")`

   - A sample environment file (`.env.sample`) is included in the project.
   - Copy and rename it to `.env`, then update the necessary variables.
   - You **must** set `ENV=production` to apply production-specific configurations.

   Example `.env` file:
   ```
   ENV=production
   AWS_STORAGE_BUCKET_NAME=your-aws-bucket-name
   AWS_REGION=aws-region
   DB_HOST=postresql host
   
   ```

   Use the `--env-file` flag when running the container:
   ```sh
   docker run --env-file .env -p 8000:8000 movies-catalog
   ```

This ensures that the application is running with the correct production settings. 🎬🐳🚀

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software under the terms of the license. See the full license text below:

```
MIT License

Copyright (c) 2024 Meyer Assayag

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

Happy coding!

