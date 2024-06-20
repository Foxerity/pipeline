import socket
import cv2
import os
import numpy as np

def bin2array(bit_list, img_shape):
    ans = []
    # assert len(bit_list) % 8 == 0, 'The data should be 8 times'
    for byte_idx in range(int(len(bit_list) // 8)):
        bits = ''
        for bit in bit_list[byte_idx * 8: (byte_idx + 1) * 8]:
            bits += str(int(bit))
        try:
            byte_num = int(bits, 2)
        except ValueError:
            print(bits)

        ans.append(byte_num)
    img_flatten = np.array(ans)
    return np.reshape(img_flatten, img_shape)

# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(("10.168.2.153", 12345))
# server_socket.listen(1)
# client_socket, client_address = server_socket.accept()
# received_bit_stream = []
# while True:
#     chunk = client_socket.recv(1047)
#     if not chunk:
#         break
#     received_bit_stream.append(chunk[3:])
#
#
# out_file_path = "output.jpg"
# flattened_list = [item for sublist in received_bit_stream for item in sublist]
# count = 0
#
# data = bin2array(flattened_list[0: 185856], (88, 88, 3))
# restore = cv2.resize(data.astype("float"), (2048, 2048))
# cv2.imwrite(out_file_path, restore)

