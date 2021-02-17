import uuid

import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np

import config
from aai.feat.material import featurize_composition
from aai.feat.molecule import featurize_molecule, pubchem_cid_to_mol, pdb_id_to_mol

app = FastAPI(
    title="AtomicAI API",
    description="""Visit port 8501 for the Streamlit interface.""",
    version="0.0.1")


@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}


@app.post("/np/{np_composition}")
def get_np_featurization(np_composition: str):
    feats, labels = featurize_composition(np_composition)
    return {"feats": feats, "labels": labels}


@app.post("/mol/{molecule}")
def get_mol_featurization(molecule: int):
    rdkit_mol = pubchem_cid_to_mol(str(molecule))
    feats, labels = featurize_molecule(rdkit_mol)
    return {"feats": feats, "labels": labels}


@app.post("/biomol/{biomolecule}")
def get_biomol_featurization(biomolecule: str):
    rdkit_mol = pdb_id_to_mol(biomolecule)
    feats, labels = featurize_molecule(rdkit_mol)
    return {"feats": feats, "labels": labels}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
