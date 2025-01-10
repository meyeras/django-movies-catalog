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

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software under the terms of the license. See the full license text below:

```
MIT License

Copyright (c) 2024 <Your Name>

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

