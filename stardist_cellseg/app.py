import numpy as np
from stardist.models import StarDist2D
import cv2
from csbdeep.utils import normalize
from decimal import Decimal


def stardist_cellseg(image, seg_channels, scaling, threshold, _min, _max):

    """Segment image by stardist deeplearning method

    Parameters
    ----------
    image : Multichannel image as numpy array
    seg_channels: list of indices to use for nuclear segmentation
    scaling: Integer value scaling
    threshold: probability cutoff
    _min: bottom percentile normalization
    _max: top percentile normalization

    Returns
    -------
    labels : per cell segmentation as numpy array

    """

    temp2 = np.zeros((image.shape[1], image.shape[2]))
    for i in seg_channels:
        try:
            temp = image[i]
            temp2 = temp + temp2
        except IndexError:
            print("oops")

    seg_image = temp2
    seg_image = cv2.resize(
        seg_image,
        (
            seg_image.shape[1] * scaling,
            seg_image.shape[0] * scaling
        ),
        interpolation=cv2.INTER_NEAREST,
    )

    # model for multiplex IF images
    model = StarDist2D.from_pretrained("2D_versatile_fluo")

    image_norm = normalize(seg_image[::1, ::1], _min, _max)
    labels, details = model.predict_instances(image_norm, prob_thresh=threshold)

    labels = cv2.resize(
        labels,
        (
            labels.shape[1] // scaling,
            labels.shape[0] // scaling
        ),
        interpolation=cv2.INTER_NEAREST,
    )

    return labels


def run(**kwargs):

    median_image = kwargs.get('median_image')
    channel_list = kwargs.get('channel_list')
    channel_list.sort()

    scaling = int(kwargs.get('scaling', 1))
    threshold = Decimal(kwargs.get('threshold', 0.479071))
    _min = int(kwargs.get('_min', 1))
    _max = int(kwargs.get('_max', 98.5))

    stardist_label = stardist_cellseg(
        median_image,
        channel_list,
        scaling,
        threshold,
        _min,
        _max
    )

    return {'labels': stardist_label}