import pytest
from fastapi.testclient import TestClient
from respx import MockRouter # Renamed from 'Router' to 'MockRouter' in newer respx versions
import httpx

from mcp_pdb.main import app
from mcp_pdb.schemas import StructureDataset
from mcp_pdb.config import PDB_API_URL
from mcp_pdb.processing.dataset_builder import cache as dataset_builder_cache # To check cache state

# Sample data, similar to what's in test_dataset_builder.py
# In a real-world scenario with many fixtures, you might share them via conftest.py
SAMPLE_PDB_ID_SUCCESS = "1XYZ"
SAMPLE_PDB_DATA_SUCCESS = {
    "pdb_id": SAMPLE_PDB_ID_SUCCESS,
    "entry_title": "Crystal structure of a test protein",
    "experimental_method": "X-RAY DIFFRACTION",
    "resolution": 2.0,
    "release_date": "2024-01-01",
    "authors": ["Test, A. B."],
    "revisions": [{"revision_date": "2024-01-01", "major_revision": 1, "minor_revision": 0}],
    "chains": [{
        "chain_id": "A", "entity_id": 1, "auth_asym_id": "A", 
        "molecule_name": "Test Protein Chain A", "molecule_type": "Polypeptide(L)", "sequence_length": 100
    }],
    "ligands": [{
        "ligand_id": "TST", "chain_id": "A", "name": "TEST LIGAND", "formula": "C10 H20 N2 O2", 
        "molecular_weight": 200.27, "number_of_instances": 1
    }],
    "provenance": {"source": "RCSB PDB API (mocked)", "retrieved_at": "2024-05-19T12:00:00Z"}
}

SAMPLE_PDB_ID_NOT_FOUND = "404X"

@pytest.fixture(scope="module")
def client() -> TestClient:
    # Using 'with TestClient(app) as c:' ensures lifespan events are run.
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def clear_cache_and_mock_api():
    dataset_builder_cache.clear()
    # Ensure respx is active for all tests in this file if needed, or manage per test.
    # Here, we'll manage it per test that needs external calls mocked.
    yield
    dataset_builder_cache.clear()

@pytest.mark.respx(base_url=PDB_API_URL)
def test_get_structure_success_and_cache(client: TestClient, respx_mock: MockRouter):
    # Mock the PDB API call for the first request
    respx_mock.get(f"/summary/{SAMPLE_PDB_ID_SUCCESS}").mock(
        return_value=httpx.Response(200, json=SAMPLE_PDB_DATA_SUCCESS)
    )

    # --- First call: API should be called, data cached ---
    response1 = client.get(f"/structure/{SAMPLE_PDB_ID_SUCCESS}")
    assert response1.status_code == 200
    response_data1 = response1.json()
    # Validate against the Pydantic model if necessary, or check key fields
    assert response_data1["pdb_id"] == SAMPLE_PDB_ID_SUCCESS
    assert response_data1["entry_title"] == SAMPLE_PDB_DATA_SUCCESS["entry_title"]
    # Check that PDB API was called
    assert respx_mock.get(f"/summary/{SAMPLE_PDB_ID_SUCCESS}").called
    assert respx_mock.get(f"/summary/{SAMPLE_PDB_ID_SUCCESS}").call_count == 1

    # Check that data is in cache
    cached_item = dataset_builder_cache.get(SAMPLE_PDB_ID_SUCCESS)
    assert cached_item is not None
    assert isinstance(cached_item, StructureDataset)
    assert cached_item.pdb_id == SAMPLE_PDB_ID_SUCCESS

    # --- Second call: API should NOT be called, data from cache ---
    response2 = client.get(f"/structure/{SAMPLE_PDB_ID_SUCCESS}")
    assert response2.status_code == 200
    response_data2 = response2.json()
    assert response_data2["pdb_id"] == SAMPLE_PDB_ID_SUCCESS
    
    # Assert that the PDB API mock was NOT called again (call_count is still 1)
    assert respx_mock.get(f"/summary/{SAMPLE_PDB_ID_SUCCESS}").call_count == 1

@pytest.mark.respx(base_url=PDB_API_URL)
def test_get_structure_not_found(client: TestClient, respx_mock: MockRouter):
    # Mock the PDB API call to return a 404
    respx_mock.get(f"/summary/{SAMPLE_PDB_ID_NOT_FOUND}").mock(
        return_value=httpx.Response(404, json={"message": "Entry not found"})
    )

    response = client.get(f"/structure/{SAMPLE_PDB_ID_NOT_FOUND}")
    assert response.status_code == 404 # Our app's PDBAPIError handler for 404
    response_data = response.json()
    assert "message" in response_data
    assert (SAMPLE_PDB_ID_NOT_FOUND in response_data.get("message", "") or
            SAMPLE_PDB_ID_NOT_FOUND in response_data.get("detail", ""))

    # Check that PDB API was called
    assert respx_mock.get(f"/summary/{SAMPLE_PDB_ID_NOT_FOUND}").called

    # Check that nothing was cached for the 404 ID
    assert dataset_builder_cache.get(SAMPLE_PDB_ID_NOT_FOUND) is None

@pytest.mark.respx(base_url=PDB_API_URL)
def test_get_structure_pdb_api_error_500(client: TestClient, respx_mock: MockRouter):
    PDB_ID_API_ERROR = "500ERR"
    # Mock the PDB API call to return a 500
    respx_mock.get(f"/summary/{PDB_ID_API_ERROR}").mock(
        return_value=httpx.Response(500, json={"message": "Internal server error on PDB API"})
    )

    response = client.get(f"/structure/{PDB_ID_API_ERROR}")
    # Our app's PDBAPIError handler for >= 500 defaults to 502 Bad Gateway
    assert response.status_code == 502 
    response_data = response.json()
    assert "message" in response_data
    assert "Error communicating with the PDB API" in response_data["message"]

    # Check that PDB API was called
    assert respx_mock.get(f"/summary/{PDB_ID_API_ERROR}").called

    # Check that nothing was cached
    assert dataset_builder_cache.get(PDB_ID_API_ERROR) is None
