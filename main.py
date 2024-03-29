import uuid

import uvicorn
from fastapi import File, UploadFile, Form, Request, Depends
from fastapi import FastAPI

from pydantic import BaseModel

import numpy as np
from PIL import Image
import json
import pandas as pd

import config

from aai.feat.material import featurize_composition
from aai.feat.molecule import featurize_molecule, pubchem_cid_to_mol, pdb_id_to_mol
from aai.segment.image_segment import model_segment, binary_segment, watershed_segment, autoencoder_postprocess
from aai.segment.utils import normalize_im, blur_im

from aai.aws.s3 import *
from aai.aws.dynamo import *
from aai.io.tem import TEMDataset

from datetime import datetime, time

from pprint import pprint

app = FastAPI(
    title="AtomicAI API",
    description="""Visit port 8501 for the Streamlit interface.""",
    version="0.0.1")

## classes for API payloads
class S3dest(BaseModel):
    bucket: str
    objectname: str
    user_name: str
    projectname: str
    image_id: str
    dynamodb_table_name: str
    backend_url: str


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
    saveprops = ['area', 'bbox', 'centroid', 'equivalent_diameter', 'label', 'perimeter', 'eccentricity', 'orientation']
    # this is necessary for the binary, watershed algorithms to work well given current hyperparams.
    im_array = im_array.astype(np.uint16)

    if seg_method == "Watershed":
        
        regiontable, label_image, im_overlay = watershed_segment(im_array, saveprops, sigma = 0.01)
        flag = True

    elif seg_method == "Binary":

        regiontable, label_image, im_overlay = binary_segment(normalize_im(im_array), saveprops, sigma=0.01)
        flag = True
                
    elif seg_method == "Autoencoder":

        im_array = normalize_im(im_array, (512,512))
        im_input = im_array.reshape(-1, 1, im_array.shape[0], im_array.shape[1])
        sagemaker_client = boto3.client('sagemaker-runtime')

        response = sagemaker_client.invoke_endpoint(
            EndpointName='tem-np-segment',
            ContentType="application/json",
            Accept="application/json",
            Body=json.dumps(im_input.tolist())
        )
        body_str = response['Body'].read().decode("utf-8")
        im_overlay = np.array(json.loads(body_str)).squeeze()
        # print(im_overlay.max())
        # print(im_overlay.min())

        regiontable, label_image, im_overlay = autoencoder_postprocess(im_overlay, saveprops) # normalize_im(im_overlay)
        # print([i['area'] for i in regionlist])
        # print(regionlist[0]['area'])
        flag = True

    else:
        regiontable = 'None'
        flag = False
        im_overlay = im_array

    time_b = datetime.now()
    print(time_b - time_a)
    # DynamoDB
    # prepare a json type "item" for uploading to DynamoDB

    if flag:
        regiontable = regiontable.to_json(orient="split")

    item = {
        "user_name": dest.user_name,
        "image_id": dest.image_id,
        "objectname": dest.objectname,
        "bucket": dest.bucket,
        "projectname": dest.projectname,
        "regiontable": regiontable,
    }
    res = create_single_item(dest.dynamodb_table_name, item)
    print(res) # return True if uploading successed

    # retrieve DynamoDB item back
    key = {'user_name': dest.user_name,'image_id': dest.image_id}
    res = get_item(dest.dynamodb_table_name, key)
    if res['regiontable'] != 'None':
        regiontable_json = json.loads(json.dumps(res['regiontable']))
        regiontable_df = pd.read_json(regiontable_json,orient="split")
        print(regiontable_df)

    time_c = datetime.now()
    print(time_c - time_b)

    # print(type(regiontable))
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

    time_d = datetime.now()
    print(time_d - time_c)

    # name = f"/storage/{str(uuid.uuid4())}.png"
    return {"name": dest.objectname, "seg_image_json": seg_image_json, "image_json": image_json, "metadata": meta_json}

class signup(BaseModel):
    dynamodb_table_name: str
    user_name: str
    passwd: str
    company: str
    first_name: str
    last_name: str
    email_addr: str
    phone_num: str
    

@app.post("/signup")
def sign_up(signup_info: signup):
    item = {
        'user_name': signup_info.user_name,
        'passwd': signup_info.passwd,
        'company': signup_info.company,
        'first_name': signup_info.first_name,
        'last_name': signup_info.last_name,
        'email_addr': signup_info.email_addr,
        'phone_num': signup_info.phone_num,
        'exists': True,
    }
    res = create_single_item(signup_info.dynamodb_table_name, item)
    print(res)

    return res

class login(BaseModel):
    dynamodb_table_name: str
    user_name: str
    passwd: str

@app.get("/login")
def log_in(login_info: login):
    key = {
        'user_name': login_info.user_name,
        'passwd': login_info.passwd
    }
    res = get_item(login_info.dynamodb_table_name, key)
    print(res)

    return res


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)