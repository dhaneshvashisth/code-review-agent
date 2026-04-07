class ReviewException(Exception):
    def __init__(self, message: str, review_id: str | None = None):
        self.message = message
        self.review_id = review_id
        super().__init__(message)

class AgentException(Exception):
    def __init__(self, message: str, agent_name: str, review_id: str | None = None):
        self.message = message
        self.agent_name = agent_name
        self.review_id = review_id
        super().__init__(message)

class DatabaseException(Exception):
    def __init__(self, message: str, operation: str):
        self.message = message
        self.operation = operation
        super().__init__(message)

class LLMException(Exception):
    def __init__(self, message: str, agent_name: str):
        self.message = message
        self.agent_name = agent_name
        super().__init__(message)