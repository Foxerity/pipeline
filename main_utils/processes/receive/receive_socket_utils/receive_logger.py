import os


class ByteStreamSaver:
    def __init__(self, save_path=r'D:\project\pipeline\main_utils\processes\receive\receive_socket_utils\logger'):
        """
        初始化 ByteStreamSaver 实例，并指定保存路径。

        参数:
        save_path (str): 文件保存路径。
        """
        self.save_path = save_path

    def save_byte_stream(self, byte_data, file_name):
        """
        将字节流保存为文本文件，保持特定格式。

        参数:
        byte_data (bytes): 要保存的字节流数据。
        """
        # 将字节流转换为十六进制字符串并按原格式处理
        hex_str = byte_data.hex()
        formatted_hex_str = ""
        for i in range(0, len(hex_str), 2):
            if i % 32 == 0 and i != 0:  # 每16字节（32个字符）换行
                formatted_hex_str += '\n'
            formatted_hex_str += "\\x" + hex_str[i:i + 2]

        # 添加 b'' 包裹
        formatted_hex_str = "b'" + formatted_hex_str + "'"

        save_path = os.path.join(self.save_path, file_name)
        # 保存到文本文件
        with open(save_path, 'w') as file:
            file.write(formatted_hex_str)

        print(f"字节流已成功保存到文件 {save_path} 中")
