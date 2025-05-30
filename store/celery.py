from celery import Celery, Task
from flask import Flask


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(
        {
            "broker_url": app.config["CELERY_BROKER_URL"],
            "result_backend": app.config["CELERY_RESULT_BACKEND"],
            "beat_schedule": app.config.get("CELERY_BEAT_SCHEDULE", {}),
        },
    )
    celery_app.set_default()
    celery_app.autodiscover_tasks(["store"])
    app.extensions["celery"] = celery_app
    return celery_app
