import logging

from mcp_pdb.adapter.pdb_client import PDBClient
from mcp_pdb.schemas import StructureDataset
from mcp_pdb.utils.cache import LRUCache
# from mcp_pdb.config import settings # If we need more specific config here beyond cache defaults

logger = logging.getLogger(__name__)

# Initialize a global cache instance for this module, or pass it around.
# For simplicity, we'll instantiate it here. Consider dependency injection for more complex apps.
cache = LRUCache() # Uses default CACHE_MAX_SIZE and CACHE_TTL_SECONDS from config

async def build_structure_context(pdb_id: str, pdb_client: PDBClient) -> StructureDataset:
    """
    Builds a structure dataset for a given PDB ID.

    It first checks a local cache for the data. If not found or expired,
    it fetches the data using the PDBClient and then caches the result.

    Args:
        pdb_id: The PDB ID to fetch data for.
        pdb_client: An instance of PDBClient to use for API calls.

    Returns:
        A StructureDataset object.

    Raises:
        PDBClientError (and its subclasses like PDBAPIError, NetworkError) if API call fails.
        DataValidationError if fetched data is invalid (though PDBClient might handle some of this).
    """
    logger.info(f"Building structure context for PDB ID: {pdb_id}")

    # Check cache first
    cached_data = cache.get(pdb_id)
    if cached_data:
        logger.info(f"Cache hit for PDB ID: {pdb_id}")
        if isinstance(cached_data, StructureDataset):
            return cached_data
        else:
            # This case should ideally not happen if only StructureDataset objects are cached.
            logger.warning(f"Cached data for {pdb_id} is not a StructureDataset instance. Fetching again.")
            cache.delete(pdb_id) # Remove invalid entry

    logger.info(f"Cache miss for PDB ID: {pdb_id}. Fetching from PDB API.")
    # If not in cache or expired, fetch from PDB API
    try:
        structure_data = await pdb_client.get_structure_summary(pdb_id)
    except Exception as e:
        logger.error(f"Error fetching data for {pdb_id} from PDB API: {e}")
        raise # Re-raise the exception to be handled by the caller (e.g., FastAPI endpoint)

    # Store in cache
    if structure_data:
        logger.info(f"Storing fetched data for PDB ID: {pdb_id} in cache.")
        cache.set(pdb_id, structure_data)
    
    return structure_data

# Example of how this might be used (for illustration, not part of the module's core logic)
# async def main_example():
#     import httpx
#     async with httpx.AsyncClient() as http_client:
#         client = PDBClient(http_client)
#         try:
#             data_1a2b = await build_structure_context("1a2b", client)
#             print(f"Fetched (1a2b): {data_1a2b.pdb_id} - {data_1a2b.entry_title}")
#             data_1a2b_cached = await build_structure_context("1a2b", client) # Should be from cache
#             print(f"Fetched cached (1a2b): {data_1a2b_cached.pdb_id} - {data_1a2b_cached.entry_title}")
#         except Exception as e:
#             print(f"Error: {e}")

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main_example())
