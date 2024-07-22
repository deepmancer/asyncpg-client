from typing import Optional

class PGConnectionError(ConnectionError):
    def __init__(self, url: str, message: Optional[str] = None,):
        base_message = f"Error: Failed to connect to postgres at {url}"
        message = f"Details: {message}"
        final_message = f"{base_message}\n{message}"
        super().__init__(final_message)

class PGSessionCreationError(Exception):
    def __init__(self, url: str, message: Optional[str] = None):
        base_message = f"Error: Failed to create a postgres session at {url}"
        message = f"Details: {message}"
        final_message = f"{base_message}\n{message}"
        super().__init__(final_message)
        
class PGEngineInitializationError(Exception):
    def __init__(self, url: str, message: Optional[str] = None):
        base_message = f"Error: Failed to create an async engine for postgres at {url}"
        message = f"Details: {message}"
        final_message = f"{base_message}\n{message}"
        super().__init__(final_message)
