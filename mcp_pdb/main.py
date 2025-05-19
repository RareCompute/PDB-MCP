# mcp_pdb/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from mcp_pdb.adapter.pdb_client import PDBClient
from mcp_pdb.processing.dataset_builder import build_structure_context
from mcp_pdb.schemas import StructureDataset
from mcp_pdb.config import LOG_LEVEL, APP_VERSION
from mcp_pdb.exceptions import (
    MCPError,
    PDBClientError,
    PDBAPIError,
    NetworkError,
    DataValidationError
)
import logging

# Configure logging
logging.basicConfig(level=LOG_LEVEL.value)
logger = logging.getLogger(__name__)

# Global PDBClient instance, managed by lifespan
pdb_client_instance: PDBClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the PDBClient
    global pdb_client_instance
    logger.info("Initializing PDBClient for the application...")
    pdb_client_instance = PDBClient()
    yield
    # Shutdown: Close the PDBClient
    logger.info("Closing PDBClient...")
    await pdb_client_instance.close()
    logger.info("PDBClient closed.")

app = FastAPI(
    title="PDB Model Context Protocol Server",
    description="Provides PDB data summaries for BioML research agents.",
    version=APP_VERSION,
    lifespan=lifespan
)

# Exception Handlers
@app.exception_handler(PDBAPIError)
async def pdb_api_exception_handler(request: Request, exc: PDBAPIError):
    log_message = f"PDBAPIError for {request.method} {request.url.path}: {exc.message}"
    if exc.pdb_id:
        log_message += f" (PDB ID: {exc.pdb_id})"
    
    if exc.status_code == 404:
        logger.warning(log_message)
        return JSONResponse(
            status_code=404,
            content={"message": f"PDB entry '{exc.pdb_id}' not found.", "detail": exc.message},
        )
    else:
        logger.error(log_message)
        # Use the status code from the exception if it's a server-side error, otherwise default to 502
        response_status_code = exc.status_code if exc.status_code and exc.status_code >= 500 else 502
        return JSONResponse(
            status_code=response_status_code, 
            content={"message": "Error communicating with the PDB API.", "detail": exc.message},
        )

@app.exception_handler(NetworkError)
async def network_exception_handler(request: Request, exc: NetworkError):
    logger.error(f"NetworkError for {request.method} {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=504, # Gateway Timeout
        content={"message": "A network error occurred while connecting to an external service.", "detail": exc.message},
    )

@app.exception_handler(DataValidationError)
async def data_validation_exception_handler(request: Request, exc: DataValidationError):
    logger.warning(f"DataValidationError for {request.method} {request.url.path}: {exc.message} - Errors: {exc.errors}")
    return JSONResponse(
        status_code=422, # Unprocessable Entity
        content={"message": "Data validation error.", "detail": exc.message, "errors": exc.errors},
    )
    
@app.exception_handler(PDBClientError) # Handles PDBClientError if not caught by more specific PDBAPIError or NetworkError
async def pdb_client_exception_handler(request: Request, exc: PDBClientError):
    logger.error(f"PDBClientError for {request.method} {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred within the PDB client.", "detail": exc.message},
    )

@app.exception_handler(MCPError) # Catch-all for any other MCPError subtypes not explicitly handled above
async def mcp_exception_handler(request: Request, exc: MCPError):
    logger.error(f"MCPError for {request.method} {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unspecified application error occurred.", "detail": exc.message},
    )

@app.get("/")
async def read_root():
    return {"message": "Welcome to the PDB-MCP API. See /docs for API documentation."}

@app.get("/structure/{pdb_id}", response_model=StructureDataset)
async def get_structure(pdb_id: str) -> StructureDataset:
    """
    Retrieve a token-efficient context bundle for a given PDB entry ID.
    """
    logger.info(f"Received request for PDB ID: {pdb_id}")
    try:
        summary = await build_structure_context(pdb_id, pdb_client_instance)
        logger.info(f"Successfully retrieved summary for PDB ID: {pdb_id}")
        return summary
    except MCPError as e: 
        # Custom MCPError and its children (PDBAPIError, NetworkError, etc.)
        # will be caught and processed by their specific @app.exception_handler.
        # Logging is handled within those handlers. We just re-raise here.
        raise e 
    except Exception as e: 
        # For any other unexpected errors not part of the MCPError hierarchy.
        logger.exception(f"An unhandled exception occurred while processing PDB ID: {pdb_id} - {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")

if __name__ == "__main__":
    import uvicorn
    # To run: uvicorn mcp_pdb.main:app --reload
    # Then access http://127.0.0.1:8000/docs
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level=LOG_LEVEL.value.lower())
