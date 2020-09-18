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
import skimage.filters
import skimage.measure


from skimage.transform import resize
from skimage.filters import threshold_otsu, threshold_local, rank
from skimage.segmentation import clear_border, watershed
from skimage.measure import label, regionprops
from skimage.morphology import closing, square, disk
from skimage.color import label2rgb

from PIL import Image as pimage
from PIL import ImageFile
from io import BytesIO


def uniq(input):
	output = []
	for x in input:
		if x not in output:
			output.append(x)
	return output

def binary_segment(image, sigma=0.1, image_type='dark_field', algo='bimodal'):
    """
    takes a grayscale image and segments it into 2 classes (can be upgraded to be multiclass)

    """
    # image = np.asarray(pimage.open(ff).convert('L')) / 255

    image = skimage.filters.gaussian(image, sigma=sigma) #, multichannel=False, preserve_range=True)

    if algo == 'bimodal':
    # apply threshold
        thresh = threshold_otsu(image)
        # print('thresh bimodal')
        print('thresh otsu: %f' % thresh)

    elif algo == 'local':
        bsize = 35 # int(np.amin(image.shape) / 2) + 1
        thresh = threshold_local(image, bsize)
        print('thresh local: %f' % thresh)

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

    image_label_overlay = label2rgb(label_image, image=image, bg_label = 0)
    
    regionlist = regionprops(label_image)
    regionlist = sorted(regionlist, key=lambda x: (x.centroid[0],(x.centroid[1])))

    return regionlist, label_image, image_label_overlay

def watershed_segment(image, thresh):

    image = skimage.filters.gaussian(image, sigma=0.1)

    denoised = rank.median(image, disk(5))
    # find continuous region (low gradient -
    # where less than 10 for this image) --> markers
    # disk(5) is used here to get a more smooth image
    plt.imshow(denoised, cmap=plt.cm.gray)
    plt.show()
    markers = rank.gradient(denoised, disk(5)) < thresh
    markers = ndi.label(markers)[0]

    # local gradient (disk(2) is used to keep edges thin)
    gradient = rank.gradient(denoised, disk(2))

    # process the watershed
    label_image = watershed(gradient, markers)

    image_label_overlay = label2rgb(label_image, image=image, bg_label = 0)
    
    regionlist = regionprops(label_image)
    regionlist = sorted(regionlist, key=lambda x: (x.centroid[0],(x.centroid[1])))



    return regionlist, label_image, image_label_overlay


def segment_main(image_data):
    pass
    return

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



