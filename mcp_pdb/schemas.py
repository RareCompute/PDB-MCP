"""
mcp_pdb.schemas
~~~~~~~~~~~~~~~~
Typed data models returned to an LLM via MCP JSON-RPC calls.

•  StructureDataset – high-level summary of one PDB entry
•  LigandDataset   – individual ligand or ion bound in that entry
•  Provenance      – where / when the data was fetched
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, constr


# ────────────────────────────────────────────────────────────
# Helper / nested models
# ────────────────────────────────────────────────────────────
class ChainInfo(BaseModel):
    """Minimal per-chain summary to keep token cost low."""

    chain_id: constr(strip_whitespace=True, min_length=1, max_length=2) = Field(
        ...,
        description="Author-provided chain identifier (e.g., 'A')",
        example="A",
    )
    sequence_length: int = Field(
        ...,
        gt=0,
        description="Number of polymer residues in this chain",
        example=250,
    )
    organism: Optional[str] = Field(
        None,
        description="Source organism of the expressed chain (if available)",
        example="Homo sapiens",
    )


class LigandDataset(BaseModel):
    """Summary for a single chemical component bound in the structure."""

    chem_id: constr(strip_whitespace=True, min_length=1, max_length=3) = Field(
        ...,
        description="Three-letter chemical component ID (e.g., 'ATP')",
        example="ATP",
    )
    name: str = Field(
        ...,
        description="Common name of the ligand",
        example="Adenosine-5'-triphosphate",
    )
    count: int = Field(
        ...,
        ge=1,
        description="Number of copies present in the asymmetric unit / biological assembly",
        example=1,
    )


class Provenance(BaseModel):
    """Metadata needed for reproducibility & FAIR compliance."""

    source: str = Field(
        ...,
        description="Primary data provider",
        example="RCSB PDB",
    )
    retrieved: datetime = Field(
        ...,
        description="UTC timestamp when the entry was fetched",
        example="2025-05-19T10:30:00Z",
    )
    api_url: HttpUrl = Field(
        ...,
        description="Exact URL (or GraphQL query) used to obtain raw JSON",
        example="https://data.rcsb.org/rest/v1/core/entry/1ABC",
    )


# ────────────────────────────────────────────────────────────
# Top-level dataset returned to agents
# ────────────────────────────────────────────────────────────
class StructureDataset(BaseModel):
    """Token-efficient context bundle for one PDB entry."""

    pdb_id: constr(strip_whitespace=True, min_length=4, max_length=6, regex=r"^[0-9][A-Za-z0-9]{3,5}$") = Field(
        ...,
        description="Unique PDB identifier",
        example="1ABC",
    )
    title: str = Field(
        ...,
        description="Descriptive title of the structure",
        example="Crystal structure of human insulin receptor ectodomain",
    )
    method: str = Field(
        ...,
        description="Experimental method (e.g., X-ray diffraction, NMR, Cryo-EM)",
        example="X-ray diffraction",
    )
    resolution: Optional[float] = Field(
        None,
        gt=0,
        description="Reported resolution in Å (null for NMR models)",
        example=2.0,
    )
    chains: List[ChainInfo] = Field(
        ...,
        description="List of polymer chains with basic metadata",
    )
    ligands: List[LigandDataset] = Field(
        ...,
        description="Non-polymer entities (ligands, ions) present in the structure",
    )
    provenance: Provenance = Field(
        ...,
        description="Where/how/when this context bundle was sourced",
    )

    class Config:
        """Pydantic settings."""

        orm_mode = True
        allow_mutation = False  # Keep datasets immutable after creation
