import uuid

import uvicorn
from fastapi import File, UploadFile, Form, Request, Depends
from fastapi import FastAPI

from pydantic import BaseModel

import numpy as np
from PIL import Image
import json

import config

from aai.feat.material import featurize_composition
from aai.feat.molecule import featurize_molecule, pubchem_cid_to_mol, pdb_id_to_mol
from aai.segment.image_segment import model_segment, binary_segment, watershed_segment
from aai.segment.utils import normalize_im, blur_im

from aai.aws.s3 import *
from aai.io.tem import TEMDataset

app = FastAPI(
    title="AtomicAI API",
    description="""Visit port 8501 for the Streamlit interface.""",
    version="0.0.1")

## classes for API payloads
class S3dest(BaseModel):
    bucket: str
    objectname: str

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


@app.post("/upload/{destination}") # {method}  
def upload(destination: str,  file: UploadFile = File(...)): # destination: str = Form(...),
    
    '''
    destination is a string of location in aws where data should go. 
    dot separated. example: s3.bucket_name.object_name 
    this is to avoid the issue of multipart form-data which is used for files being incompatible with application/json.
    see the Warning on https://fastapi.tiangolo.com/tutorial/request-files/?h=upload#uploadfile
    can add additional path parameters which can parse s3 paths (maybe with starlette {file_path:path}) to work around.
    otherwise, would normally use S3dest to accept post body here.
    '''
    destination = destination.split('.')
    # data = await request.form()
    print(destination)
    bucket_name = destination[1]
    object_name = '/'.join(destination[2:]) + '/' + file.filename

    if destination[0] == 's3':
        s3_url, arn, object_url = upload_to_s3(file.file, bucket_name, object_name)

    return {"name": s3_url}

@app.post("/get_tem_image/{seg_method}")
def get_tem_image(seg_method: str, dest: S3dest):
    # TODO: implement autoencoder inference. point to model location on S3. generalize for multiple files 
    
    #image_bytes is BytesIO object
    image_bytes = download_from_s3_to_memory(dest.bucket, dest.objectname)
    temdata = TEMDataset(filenames=[dest.objectname], filestreams=[image_bytes])
    im_array, im_meta = temdata[0] # single image dataset

    # this is necessary for the binary, watershed algorithms to work well given current hyperparams.
    im_array = im_array.astype(np.uint16)

    if seg_method == "Watershed":
        
        regionlist, label_image, im_overlay = watershed_segment(im_array, 0.05, 0.01)

    elif seg_method == "Binary":

        regionlist, label_image, im_overlay = binary_segment(normalize_im(im_array), sigma=0.01)
                
    elif seg_method == "Autoencoder":
        im_array = normalize_im(im_array)
        pass
    
    # normalize segmented image
    im_overlay = normalize_im(im_overlay)
    im_array = normalize_im(im_array)

    ## json outputs
    # segmented image
    seg_image_json = json.dumps(np.asarray(im_overlay).tolist())

    # original image   
    image_json = json.dumps(im_array.tolist())

    # original metadata from TEMDataset  # check for json compatibility  print([type(i)for i in im_meta.values()])
    meta_json = json.dumps(im_meta)
   
    # name = f"/storage/{str(uuid.uuid4())}.png"
    return {"name": dest.objectname, "seg_image_json": seg_image_json, "image_json": image_json, "metadata": meta_json}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
