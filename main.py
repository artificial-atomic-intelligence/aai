import uuid

import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np

import config
from aai.feat.material import featurize_composition


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}

@app.post("/{composition}")
def get_featurization(composition: str):
    feats, labels = featurize_composition(composition)
    return feats, labels


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)