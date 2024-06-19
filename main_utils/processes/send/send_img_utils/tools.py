from PIL import Image


def downsample_images(image):
    resized_image = image.resize((64, 64), Image.BICUBIC)
    return resized_image


def resize_2k_image(img, size=(2048, 2048)):
    # 使用Lanczos重采样算法调整图像大小
    img_resized = img.resize(size, Image.Resampling.LANCZOS)
    return img_resized


def split_image(original_image):
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
