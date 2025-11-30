# flashcards_backend

# Requirements
```bash
$ python -m venv venv
$ .\venv\Scripts\activate
$ pip install -r requirements.txt
```

# Running
```bash
$ uvicorn app.main:app --reload
```

# Database Postgres
```bash
$ docker compose up -d # Starts the database container
$ docker compose down # Stops the database container
$ docker compose logs db # Shows logs for the database container
$ docker compose down -v # Deletes ALL the data in the database
```

The API will be available at http://127.0.0.1:8000