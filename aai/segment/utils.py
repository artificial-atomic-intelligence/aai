"""Utils for image data processing and augmentation."""
import numpy as np
import matplotlib.pyplot as plt
import skimage
from skimage import filters, transform, util
import os


def fourfold_rotate(image):
    """Rotate image by 90, 180, and 270 degrees.

    Arguments
    ---------
    image: np.array

    Returns
    -------
    rotated_images: List

    """

    rotations = [90, 180, 270]
    rotated_images = [transform.rotate(image, r) for r in rotations]
    return rotated_images


def crop_image(image, step_size: int = 512):
    """
    Chop image into grids to increase dataset size and reduce memory
    requirements.

    Arguments
    ---------
    image: np.array
    step_size: int
        Images will be cropped into tiles of dimension 
        (step_size, step_size).

    Returns
    -------
    cropped_images: np.array

    """

    windows = util.view_as_windows(
        image, window_shape=(step_size, step_size), step=step_size)
    cropped_images = windows.reshape(-1, step_size, step_size)

    return cropped_images


def normalize_im(image):
    """Scale and normalize pixel values to be between 0 and 1.

    Arguments
    ---------
    image: np.array

    Returns
    -------
    normed: np.array

    """

    scaled = (image - np.mean(image) / np.std(image))
    normed = (scaled - np.min(scaled)) / (np.max(scaled) - np.min(scaled))

    return normed


def blur_im(image, sigma: int = 3):
    """Apply Gaussian filter to reduce image noise.

    Arguments
    ---------
    image: np.array
    sigma: int

    Returns
    -------
    blurred: np.array

    """

    return filters.gaussian(image, sigma, multichannel=True)
