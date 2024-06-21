import os
import time
from collections import Counter
import torch
import json
import argparse
from main_utils.processes.send.send_text_utils.models.transceiver import DeepSC
from main_utils.processes.send.send_text_utils.utils import SeqtoText, most_frequent_element_int, most_frequent_element_float, replace_and_return, subsequent_mask, bytes_to_list
import numpy as np
import time
class Receiver:
    def __init__(self):
        super().__init__()
        self.args = self.parse_arguments()
        self.device = self.set_device()
        self.vocab, self.token_to_idx, self.idx_to_token = self.load_vocab(self.args.vocab_file)
        self.num_vocab = len(self.token_to_idx)
        self.pad_idx = self.token_to_idx.get("<PAD>")
        self.start_idx = self.token_to_idx.get("<START>")
        self.end_idx = self.token_to_idx.get("<END>")
        self.receive_data_queue = None
        self.txt_tral_queue = None

        self.value_dict = {
            "send_packet_count": 0,
            "recevie_packet_count": 0,             # 接受端受到的包数
            "most_common_number": 0,                # 发送端发送的包数
            "loss_packet": 0,                       # 接收端丢包率
            "bit_ratio": 0,                         # 比特率
            "ber_ratio": 0,                         # 误码率
            "mean_ber_ratio": 0                     # 平均误码率
        }
    def setup(self):
        self.deepsc = self.initialize_deepsc()
        self.load_checkpoint()
        self.deepsc.eval()

    def run(self, send_data_queue, receive_data_queue, txt_tral_queue, txt_value_queue):
        self.setup()
        flag = 0
        while True:
            if not send_data_queue.empty():
                self.receive_data_queue = receive_data_queue
                self.txt_tral_queue = txt_tral_queue
                start_time = time.time()
                bit_stream = send_data_queue.get()
                end_time = time.time()
                delay_time = end_time - start_time
                # 比特率
                self.value_dict["bit_ratio"] = len(bit_stream)/delay_time
                # 丢包率
                if flag == 0:
                    bit_stream = np.frombuffer(bit_stream, dtype='<u2')
                    counter = Counter(bit_stream)
                    self.value_dict["send_packet_count"], _ = counter.most_common(1)[0]
                    flag = 1
                    continue
                self.value_dict["recevie_packet_count"] += 1

                receive = bytes_to_list(bit_stream)
                if len(receive[0][0]) == 0:
                    self.receive_data_queue.put('? \n')
                    self.txt_tral_queue.put('? \n')
                    continue
                Rx_sig, int_1, int_2, int_3, int_4, int_5, float_1, float_2, float_3, float_4, float_5, tral_txt = receive
                Rx_sig = torch.tensor(Rx_sig).to(self.device)
                try:
                    total_int = most_frequent_element_int(torch.tensor(int_1), torch.tensor(int_2), torch.tensor(int_3),
                                                          torch.tensor(int_4), torch.tensor(int_5))
                except ValueError:
                    self.receive_data_queue.put('? \n')
                    self.txt_tral_queue.put('? \n')
                    continue
                total_float = most_frequent_element_float(torch.tensor(float_1), torch.tensor(float_2),
                                                          torch.tensor(float_3), torch.tensor(float_4),
                                                          torch.tensor(float_5))
                outputs = self.decode_signal(Rx_sig)
                result_string = self.process_output(outputs)
                self.save_result(result_string, total_int, total_float, tral_txt)
                txt_value_queue.put(self.value_dict)
            time.sleep(0.2)
        self.value_dict["loss_packet"] = (self.value_dict["send_packet_count"] - self.value_dict["recevie_packet_count"])/self.value_dict["send_packet_count"]

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Configuration for the Receiver model.")
        parser.add_argument('--vocab-file', default='main_utils/processes/send/send_text_utils/europarl/vocab.json', type=str, help='Path to the vocabulary file.')
        parser.add_argument('--checkpoint-path', default='main_utils/processes/send/send_text_utils/checkpoints/deepsc-AWGN', type=str, help='Path to the checkpoint directory.')
        parser.add_argument('--channel', default='AWGN', type=str, help='Channel type.')
        parser.add_argument('--MAX-LENGTH', default=50, type=int, help='Maximum sequence length.')
        parser.add_argument('--MIN-LENGTH', default=4, type=int, help='Minimum sequence length.')
        parser.add_argument('--d-model', default=128, type=int, help='Dimension of the model.')
        parser.add_argument('--dff', default=512, type=int, help='Dimension of the feed-forward network.')
        parser.add_argument('--num-layers', default=4, type=int, help='Number of layers.')
        parser.add_argument('--num-heads', default=8, type=int, help='Number of attention heads.')

        args = parser.parse_args()
        args.vocab_file = './' + args.vocab_file
        return args

    def set_device(self):
        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def load_vocab(self, vocab_file):
        with open(vocab_file, 'r', encoding='utf-8') as file:
            vocab = json.load(file)
        token_to_idx = vocab['token_to_idx']
        idx_to_token = {idx: token for token, idx in token_to_idx.items()}
        return vocab, token_to_idx, idx_to_token

    def initialize_deepsc(self):
        return DeepSC(
            self.args.num_layers,
            self.num_vocab,
            self.num_vocab,
            self.num_vocab,
            self.num_vocab,
            self.args.d_model,
            self.args.num_heads,
            self.args.dff,
            0.1
        ).to(self.device)

    def load_checkpoint(self):
        model_paths = [
            (os.path.join(self.args.checkpoint_path, fn), int(os.path.splitext(fn)[0].split('_')[-1]))
            for fn in os.listdir(self.args.checkpoint_path) if fn.endswith('.pth')
        ]
        model_paths.sort(key=lambda x: x[1])
        latest_checkpoint_path = model_paths[-1][0] if model_paths else None

        if latest_checkpoint_path:
            checkpoint = torch.load(latest_checkpoint_path)
            self.deepsc.load_state_dict(checkpoint)

    def decode_signal(self, Rx_sig):
        memory = self.deepsc.channel_decoder(Rx_sig)
        int_tensor = Rx_sig.int()
        flattened_tensor = int_tensor.flatten(start_dim=1)
        outputs = torch.ones(1, 1).fill_(self.start_idx).type_as(flattened_tensor.data)
        for i in range(self.args.MAX_LENGTH - 1):
            trg_mask = (outputs == self.pad_idx).unsqueeze(-2).type(torch.FloatTensor)
            look_ahead_mask = subsequent_mask(outputs.size(1)).type(torch.FloatTensor)
            combined_mask = torch.max(trg_mask, look_ahead_mask).to(self.device)

            dec_output = self.deepsc.decoder(outputs, memory, combined_mask, None)
            pred = self.deepsc.dense(dec_output)

            prob = pred[:, -1:, :]
            _, next_word = torch.max(prob, dim=-1)
            outputs = torch.cat([outputs, next_word], dim=1)
        return outputs

    def process_output(self, outputs):
        StoT = SeqtoText(self.token_to_idx, self.end_idx)
        sentences = outputs.cpu().numpy().tolist()
        result_string = list(map(StoT.sequence_to_text, sentences))
        result_string = [result_string[0][8:]]
        result_string = [' '.join(result_string[0].split())]
        return result_string

    def save_result(self, result_string, total_int, total_float, tral_txt):
        final = replace_and_return(result_string, total_int, total_float)
        file_contents = "".join(final[0]).replace("， ", "，") + "\n"

        if file_contents.strip():  # Check if file_contents is not just whitespace or empty
            self.receive_data_queue.put(file_contents)
            self.txt_tral_queue.put(tral_txt)




