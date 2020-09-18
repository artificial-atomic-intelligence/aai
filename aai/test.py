#!/usr/bin/python

from scipy import ndimage as ndi
import matplotlib.pyplot as plt

from skimage.morphology import disk
from skimage.segmentation import watershed
from skimage import data
from skimage.filters import rank
from skimage.util import img_as_ubyte

from aai.io import dm3_lib as dm3
from aai.io import tem
import base64
import os
import sys
# print(data.camera())
# image = img_as_ubyte(data.camera())
# print(image)

# # denoise image
# denoised = rank.median(image, disk(2))

# # find continuous region (low gradient -
# # where less than 10 for this image) --> markers
# # disk(5) is used here to get a more smooth image
# markers = rank.gradient(denoised, disk(5)) < 10
# markers = ndi.label(markers)[0]

# # local gradient (disk(2) is used to keep edges thin)
# gradient = rank.gradient(denoised, disk(2))

# # process the watershed
# labels = watershed(gradient, markers)
# print(labels)
# print(labels.shape)

# # display results
# fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 8),
#                          sharex=True, sharey=True)
# ax = axes.ravel()

# # print(image)

# ax[0].imshow(image, cmap=plt.cm.gray)
# ax[0].set_title("Original")

# ax[1].imshow(gradient, cmap=plt.cm.nipy_spectral)
# ax[1].set_title("Local Gradient")

# ax[2].imshow(markers, cmap=plt.cm.nipy_spectral)
# ax[2].set_title("Markers")

# ax[3].imshow(image, cmap=plt.cm.gray)
# ax[3].imshow(labels, cmap=plt.cm.nipy_spectral, alpha=.7)
# ax[3].set_title("Segmented")

# for a in ax:
#     a.axis('off')

# fig.tight_layout()
# plt.show()

dirr = '/mnt/g/aai-data/07152020_Au-synth'

filename = dirr + '/A_x30k.dm3'

os.chdir(dirr)
print(os.getcwd())

data = open('A_x30k.dm3','rb').read()
encoded = base64.b64encode(data)


print(type(encoded))
print(isinstance(encoded, str))

# data1 = tem.TEMDataset(filenames=[filename])
data2 = tem.TEMDataset(filenames=[filename], filestreams=[encoded])

# img, meta = data1[0]
img, meta = data2[0]

print(img)
print(meta)
print(type(encoded))

plt.matshow(img)
plt.show()

# dm3f1 = dm3.DM3(filename=dirr+'/A_x30k.dm3', debug = 2)

# aa1 = dm3f1.imagedata
# print(type(aa1))
# print(aa1.shape)
# cuts = dm3f1.cuts
# print("cuts:",cuts)

# if cuts[0] != cuts[1]:
#     plt.matshow(aa1, cmap=plt.cm.gray, vmin=cuts[0], vmax=cuts[1])
#     # plt.title("%s"%filename)
#     plt.colorbar(shrink=.8)

# plt.show()

# print('next')
# dm3f2 = dm3.DM3(filename=dirr+'/A_x30k.dm3', filestream=encoded, debug = 2)

# aa2 = dm3f2.imagedata
# print(type(aa2))
# print(aa2.shape)

# cuts = dm3f2.cuts
# print("cuts:",cuts)

# if cuts[0] != cuts[1]:
#     plt.matshow(aa2, cmap=plt.cm.gray, vmin=cuts[0], vmax=cuts[1])
#     # plt.title("%s"%filename)
#     plt.colorbar(shrink=.8)

# plt.show()

