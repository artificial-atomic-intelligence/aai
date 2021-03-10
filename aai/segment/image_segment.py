#!/usr/bin/python
"""
Version 4/14/2020

Segment split .tifs and identify a cell ID for each cell taken from an assay / plasticity / condition.

"""
# from IPython import get_ipython

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import numpy as np
import pandas as pd
from scipy import ndimage as ndi

import os
import sys
import re
import timeit

import torch

import skimage.filters
import skimage.measure
from skimage.transform import resize
from skimage.filters import threshold_otsu, threshold_local, rank
from skimage.segmentation import clear_border, watershed
from skimage.measure import label, regionprops
from skimage.morphology import closing, square, disk
from skimage.color import label2rgb
from skimage.util import img_as_ubyte

from PIL import Image as pimage
from PIL import ImageFile
from io import BytesIO

from aai.segment.autoencoder import AutoencoderBottle

def numpy_to_pil(im):

    im = np.uint8(255*im)
    im = pimage.fromarray(im).convert('L')
    # print(im.mode)

    return im

def uniq(input):
    output = []
    for x in input:
        if x not in output:
            output.append(x)
    return output


def model_segment(image, model_name, model_file):
    """Segment image with a trained model.

    Arguments
    ---------
    image: np.array
    model_name: str
        Model to instantiate.
    model_file: str
        Filename of trained model

    Returns
    -------
    contour: np.array
        Detected image contours

    """

    if model_name == "AutoencoderBottle":
        model = AutoencoderBottle()

    model.load_state_dict(torch.load(model_file))
    model.eval()
    tensor_im = torch.Tensor(image)
    contour = model(tensor_im)

    # TODO: not sure if need optimizer and loss function here too

    return contour


def binary_segment(image, sigma=0.1, image_type='dark_field', algo='bimodal'):
    """
    takes an image and segments it into 2 classes based on grayscaling (can be upgraded to be multiclass)

    """
        # use pil conversion to get to grayscale
    image = numpy_to_pil(image)

    if image.mode != 'L':
        # im_pil is usually 'RGB' with all 3 channels the same; binary_segment requires grayscale, but back-conversion to rgb at the end.
        image = image.convert('L')

    image = skimage.filters.gaussian(
        np.asarray(image), sigma=sigma)  #, multichannel=False, preserve_range=True)

    if algo == 'bimodal':
        # apply threshold
        thresh = threshold_otsu(image)
        # print('thresh bimodal')
        # print('thresh otsu: %f' % thresh)

    elif algo == 'local':
        bsize = 35  # int(np.amin(image.shape) / 2) + 1
        thresh = threshold_local(image, bsize)
        # print('thresh local: %f' % thresh)

    # remove artifacts connected to image border
    if image_type == 'bright_field':
        bgl = 1
    elif image_type == 'dark_field':
        bgl = 0
    else:
        sys.exit()

    bw = closing(image < thresh)
    cleared = clear_border(bw)
    label_image = label(cleared)
    #     label_image = label(bw)

    image_label_overlay = label2rgb(label_image, image=image, bg_label=0)

    regionlist = regionprops(label_image)
    regionlist = sorted(regionlist, key=lambda x: (x.centroid[0], (x.centroid[1])))

    image_label_overlay = pimage.fromarray(skimage.util.img_as_ubyte(image_label_overlay), 'RGB')

    return regionlist, label_image, image_label_overlay


def watershed_segment(image, thresh, sigma):

    """Use watershed algorithm to segment images.

    Arguments
    ---------
    image: np.array
    thresh: float

    Returns
    -------
    regionlist: list. list of instance segmented regions
    label_image: np.array. labeled image mask of regions
    image_label_overlay: np.array. image with segmeneted regions overlaid

    """

    # image = np.array(image.convert('P'))  # 8-bit pixels
    
    if len(np.shape(image)) > 2:
        # im_pil is usually 'RGB' with all 3 channels the same; binary_segment requires grayscale, but back-conversion to rgb at the end.
        image = numpy_to_pil(image)
        image = image.convert('L')

    image = img_as_ubyte(image)
    image = skimage.filters.gaussian(image, sigma=0.05)

    print(image.shape)

    denoised = rank.median(image, disk(5))
    # find continuous region (low gradient -
    # where less than 10 for this image) --> markers
    # disk(5) is used here to get a more smooth image
    # plt.imshow(denoised, cmap=plt.cm.gray)
    # plt.show()
    markers = rank.gradient(denoised, disk(5)) < thresh
    markers = ndi.label(markers)[0]

    # local gradient (disk(2) is used to keep edges thin)
    gradient = rank.gradient(denoised, disk(2))

    # process the watershed
    label_image = watershed(gradient, markers)

    image_label_overlay = label2rgb(label_image, image=image, bg_label=0)

    regionlist = regionprops(label_image)
    regionlist = sorted(
        regionlist, key=lambda x: (x.centroid[0], (x.centroid[1])))

    return regionlist, label_image, image_label_overlay


def segment_main(image_data):
    pass
    return


if __name__ == '__main__':

    print(pd.__version__)
    print(skimage.__version__)
    pd.set_option('display.expand_frame_repr', False, 'display.max_columns',
                  None)
    cwd = os.getcwd()

    if 'Chris Price' in cwd:
        datadir = 'C:\\Users\\Chris Price\\Box Sync\\projects\\'
    else:
        print('add your path here')
        sys.exit()

    os.chdir(datadir + '11282018_Au_SA_withlight-as-assem\\')

    files = os.listdir()
