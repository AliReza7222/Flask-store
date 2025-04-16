class ConflictIntegrityError(Exception):
    def __init__(self, message="This product is used in orders and cannot be deleted."):
        super().__init__(message)
