import time
import random

from pipeline_abc import Pipeline

""" Simple Channel Effect
"""


class ReceiveChannelEffect(Pipeline):
    """
    
    Use Example:

    ```python

    SCE = SimpleChannelEffect()             # Init SimpleChannelEffect Class

    send_bytes = b'\x00' * 1047

    print("start")
    start_time = time.perf_counter()

    receive_bytes = SCE.fun(send_bytes)     # Call SimpleChannelEffect.fun()

    end_time = time.perf_counter()
    print("End")

    print(f"send_bytes: {send_bytes}")
    print(f"receive_bytes: {receive_bytes}")
    print(f"Time Cost: {end_time - start_time} s")

    ```
    Args:

        BER: Bit Error Rate, e.g. 0.01 means 1% bit error rate
        BW: BandWidth (Kbps), e.g. 3 means 3Kbps
        PKG_SIZE: One Packet Data Size (bytes), e.g. 1047 means 1047 bytes per packet
    """

    def __init__(self):
        super().__init__()
        self.ber = None
        self.bw = None
        self.pkg_size = None
        self.byteorder = None

        self.data_dict = None

    def setup(self, BER: int = 0.01, BW: float = 3., PKG_SIZE: int = 1047, byteorder: str = "little", **kwargs):
        self.ber = BER
        self.bw = BW
        self.pkg_size = PKG_SIZE
        self.byteorder = byteorder

        self.data_dict = {}

    @staticmethod
    def bitlist2bytes(bitlist: list, byteorder: str = "little"):
        if len(bitlist) % 8 != 0:
            raise ValueError("bitlist length must be a multiple of 8")
        bytes_value = b''
        for i in range(0, len(bitlist), 8):
            bytes_value += int("".join(map(str, bitlist[i:i + 8])), 2).to_bytes(1, byteorder)
        if byteorder == "little":
            bytes_value = bytes_value[::-1]
        return bytes_value

    @staticmethod
    def bytes2bitlist(bytes_value: bytes, byteorder: str = "little"):
        bitlist = []
        if byteorder == "little":
            bytes_value = bytes_value[::-1]
        for B in bytes_value:
            bitstrs = bin(B)[2:].rjust(8, '0')
            bitlist.extend([int(b) for b in bitstrs])
        return bitlist

    @staticmethod
    def channel_error(bitlist: list, ber: float, mode: str = "constant"):
        """ Simple simulation of channel error according to bit error rate
        Args:
            bitlist: bits to be disturbed
            ber: bit error rate
            mode: support "constant", "accidental", "fluctuate" mode

        Returns:
            bitlist (list) : disturbed bits
            _ber (float) : actual bit error rate
        """
        if mode == "constant":
            _ber = ber
        elif mode == "accidental":
            _ber = random.choices((0, ber))[0]
        elif mode == "fluctuate":
            _ber = max(0, ber + random.gauss(0, 1) / 1.96 * 0.1)
        else:
            raise ValueError(f"mode {mode} is not supported")
        idxs = random.sample(range(0, len(bitlist)), int(len(bitlist) * _ber))
        for i in idxs:
            bitlist[i] = 1 - bitlist[i]
        return bitlist, _ber

    @staticmethod
    def channel_delay(bw: float, pkg_size: int):
        """ Calculate channel delay based on bandwidth
        Args:
            bw: bandwidth (Kbps), e.g. 3 means 3Kbps
            pkg_size: One Packet Data Size (bytes), e.g. 1047 means 1047 bytes per packet
        Returns:
            packet_delay_time: packet delay time (s)
        """
        other_time = 0
        packet_delay_time = pkg_size * 8 / (bw * 1024) - other_time
        return packet_delay_time

    def fun(self, put_data_queue, get_data_queue, socket_value_queue):
        while True:
            while not put_data_queue.empty():
                print("ReceiveChannelEffect: getting data")
                ori_bytes = put_data_queue.get()
                ori_bytes = self.bytes2bitlist(ori_bytes, self.byteorder)
                ori_bytes, _ber = self.channel_error(ori_bytes, self.ber)
                ori_bytes = self.bitlist2bytes(ori_bytes, self.byteorder)
                sleep_time = self.channel_delay(self.bw, self.pkg_size)
                sleep_time += random.uniform(0.05, 0.2)
                print(f"effect time: {sleep_time} s")
                self.data_dict['time'] = 8 * (1047 / sleep_time)
                time.sleep(sleep_time)
                socket_value_queue.put(self.data_dict)
                get_data_queue.put(ori_bytes)


