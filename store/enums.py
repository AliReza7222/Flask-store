from enum import Enum


class OrderStatusEnum(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELED = "Canceled"
