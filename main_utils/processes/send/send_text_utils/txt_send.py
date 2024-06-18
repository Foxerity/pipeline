import sys

sys.path.append(r'D:\project\pipeline\main_utils\processes\send\send_text_utils')
import os
import json
import torch
import argparse
import multiprocessing
from txt_receive import Receiver
from preprocess_text import process
from models.transceiver import DeepSC
from main_utils.processes.send.send_text_utils.utils import PowerNormalize, split_sentences, list_to_bytes


class Sender:
    def __init__(self):
        super().__init__()
        self.args = self.parse_arguments()
        self.device = self.set_device()
        self.vocab, self.token_to_idx, self.idx_to_token = self.load_vocab(self.args.vocab_file)
        self.num_vocab = len(self.token_to_idx)
        self.pad_idx = self.token_to_idx.get("<PAD>")
        self.start_idx = self.token_to_idx.get("<START>")
        self.end_idx = self.token_to_idx.get("<END>")
        self.deepsc = None
        self.txt_queue = None
        self.txt_tral_queue = None

    def setup(self):
        self.deepsc = self.initialize_deepsc()
        self.load_checkpoint()

    def run(self, txt_queue, txt_tral_queue):
        self.setup()
        self.txt_queue = txt_queue
        self.txt_tral_queue = txt_tral_queue
        input_dir = txt_queue.get()

        # 读出文件夹中所有.txt文件的句子
        process_sentences = process(input_dir)

        for single_sentence in process_sentences:
            cn_sentences, int_numbers, float_numbers = split_sentences([single_sentence])
            self.process_sentence(cn_sentences[0], int_numbers, float_numbers, single_sentence)

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Configuration for the Sender model.")
        parser.add_argument('--vocab-file', default=r'D:\project\pipeline\main_utils\processes\send\send_text_utils/europarl/vocab.json',
                            type=str,
                            help='Path to the vocabulary file.')
        parser.add_argument('--checkpoint-path',
                            default=r'D:\project\pipeline\main_utils\processes\send\send_text_utils/checkpoints/deepsc-AWGN', type=str,
                            help='Path to the checkpoint directory.')
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
        vocab_file = r"D:\project\pipeline\main_utils\processes\send\send_text_utils\europarl\vocab.json"
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

    def process_sentence(self, sentence, int_numbers, float_numbers, single_sentence):
        self.deepsc.eval()
        with torch.no_grad():
            # 数据准备
            sent_tensor = self.prepare_sentence(sentence)
            sent_mask = self.create_sentence_mask(sent_tensor)

            enc_output = self.deepsc.encoder(sent_tensor, sent_mask)  # 语义编码
            channel_enc_output = self.deepsc.channel_encoder(enc_output)  # 信道编码
            Tx_sig = PowerNormalize(channel_enc_output)  # 归一化
            bit_stream = self.prepare_bit_stream(Tx_sig, int_numbers, float_numbers, single_sentence)
            self.txt_queue.put(bit_stream)

    def prepare_sentence(self, sentence):
        sent_tensor = torch.tensor(sentence).unsqueeze(0).to(self.device)
        return sent_tensor

    def create_sentence_mask(self, sentence_tensor):
        return (sentence_tensor == self.pad_idx).unsqueeze(-2).type(torch.FloatTensor).to(self.device)

    @staticmethod
    def prepare_bit_stream(Tx_sig, int_numbers, float_numbers, single_sentence):
        Tx_sig = Tx_sig.cpu().numpy().tolist()
        total = [Tx_sig] + [int_numbers] * 5 + [float_numbers] * 5 + [single_sentence]
        return list_to_bytes(total)
