import socket
import io
from PIL import Image
from tools import super_resolution, reconstruct_image


def receive_image_chunks():
    received_chunks = []
    total_size = 0

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "10.168.2.153"
    port = 12345

    server_socket.bind((host, port))
    server_socket.listen(1)

    print("Waiting for client to connect...")
    client_socket, client_address = server_socket.accept()
    print("Connected to client:", client_address)

    while True:
        chunk = client_socket.recv(1047)
        if not chunk:
            break
        received_chunks.append(chunk)
        total_size += len(chunk)

    print("Received total bytes:", total_size)
    client_socket.close()
    server_socket.close()

    return received_chunks


if __name__ == "__main__":
    output_image_path = '../out.png'
    received_chunks = receive_image_chunks()
    reconstructed_image = reconstruct_image(received_chunks)
    super_resolution_image = super_resolution(reconstructed_image, "sr_out.png")
