from store.app import create_app
from store.celery import celery_init_app

flask_app = create_app()
celery_app = celery_init_app(flask_app)
