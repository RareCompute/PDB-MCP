import pytest
import httpx
from datetime import datetime, timezone
from respx import MockRouter

from mcp_pdb.adapter.pdb_client import PDBClient
from mcp_pdb.schemas import StructureDataset, ChainInfo, LigandDataset, Provenance
from mcp_pdb.exceptions import PDBAPIError, NetworkError
from mcp_pdb.config import PDB_API_BASE_URL

@pytest.fixture
def client() -> PDBClient:
    return PDBClient()

@pytest.mark.asyncio
async def test_get_structure_summary_success(client: PDBClient, respx_router: MockRouter):
    pdb_id = "1ehz"
    api_url = f"{PDB_API_BASE_URL}/rest/v1/core/entry/{pdb_id}"

    mock_api_response = {
        "struct": {"title": "Human Insulin"},
        "exptl": [{"method": "X-RAY DIFFRACTION"}],
        "refine": [{"ls_d_res_high": "1.5"}],
        "polymer_entities": [
            {
                "entity_poly": {"pdbx_strand_id": "A,B"},
                "rcsb_entity_source_organism": [{"ncbi_scientific_name": "Homo sapiens"}],
                "rcsb_polymer_entity_container_identifiers": {"auth_asym_ids": ["A", "B"]},
                "entity_poly": {"rcsb_sample_sequence_length": 21}
            }
        ],
        "nonpolymer_entities": [
            {
                "nonpolymer_comp": {"chem_comp": {"id": "ZN", "name": "ZINC ION"}},
                "rcsb_nonpolymer_entity_container_identifiers": {"instance_count": 2}
            }
        ]
    }

    respx_router.get(api_url).mock(return_value=httpx.Response(200, json=mock_api_response))

    summary = await client.get_structure_summary(pdb_id)

    assert isinstance(summary, StructureDataset)
    assert summary.pdb_id == pdb_id
    assert summary.title == "Human Insulin"
    assert summary.method == "X-RAY DIFFRACTION"
    assert summary.resolution == 1.5
    assert len(summary.chains) > 0
    assert summary.chains[0].chain_id == "A" # or check based on your processing logic
    assert summary.chains[0].sequence_length == 21
    assert summary.chains[0].organism == "Homo sapiens"
    assert len(summary.ligands) > 0
    assert summary.ligands[0].chem_id == "ZN"
    assert summary.ligands[0].name == "ZINC ION"
    assert summary.ligands[0].count == 2
    assert summary.provenance.source == "RCSB PDB"
    assert summary.provenance.api_url == api_url
    assert isinstance(summary.provenance.retrieved, datetime)
    await client.close()

@pytest.mark.asyncio
async def test_get_structure_summary_not_found(client: PDBClient, respx_router: MockRouter):
    pdb_id = "xxxx"
    api_url = f"{PDB_API_BASE_URL}/rest/v1/core/entry/{pdb_id}"
    respx_router.get(api_url).mock(return_value=httpx.Response(404))

    with pytest.raises(PDBAPIError) as excinfo:
        await client.get_structure_summary(pdb_id)
    
    assert excinfo.value.status_code == 404
    assert pdb_id in excinfo.value.message
    await client.close()

@pytest.mark.asyncio
async def test_get_structure_summary_api_error(client: PDBClient, respx_router: MockRouter):
    pdb_id = "1ehz"
    api_url = f"{PDB_API_BASE_URL}/rest/v1/core/entry/{pdb_id}"
    respx_router.get(api_url).mock(return_value=httpx.Response(500, text="Internal Server Error"))

    with pytest.raises(PDBAPIError) as excinfo:
        await client.get_structure_summary(pdb_id)

    assert excinfo.value.status_code == 500
    assert "Internal Server Error" in excinfo.value.message
    await client.close()

@pytest.mark.asyncio
async def test_get_structure_summary_network_error(client: PDBClient, respx_router: MockRouter):
    pdb_id = "1ehz"
    api_url = f"{PDB_API_BASE_URL}/rest/v1/core/entry/{pdb_id}"
    respx_router.get(api_url).mock(side_effect=httpx.ConnectError("Connection failed"))

    with pytest.raises(NetworkError) as excinfo:
        await client.get_structure_summary(pdb_id)

    assert "Connection failed" in excinfo.value.message
    await client.close()
