class ConflictIntegrityError(Exception):
    def __init__(
        self,
        message="This obj is used in other models and cannot be deleted.",
    ):
        super().__init__(message)
