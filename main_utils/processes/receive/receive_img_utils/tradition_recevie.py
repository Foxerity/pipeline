import socket
import cv2
import os
import numpy as np


def bin2array(bit_list, img_shape):
    ans = []
    # assert len(bit_list) % 8 == 0, 'The data should be 8 times'
    tmp_bits = 249
    for byte_idx in range(int(len(bit_list) // 8)):
        bits = ''

        for bit in bit_list[byte_idx * 8: (byte_idx + 1) * 8]:
            bits += str(int(bit))
        try:
            byte_num = int(bits, 2)
            ans.append(byte_num)
            tmp_bits = byte_num
        except ValueError:
            ans.append(tmp_bits)

    img_flatten = np.array(ans)
    return np.reshape(img_flatten, img_shape)

