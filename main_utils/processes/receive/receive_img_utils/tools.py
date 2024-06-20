from PIL import Image
import torch
from torchvision import transforms
import main_utils.processes.receive.receive_img_utils.models as models
from main_utils.processes.receive.receive_img_utils.utils import make_coord
from main_utils.processes.receive.receive_img_utils.test import batched_predict


def reconstruct_image(chunks):
    num_tiles = len(chunks)  # 16
    num_rows = 4
    num_cols = 4
    tile_width = 0
    tile_height = 0
    new_chunks = []
    for c in chunks:

        index = 0
        count = 0
        for byte in c:
            if byte != 0:
                count += 1
            if count == 768 + 3:
                break
            index += 1
        new_chunks.append(c[3:index + 1])
    chunks = new_chunks

    # 获取图像块的尺寸
    if num_tiles > 0:
        first_tile = Image.frombytes("RGB", (16, 16), chunks[0])
        tile_width, tile_height = first_tile.size

    reconstructed_image = Image.new('RGB', (tile_width * num_cols, tile_height * num_rows))

    for i in range(num_rows):
        for j in range(num_cols):
            tile_index = i * num_cols + j
            if tile_index < num_tiles:
                tile_data = chunks[tile_index]
                tile_image = Image.frombytes('RGB', (tile_width, tile_height), tile_data)
                reconstructed_image.paste(tile_image, (j * tile_width, i * tile_height))

    return reconstructed_image


def super_resolution(image):
    img = transforms.ToTensor()(image.convert('RGB'))

    model = models.make(torch.load("/home/samaritan/Desktop/pipeline_final/pipeline/main_utils/processes/receive/receive_img_utils/rdn-liif.pth")['model'], load_sd=True).cuda()

    h, w = list(map(int, '2048,2048'.split(',')))
    coord = make_coord((h, w)).cuda()
    cell = torch.ones_like(coord)
    cell[:, 0] *= 2 / h
    cell[:, 1] *= 2 / w
    pred = batched_predict(model, ((img - 0.5) / 0.5).cuda().unsqueeze(0),
                           coord.unsqueeze(0), cell.unsqueeze(0), bsize=30000)[0]
    pred = (pred * 0.5 + 0.5).clamp(0, 1).view(h, w, 3).permute(2, 0, 1).cpu()
    return transforms.ToPILImage()(pred)
