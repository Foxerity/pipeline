import os


def is_not_empty(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print("指定的路径不存在。")
        return False
    # 检查文件夹是否为空
    return os.listdir(folder_path)


def main(image_load_path):
    while True:
        if is_not_empty(image_load_path):
            image_list = os.listdir(image_load_path)
