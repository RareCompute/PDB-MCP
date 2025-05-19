import pytest
# import json # No longer needed for embedded sample_pdb_data_json
# from pathlib import Path # No longer needed for embedded sample_pdb_data_json
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_pdb.processing.dataset_builder import build_structure_context, cache as dataset_builder_cache
from mcp_pdb.schemas import StructureDataset
from mcp_pdb.adapter.pdb_client import PDBClient
from mcp_pdb.exceptions import PDBAPIError, DataValidationError

# Fixture path removed as sample_pdb_data_json is now embedded
@pytest.fixture
def sample_pdb_data_json() -> dict: # No longer takes fixture_path
    # Data embedded directly
    return {
      "pdb_id": "1XYZ",
      "entry_title": "Crystal structure of a test protein",
      "experimental_method": "X-RAY DIFFRACTION",
      "resolution": 2.0,
      "release_date": "2024-01-01",
      "authors": ["Test, A. B."],
      "revisions": [
        {
          "revision_date": "2024-01-01",
          "major_revision": 1,
          "minor_revision": 0
        }
      ],
      "chains": [
        {
          "chain_id": "A",
          "entity_id": 1,
          "auth_asym_id": "A",
          "molecule_name": "Test Protein Chain A",
          "molecule_type": "Polypeptide(L)",
          "sequence_length": 100
        }
      ],
      "ligands": [
        {
          "ligand_id": "TST",
          "chain_id": "A",
          "name": "TEST LIGAND",
          "formula": "C10 H20 N2 O2",
          "molecular_weight": 200.27,
          "number_of_instances": 1
        }
      ],
      "provenance": {
        "source": "RCSB PDB API (mocked)",
        "retrieved_at": "2024-05-19T12:00:00Z"
      }
    }

@pytest.fixture
def sample_pdb_dataset(sample_pdb_data_json: dict) -> StructureDataset:
    return StructureDataset(**sample_pdb_data_json)

@pytest.fixture
def mock_pdb_client() -> PDBClient:
    client = AsyncMock(spec=PDBClient)
    return client

@pytest.fixture(autouse=True)
def clear_builder_cache_before_each_test():
    # Ensure a clean cache for each test that uses the module-level cache
    dataset_builder_cache.clear()
    yield
    dataset_builder_cache.clear()

@pytest.mark.asyncio
async def test_build_structure_context_cache_miss(mock_pdb_client: PDBClient, sample_pdb_dataset: StructureDataset):
    pdb_id = "1XYZ"
    mock_pdb_client.get_structure_summary = AsyncMock(return_value=sample_pdb_dataset)

    # First call: cache miss, client is called
    result = await build_structure_context(pdb_id, mock_pdb_client)
    
    assert result == sample_pdb_dataset
    mock_pdb_client.get_structure_summary.assert_awaited_once_with(pdb_id)
    assert dataset_builder_cache.get(pdb_id) == sample_pdb_dataset # Check it's cached

@pytest.mark.asyncio
async def test_build_structure_context_cache_hit(mock_pdb_client: PDBClient, sample_pdb_dataset: StructureDataset):
    pdb_id = "1XYZ"
    # Pre-populate cache
    dataset_builder_cache.set(pdb_id, sample_pdb_dataset)
    mock_pdb_client.get_structure_summary = AsyncMock(return_value=sample_pdb_dataset) # Should not be called

    # Second call: cache hit
    result = await build_structure_context(pdb_id, mock_pdb_client)

    assert result == sample_pdb_dataset
    mock_pdb_client.get_structure_summary.assert_not_awaited() # Client should not be called

@pytest.mark.asyncio
async def test_build_structure_context_api_error(mock_pdb_client: PDBClient):
    pdb_id = "ERROR1"
    mock_pdb_client.get_structure_summary = AsyncMock(side_effect=PDBAPIError("API call failed", status_code=500))

    with pytest.raises(PDBAPIError):
        await build_structure_context(pdb_id, mock_pdb_client)
    
    assert dataset_builder_cache.get(pdb_id) is None # Nothing should be cached on error

@pytest.mark.asyncio
async def test_build_structure_context_invalid_data_in_cache(mock_pdb_client: PDBClient, sample_pdb_dataset: StructureDataset):
    pdb_id = "INVALIDCACHE"
    # Put something non-StructureDataset into the cache
    dataset_builder_cache.set(pdb_id, {"some": "invalid_data"})
    
    mock_pdb_client.get_structure_summary = AsyncMock(return_value=sample_pdb_dataset)

    # Call should detect invalid cache, delete it, and fetch fresh data
    result = await build_structure_context(pdb_id, mock_pdb_client)

    assert result == sample_pdb_dataset
    mock_pdb_client.get_structure_summary.assert_awaited_once_with(pdb_id)
    assert dataset_builder_cache.get(pdb_id) == sample_pdb_dataset # Fresh data should now be cached

@pytest.mark.asyncio
async def test_build_structure_context_pdb_client_returns_none(mock_pdb_client: PDBClient):
    pdb_id = "NONEPDB"
    # Simulate PDBClient returning None (though it's typed to return StructureDataset or raise error)
    mock_pdb_client.get_structure_summary = AsyncMock(return_value=None)

    result = await build_structure_context(pdb_id, mock_pdb_client)

    assert result is None
    mock_pdb_client.get_structure_summary.assert_awaited_once_with(pdb_id)
    assert dataset_builder_cache.get(pdb_id) is None # If client returns None, None is cached (or not, depending on set logic)
                                                # Current LRUCache.set will store None
                                                # Current build_structure_context logic caches if structure_data is not None
                                                # So, it should NOT cache None here.
    # Re-check after confirming set logic for None:
    # build_structure_context has: `if structure_data: cache.set(pdb_id, structure_data)`
    # So, if structure_data is None, it will not be cached.
    assert dataset_builder_cache.get(pdb_id) is None
