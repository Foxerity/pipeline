import io
import socket
import struct
import numpy as np
from PIL import Image

from tools import downsample_images, resize_2k_image, split_image

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "10.168.2.153"
port = 12345

# Connect to the server
client_socket.connect((host, port))

# Send data to the server
# message = "Hello, server!"
# client_socket.send(message.encode('utf-8'))

img = '鱼.png'
image_path = f'{img.replace(".png", "")}_2k.png'
downsample_image_path = f'{img.replace(".png", "")}_64.png'
img = Image.open(img)
img_2k = resize_2k_image(img)
img_64 = downsample_images(img_2k)
image_chunks_list = split_image(img_64)

for chunk in image_chunks_list:
    chunk = chunk.tobytes()

    while len(chunk) < 1044:
        chunk += b'\x00'
    chunk = b'\x24' + b'\x4d' + b'\x53' + chunk
    #    client_socket.sendall(struct.pack('!I', len(chunk)))

    print("size:{}".format(len(chunk)))

    client_socket.sendall(chunk)

# Receive a response from the server
# response = client_socket.recv(1047)
# print("Received from server:", response.decode('utf-8'))

client_socket.close()
