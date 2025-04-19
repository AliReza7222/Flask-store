# Flask Project

## Installation

**1. Clone the Repository**
```bash
   git clone https://github.com/AliReza7222/mini-flask-store.git
   cd mini-flask-store
```
**2. Install Dependencies**
```bash
pip install -r requirement.txt
```
## Configuration

**Set Environment Variables**
```bash
FLASK_APP=run.py
FLASK_ENV=<development|production>
SECRET_KEY=<your-secret-key>
JWT_SECRET_KEY=<your-jwt-secret-key>
DATABASE_URL=<your-database-url>
```

## Database Migration
```bash
flask db init
flask db migrate -m "Migration message"
flask db upgrade
```


## Create Admin User
```bash
flask create-admin-user
```

## Run Project in Debug Mode
```bash
flask run --debug
```

## Celery

This app comes with Celery.

To run a celery worker:

```bash
celery -A store.celery_worker.celery_app worker --loglevel=info
```

To run a celery beat:

```bash
celery -A store.celery_worker.celery_app beat --loglevel=info
```

To run a celery flower for monitoring:

```bash
celery -A store.celery_worker.celery_app flower
```


## API docs
```bash
http://127.0.0.1:5000/apidocs/
```
