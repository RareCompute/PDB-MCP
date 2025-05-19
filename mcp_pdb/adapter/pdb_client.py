# mcp_pdb/adapter/pdb_client.py
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from mcp_pdb.config import PDB_API_BASE_URL
from mcp_pdb.schemas import (
    StructureDataset,
    ChainInfo,
    LigandDataset,
    Provenance,
)
from mcp_pdb.exceptions import (
    PDBClientError,
    PDBAPIError,
    NetworkError
)


class PDBClient:
    def __init__(self, base_url: str = PDB_API_BASE_URL, client: Optional[httpx.AsyncClient] = None):
        self.base_url = base_url.rstrip('/') # Ensure no trailing slash
        self._client = client
        self._created_client = False # Flag to track if this instance created the client

    async def _get_async_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
            self._created_client = True
        return self._client

    async def close(self):
        """Closes the underlying httpx.AsyncClient if it was created by this instance."""
        if self._client and self._created_client:
            await self._client.aclose()
            self._client = None
            self._created_client = False

    async def get_structure_summary(self, pdb_id: str) -> StructureDataset:
        """
        Fetches a summary for a given PDB ID from the RCSB PDB Data API.
        """
        client = await self._get_async_client()
        # RCSB PDB API endpoint for core entry data
        api_path = f"/rest/v1/core/entry/{pdb_id}"
        full_api_url = f"{self.base_url}{api_path}"

        try:
            response = await client.get(api_path)
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise PDBAPIError(
                    pdb_id=pdb_id,
                    status_code=404,
                    detail=f"PDB entry '{pdb_id}' not found at {full_api_url}."
                ) from e
            else:
                raise PDBAPIError(
                    pdb_id=pdb_id,
                    status_code=e.response.status_code,
                    detail=f"PDB API request failed with status {e.response.status_code} for entry '{pdb_id}' at {full_api_url}. Response: {e.response.text}"
                ) from e
        except httpx.RequestError as e:
            # Covers network errors like DNS failure, connection refused, timeouts, etc.
            raise NetworkError(
                message=f"Network error while requesting PDB entry '{pdb_id}' from {full_api_url}: {str(e)}"
            ) from e
        except Exception as e:
            # Fallback for any other unexpected errors during the request or initial processing
            raise PDBClientError(
                message=f"An unexpected error occurred in PDBClient for PDB ID '{pdb_id}' at {full_api_url}: {str(e)}"
            ) from e

        data = response.json()

        provenance = Provenance(
            source="RCSB PDB",
            retrieved=datetime.now(timezone.utc),
            api_url=full_api_url
        )

        title = data.get("struct", {}).get("title", "N/A")
        method_list = data.get("exptl", [])
        method = method_list[0].get("method", "N/A") if method_list else "N/A"
        
        resolution = None
        refine_list = data.get("refine", [])
        if refine_list:
            res_val = refine_list[0].get("ls_d_res_high")
            if res_val is not None:
                try:
                    resolution = float(res_val)
                except (ValueError, TypeError):
                    resolution = None

        chains_data: List[ChainInfo] = []
        processed_chain_ids = set()
        polymer_entities = data.get("polymer_entities", [])
        for entity in polymer_entities:
            source_organisms = entity.get("rcsb_entity_source_organism", [])
            organism_name = source_organisms[0].get("ncbi_scientific_name") if source_organisms else None
            
            seq_length = entity.get("entity_poly", {}).get("rcsb_sample_sequence_length", 0)
            if seq_length == 0:
                seq_code = entity.get("entity_poly", {}).get("pdbx_seq_one_letter_code_can")
                if seq_code:
                    seq_length = len(seq_code)

            chain_id_str = entity.get("entity_poly", {}).get("pdbx_strand_id", "") # Comma-separated e.g., A,B
            auth_asym_ids_from_entity_container = entity.get("rcsb_polymer_entity_container_identifiers", {}).get("auth_asym_ids", [])

            current_entity_chain_ids = []
            if chain_id_str:
                current_entity_chain_ids.extend([c.strip() for c in chain_id_str.split(',') if c.strip()])
            if auth_asym_ids_from_entity_container:
                 current_entity_chain_ids.extend(auth_asym_ids_from_entity_container)
            
            unique_current_entity_chain_ids = sorted(list(set(current_entity_chain_ids)))

            for chain_id_val in unique_current_entity_chain_ids:
                if chain_id_val and chain_id_val not in processed_chain_ids:
                    chains_data.append(
                        ChainInfo(
                            chain_id=str(chain_id_val)[:2],
                            sequence_length=max(1, seq_length), # Ensure gt=0
                            organism=organism_name,
                        )
                    )
                    processed_chain_ids.add(chain_id_val)
        
        ligands_data: List[LigandDataset] = []
        nonpolymer_entities = data.get("nonpolymer_entities", [])
        for entity in nonpolymer_entities:
            chem_id = entity.get("nonpolymer_comp", {}).get("chem_comp", {}).get("id")
            name = entity.get("nonpolymer_comp", {}).get("chem_comp", {}).get("name")
            if not name:
                name = entity.get("pdbx_entity_nonpoly", {}).get("name", "N/A")

            count = entity.get("rcsb_nonpolymer_entity_container_identifiers", {}).get("instance_count", 1)
            count = max(1, count) # Ensure ge=1

            if chem_id:
                ligands_data.append(
                    LigandDataset(
                        chem_id=str(chem_id)[:3],
                        name=str(name),
                        count=count,
                    )
                )

        return StructureDataset(
            pdb_id=str(pdb_id),
            title=str(title),
            method=str(method),
            resolution=resolution,
            chains=chains_data,
            ligands=ligands_data,
            provenance=provenance,
        )

async def main_test(pdb_id_to_test: str):
    client = PDBClient()
    print(f"Fetching summary for PDB ID: {pdb_id_to_test}")
    try:
        summary = await client.get_structure_summary(pdb_id_to_test)
        print("\n--- Structure Summary ---")
        print(f"PDB ID: {summary.pdb_id}")
        print(f"Title: {summary.title}")
        print(f"Method: {summary.method}")
        print(f"Resolution: {summary.resolution} Å")
        print("\nChains:")
        for chain in summary.chains:
            print(f"  ID: {chain.chain_id}, Length: {chain.sequence_length}, Organism: {chain.organism}")
        print("\nLigands:")
        for ligand in summary.ligands:
            print(f"  ID: {ligand.chem_id}, Name: {ligand.name}, Count: {ligand.count}")
        print("\nProvenance:")
        print(f"  Source: {summary.provenance.source}")
        print(f"  Retrieved: {summary.provenance.retrieved.isoformat()}")
        print(f"  API URL: {summary.provenance.api_url}")
    except PDBClientError as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    import asyncio
    # Test with: python -m mcp_pdb.adapter.pdb_client
    # Example PDB IDs: 1ehz (Human Insulin), 1tup (Lysozyme), 
    # 6wlc (SARS-CoV-2 main protease with inhibitor N3)
    # 4hhb (Hemoglobin)
    test_pdb_id = "1ehz"
    asyncio.run(main_test(test_pdb_id))
