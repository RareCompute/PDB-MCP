class MCPError(Exception):
    """Base exception class for PDB-MCP application-specific errors."""
    def __init__(self, message: str = "An unspecified error occurred in the PDB-MCP application."):
        self.message = message
        super().__init__(self.message)

class PDBClientError(MCPError):
    """Base exception for errors originating from the PDBClient."""
    def __init__(self, message: str = "An error occurred in the PDB client."):
        super().__init__(message)

class PDBAPIError(PDBClientError):
    """Raised when the PDB API returns an error or unexpected response."""
    def __init__(self, pdb_id: str = None, status_code: int = None, detail: str = "Error interacting with PDB API."):
        self.pdb_id = pdb_id
        self.status_code = status_code
        message = f"PDB API error for ID '{pdb_id}' (Status: {status_code}): {detail}" if pdb_id and status_code else detail
        super().__init__(message)

class NetworkError(PDBClientError):
    """Raised for network-related issues (e.g., connection timeouts, DNS failures)."""
    def __init__(self, message: str = "A network error occurred."):
        super().__init__(message)

class ConfigurationError(MCPError):
    """Raised when there is a misconfiguration in the application settings."""
    def __init__(self, message: str = "Application configuration error."):
        super().__init__(message)

class DataValidationError(MCPError):
    """Raised when data fails validation checks (e.g., Pydantic model validation)."""
    def __init__(self, message: str = "Data validation error.", errors: list = None):
        self.errors = errors if errors is not None else []
        super().__init__(message)
