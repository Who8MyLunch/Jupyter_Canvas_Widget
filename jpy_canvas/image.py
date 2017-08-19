
from __future__ import division, print_function, unicode_literals, absolute_import

import base64
import urllib
import io

import numpy as np
import PIL.Image
import requests

"""
This module contains a variety of helper functions for working with image data.
"""


#################################################
# File I/O
def read(fp):
    """
    Read image data from file-like object.  Return Numpy array.
    """
    img = PIL.Image.open(fp)
    data = np.asarray(img)

    return data


def write(fp, data, fmt=None, **kwargs):
    """
    Write image data from Numpy array to file-like object.

    File format is automatically determined from fp if it's a filename, otherwise you
    must specify format via fmt keyword, e.g. fmt = 'png'.

    Parameter options: http://pillow.readthedocs.org/handbook/image-file-formats.html
    """
    m = determine_mode(data)
    img = PIL.Image.fromarray(data.squeeze(), mode=m)
    img.save(fp, format=fmt, **kwargs)


#################################################
# Fetch image data from a URL
def normalize_url(url):
    """
    https://docs.python.org/3.0/library/
    urllib.parse.html#urllib.parse.ParseResult.geturl
    """
    parts = urllib.parse.urlsplit(url)
    url_nice = parts.geturl()

    return url_nice


def download(url, verbose=False):
    """
    Download compressed image data from URL.

    http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests/13137873#13137873
    """
    resp = requests.get(url)
    if not resp.ok:
        msg = 'Problem fetching data: {}'.format(resp.reason)
        raise requests.RequestException(msg)

    # Binary compressed image data from response content.
    data_comp = resp.content

    # Compression format, e.g. 'image/jpeg' --> 'jpeg'
    fmt = resp.headers['content-type'].split('/')[1]

    return data_comp, fmt

#################################################


def determine_mode(data):
    """
    Determine image color mode.
    Input data is expected to be 3D: [num_lines, num_samples, num_bands].
    """
    # Force data to be Numpy ndarray, if not already.
    data = np.asarray(data)

    num_bands = data.shape[2]

    if num_bands == 1:
        mode = 'L'
    elif num_bands == 3:
        mode = 'RGB'
    elif num_bands == 4:
        mode = 'RGBA'
    else:
        raise ValueError('Invalid number of bands.')

    return mode


def setup_data(data):
    """
    Prepare input image data for compression.

    Valid data shapes:
        (rows, columns)    - Greyscale
        (rows, columns, 1) - Greyscale
        (rows, columns, 3) - RGB
        (rows, columns, 4) - RGBA   note: Not valid for jpeg!!!!

    If data type is either np.uint8, then it will be converted by scaling
    min(data) -> 0 and max(data) -> 255.

    Returns np.uint8 data with shape (num_lines, num_samples, num_bands)
    """
    data = np.asarray(data).copy()

    if data.ndim < 2 or 3 < data.ndim:
        raise ValueError('Input data must be 2D or 3D: {}'.format(data.shape))

    # Force 3D array.
    num_lines, num_samples = data.shape[:2]
    if data.ndim == 2:
        data.shape = num_lines, num_samples, 1

    # Convert to np.uint8?
    if not (data.dtype == np.uint8):
        data = data.astype(np.float32)
        mn = data.min()
        mx = data.max()
        if mn == mx:
            raise ValueError('Invalid data range: {}, {}'.format(mn, mx))

        data = (data - mn) / (mx - mn) * 255
        data = np.round(data).astype(np.uint8)

    return data


def encode(data, fmt='png', **kwargs):
    """
    Compress image data contained in Numpy array. and return string of compressed bytes.

    Valid data shapes:
        (rows, columns)    - Greyscale
        (rows, columns, 1) - Greyscale
        (rows, columns, 3) - RGB
        (rows, columns, 4) - RGBA

    fmt: 'png', 'jpg', etc.

    Alpha channel is ignored for JPEG image format.

    Parameter options: http://pillow.readthedocs.org/handbook/image-file-formats.html
    """
    data = setup_data(data)

    fmt = fmt.lower()
    if fmt == 'jpg':
        fmt = 'jpeg'

    if fmt == 'jpeg':
        if data.shape[2] == 4:
            # Discard alpha channel for JPG compression.
            data = data[:, :, :2]

    buff = io.BytesIO()
    write(buff, data, fmt, **kwargs)

    data_comp = buff.getvalue()

    return data_comp


def decode(data_comp):
    """
    Decompress image from byte or string sequence of compressed image data.
    """
    buff = io.BytesIO(data_comp)
    img = PIL.Image.open(buff)

    data = np.asarray(img)

    return data


def data_url(data_comp, fmt):
    """
    Assemble compressed image into data URL string.
    """
    # The decoding step here is necesary since we need to interpret byte data as text.
    # See this link for a nice explanation:
    # http://stackoverflow.com/questions/14010551/how-to-convert-between-bytes-and-strings-in-python-3
    template = 'data:image/{:s};charset={};base64,{:s}'

    # Base64 binary-to-string encoding
    data_encode = base64.b64encode(data_comp)
    encoding = 'utf-8'

    # Build the data url
    data_url = template.format(fmt, encoding, data_encode.decode(encoding=encoding))

    return data_url

#################################################

if __name__ == '__main__':
    pass
