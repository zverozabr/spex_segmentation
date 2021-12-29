import numpy as np
from skimage.exposure import rescale_intensity
from skimage.filters import median, gaussian
from skimage.filters import threshold_otsu
from skimage.util import apply_parallel


def background_subtract(image, channel, threshold, subtraction):

    """Subtract background signal from other channels

    Parameters
    ----------
    image : Multichannel numpy array (C,X,Y)
    channel: int, Index of background channel
    threshold : int, ignore pixels above this threshold
    subtraction: int, how many intensity units to subract from other channels

    Returns
    -------
    Image Stack : Background corrected Image Stack

    """
    background_ch = image[channel]
    raw_mask_data_cap = background_ch

    raw_mask_data_cap[np.where(raw_mask_data_cap > threshold)] = threshold
    guassian_bg = rescale_intensity(gaussian(raw_mask_data_cap, sigma=3))

    level = threshold_otsu(guassian_bg)
    mask1 = (guassian_bg >= level) * subtraction

    def background_subtract_wrap(array, mask=mask1):
        correct = array[0] - mask
        correct[np.where(correct < 0)] = 0
        return correct[np.newaxis, ...]

    bg_correct = apply_parallel(
        background_subtract_wrap,
        image,
        chunks=(1, image.shape[1], image.shape[2]),
        dtype="float",
    )

    return bg_correct


def run(**kwargs):
    image = kwargs.get('median_image')
    channel = kwargs.get('channel')
    threshold = int(kwargs.get('threshold'))
    subtraction = int(kwargs.get('subtraction'))

    median_image = background_subtract(image, channel, threshold, subtraction)

    return {'median_image': median_image}
