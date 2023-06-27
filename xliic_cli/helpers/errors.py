import json


class TaskError(Exception):
    def __init__(self, message: str, is_network_error: bool = False):
        super().__init__(message)
        self.is_network_error = is_network_error


class ScanError(Exception):
    def __init__(self, message: str, details: str):
        super().__init__(message)
        self.details = details

    def __str__(self):
        error_details = f". Details: {self.details}" if self.details is not None else ""
        try:
            answer = json.loads(self.details)
            if "message" in answer and answer["message"] == "invalid session":
                error_details = ". Invalid session: please check your API token."
        except json.JSONDecodeError:
            pass
        return f"Error in scan process: {str(self.args[0])}{error_details}"
