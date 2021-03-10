#!/usr/bin/python

"""
Version 8/20/2020

Load TEM images

"""
# from IPython import get_ipython

import numpy as np
import pandas as pd

from torch.utils.data import Dataset
from aai.io import dm3_lib as dm3

import os
import sys
import re

from PIL import Image


def uniq(input):
    output = []
    for x in input:
        if x not in output:
            output.append(x)
    return output

class TEMDataset(Dataset):

    def __init__(self, filedir = None, filenames = None, filestreams = None):

        if filedir is not None:
            self.filenames = os.listdir(filedir)
        elif filenames is not None:
            self.filenames = filenames
        else:
            print('no files specified')
            sys.exit()

        self.file_types = uniq([i.split('.') for i in self.filenames])

        if filestreams is not None:
            if len(filenames) != len(filestreams):
                print('need same number of file names and streams')
                sys.exit()

            self.filestreams = filestreams
        else:
            self.filestreams = None

        self.metadata = {

                        'name': 'unknown',
                        'units': 'px',
                        'scale': 1.,
                        'date': ' ',
                        'device': ' ',
                        'cuts': (0,1)

                            }

    def __getitem__(self, idx):

        # ensure that everything returned in metadata is directly json serializable
        ext = self.filenames[idx].split('.')[-1]

        if ext == 'dm3':
            # print(dm3f.pxsize)     # print(type(dm3f.pxsize[0]))      # print(type(dm3f.pxsize[1]))
            
            if self.filestreams is None:
                dm3f = dm3.DM3(filename = self.filenames[idx], debug = 0)
            else:
                dm3f = dm3.DM3(filename = self.filenames[idx], filestream = self.filestreams[idx], debug=0)

            metadata = self.metadata

            metadata['name'] = self.filenames[idx].split('/')[-1].split('.')[0]
 
            metadata['units'] = dm3f.pxsize[1].decode("utf-8")
            metadata['scale'] = dm3f.pxsize[0]      # number of units per pixel
            metadata['device'] = dm3f.info['device'].decode("utf-8")
            metadata['cuts'] = dm3f.cuts

            img = np.clip(dm3f.imagedata, metadata['cuts'][0], metadata['cuts'][1])
            # convert to RGB
            # img = np.dstack((img, img, img))
            # print('dm3')
            # print(img.shape)
            # print(type(img))
            # print(np.amax(img))
            # print(np.amin(img))
            # print(dm3f.cuts)

        elif ext == 'jpg' or ext == 'png':
            if self.filestreams is None:
                img = np.array(Image.open(self.filenames[idx]).convert('L'))
                # print('jpg1')
                # print(img.shape)
            else:
                img = np.array(Image.open(self.filestreams[idx]).convert('L'))   
                # print('jpg2')
                # print(img.shape)         

            metadata = self.metadata
            metadata['cuts'] = (float(np.amin(img)), float(np.amax(img)))

        else:

            print('unknown file type')
            sys.exit()

        return img, metadata



if __name__ == '__main__':

    print(pd.__version__)
    print(skimage.__version__)
    pd.set_option('display.expand_frame_repr', False, 'display.max_columns', None)
    cwd = os.getcwd()

    if 'Chris Price' in cwd:
        datadir = 'C:\\Users\\Chris Price\\Box Sync\\projects\\'
    else:
        print('add your path here')
        sys.exit()

    os.chdir(datadir +'11282018_Au_SA_withlight-as-assem\\')

    files = os.listdir()