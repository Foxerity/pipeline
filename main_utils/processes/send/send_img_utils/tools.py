from PIL import Image
import os
import torch
from torchvision import transforms
import models
from utils import make_coord
from test import batched_predict

def downsample_images(img_path, img_output):
    # 检查输入文件夹是否存在
    # if not os.path.exists(folder_path):
    #     print("输入文件夹不存在。")
    #     return
    #
    # # 创建输出文件夹
    # if not os.path.exists(output_folder):
    #     os.makedirs(output_folder)
    #
    # # 获取文件夹中的所有文件
    # files = os.listdir(folder_path)

    # 遍历文件夹中的每个文件
    # for file_name in files:
        # 检查文件是否为图片
    if img_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
        # file_path = os.path.join(folder_path, file_name)
        # 打开图片
        image = Image.open(img_path)
        # 显示图片信息
        resized_image = image.resize((64, 64), Image.BICUBIC)

        # 创建输出文件夹中的文件路径
        # output_file_path = os.path.join(output_folder, file_name)
        # 保存图片到输出文件夹
        resized_image.save(img_output)

        # 关闭图片
        image.close()
    print(f"downsample image save to {img_output}")



def resize_2k_image(input_image_path, output_2k_image_path, size=(2048, 2048)):
    # 打开原始图像
    with Image.open(input_image_path) as img:
        # 使用Lanczos重采样算法调整图像大小
        img_resized = img.resize(size, Image.Resampling.LANCZOS)
        img_resized.save(output_2k_image_path)
        print(f"2k image saved to {output_2k_image_path}")

def split_image(image_path):
    original_image = Image.open(image_path)
    width, height = original_image.size
    print("original image size:", (width, height))

    tile_width = width // 4
    tile_height = height // 4

    tiles = []
    for i in range(4):
        for j in range(4):
            left = j * tile_width
            top = i * tile_height
            right = left + tile_width
            bottom = top + tile_height

            tile = original_image.crop((left, top, right, bottom))
            tiles.append(tile)

    return tiles



def reconstruct_image(chunks):
    num_tiles = len(chunks) #16
    num_rows = 4
    num_cols = 4
    tile_width = 0
    tile_height = 0
    #chunks = [c-b'\x00' for c in chunks]
    new_chunks=[]
    for c in chunks:

        index = 0
        count = 0
        for byte in c:
            if byte != 0:
                count += 1
            if count == 768+3:
                break
            index += 1
        new_chunks.append(c[3:index+1])
    chunks = new_chunks

    # 获取图像块的尺寸
    if num_tiles > 0:
        first_tile = Image.frombytes("RGB", (16, 16), chunks[0])
        tile_width, tile_height = first_tile.size  #16,16

    reconstructed_image = Image.new('RGB', (tile_width * num_cols, tile_height * num_rows))

    for i in range(num_rows):
        for j in range(num_cols):
            tile_index = i * num_cols + j
            if tile_index < num_tiles:
                tile_data = chunks[tile_index]
                tile_image = Image.frombytes('RGB', (tile_width, tile_height), tile_data)
                reconstructed_image.paste(tile_image, (j * tile_width, i * tile_height))

    return reconstructed_image


def super_resolution(image_path, output_image_path):
    img = transforms.ToTensor()(Image.open(image_path).convert('RGB'))

    model = models.make(torch.load("rdn-liif.pth")['model'], load_sd=True).cuda()

    h, w = list(map(int, '2048,2048'.split(',')))
    coord = make_coord((h, w)).cuda()
    cell = torch.ones_like(coord)
    cell[:, 0] *= 2 / h
    cell[:, 1] *= 2 / w
    pred = batched_predict(model, ((img - 0.5) / 0.5).cuda().unsqueeze(0),
                           coord.unsqueeze(0), cell.unsqueeze(0), bsize=30000)[0]
    pred = (pred * 0.5 + 0.5).clamp(0, 1).view(h, w, 3).permute(2, 0, 1).cpu()
    transforms.ToPILImage()(pred).save(output_image_path)