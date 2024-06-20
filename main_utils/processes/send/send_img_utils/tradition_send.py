import socket

import cv2
import os
import numpy as np


def JPEGCompression(img_path, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    encode_param = [cv2.IMWRITE_JPEG2000_COMPRESSION_X1000, 3]
    quality_param = [cv2.IMWRITE_JPEG_QUALITY, 0]

    name = 'traditional'

    # IMWRITE_JPEG2000_COMPRESSION_X1000
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)
    jp2_path = os.path.join(out_dir, f'{name}.jp2')
    # # cv2.imwrite(jp2_path, img, encode_param)
    cv2.imwrite(jp2_path, img, encode_param)

    img_com = cv2.imdecode(np.fromfile(jp2_path, dtype=np.uint8), -1)
    out_path = os.path.join(out_dir, f'{name}.jpg')
    # cv2.imwrite(out_path, img_com)
    cv2.imencode('.jpg', img_com)[1].tofile(out_path)
    os.remove(jp2_path)

    # # IMWRITE_JPEG_QUALITY
    img = cv2.imdecode(np.fromfile(out_path, dtype=np.uint8), -1)
    cv2.imencode('.jpg', img, quality_param)[1].tofile(out_path)

    # Resize + IMWRITE_JPEG2000_COMPRESSION_X1000 + IMWRITE_JPEG_QUALITY + Resize + IMWRITE_JPEG_QUALITY
    img = cv2.imdecode(np.fromfile(out_path, dtype=np.uint8), -1)
    img = cv2.resize(img, (384, 288))

    cv2.imwrite(jp2_path, img, encode_param)
    img_com = cv2.imdecode(np.fromfile(jp2_path, dtype=np.uint8), -1)
    cv2.imencode('.jpg', img_com)[1].tofile(out_path)
    os.remove(jp2_path)

    img = cv2.imdecode(np.fromfile(out_path, dtype=np.uint8), -1)
    cv2.imencode('.jpg', img, quality_param)[1].tofile(out_path)

    img = cv2.imdecode(np.fromfile(out_path, dtype=np.uint8), -1)
    cv2.imencode('.jpg', img, quality_param)[1].tofile(out_path)

    img = cv2.imread(out_path, cv2.COLOR_BGR2RGB)
    ori_shape = img.shape

    img = cv2.resize(img, (88, 88))
    return img


def array2bin(data):
    lst = []
    # print("Shape: ", data.shape)
    for x in data.flatten():
        byte_str = bin(x)[2:].zfill(8)
        bit_list = [int(bit_char) for bit_char in byte_str]
        lst.extend(bit_list)
    return lst

# img_path = "鱼.png"
# out_dir = 'temp'
#
# img = JPEGCompression(img_path, out_dir)
# data = array2bin(img)
#
# for i in range(0, len(data), 1044):
#     chunk = data[i:i + 1044]
#     chunk += b'\x00' * (1044 - len(chunk))
#     chunk = b'\x24' + b'\x4d' + b'\x53' + bytes(chunk)
#     assert len(chunk) == 1047