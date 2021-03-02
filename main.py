import uuid

import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np
from PIL import Image
import json

import config

from aai.feat.material import featurize_composition
from aai.feat.molecule import featurize_molecule, pubchem_cid_to_mol, pdb_id_to_mol
from aai.segment.image_segment import model_segment, binary_segment, watershed_segment
from aai.segment.utils import normalize_im, blur_im

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


@app.post("/image/{method}")
def get_image(method: str, file: UploadFile = File(...)):
    # TODO: implement real segmentation; save file to shared volume
    if method == "Watershed":
        image = Image.open(file.file)
        regionlist, label_image, image_label_overlay = watershed_segment(
            image, .1)
        image_json = json.dumps(label_image.tolist())
    else:
        image_array = np.array(Image.open(file.file))
        image_array = blur_im(normalize_im(image_array))
        # convert to RGB
        image_array = np.array(image_array * 255, dtype='uint8')
        # im = Image.fromarray(image_array)
        image_json = json.dumps(image_array.tolist())
    name = f"/storage/{str(uuid.uuid4())}.png"
    # im.save(name)
    return {"name": name, "image_json": image_json}  # im


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
