import enum

class SenderEnum(enum.Enum):
    user = "user"
    bot = "bot"

class AuthStatusEnum(enum.Enum):
    success = "success"
    failure = "failure"

class TransactionStatusEnum(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"