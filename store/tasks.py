from datetime import datetime, timedelta

from celery import shared_task

from store.enums import OrderStatusEnum
from store.extensions import db
from store.order.models import Order


@shared_task(ignore_result=True)
def remove_old_order_pending_status():
    one_hour_ago = datetime.now() - timedelta(hours=1)  # noqa: DTZ005
    Order.query.filter(
        Order.created_at < one_hour_ago,
        Order.status == OrderStatusEnum.PENDING.name,
    ).delete()
    db.session.commit()
