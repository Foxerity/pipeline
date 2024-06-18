import os
import torch
import json
import argparse
from main_utils.processes.send.send_text_utils.models.transceiver import DeepSC
from main_utils.processes.send.send_text_utils.utils import SeqtoText, most_frequent_element_int, most_frequent_element_float, replace_and_return, subsequent_mask, bytes_to_list

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

    def setup(self):
        self.deepsc = self.initialize_deepsc()
        self.load_checkpoint()
        self.deepsc.eval()

    def run(self, send_data_queue, receive_data_queue):
        self.setup()
        while True:

            if not send_data_queue.empty():
                self.receive_data_queue = receive_data_queue

                bit_stream = send_data_queue.get()
                receive = bytes_to_list(bit_stream)
                Rx_sig, int_1, int_2, int_3, int_4, int_5, float_1, float_2, float_3, float_4, float_5 = receive
                Rx_sig = torch.tensor(Rx_sig).to(self.device)

                total_int = most_frequent_element_int(torch.tensor(int_1), torch.tensor(int_2), torch.tensor(int_3),
                                                      torch.tensor(int_4), torch.tensor(int_5))
                total_float = most_frequent_element_float(torch.tensor(float_1), torch.tensor(float_2),
                                                          torch.tensor(float_3), torch.tensor(float_4),
                                                          torch.tensor(float_5))
                outputs = self.decode_signal(Rx_sig)
                result_string = self.process_output(outputs)
                self.save_result(result_string, total_int, total_float)

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

    def save_result(self, result_string, total_int, total_float):
        final = replace_and_return(result_string, total_int, total_float)
        file_contents = "".join(final[0]).replace("， ", "，") + "\n"

        if file_contents.strip():  # Check if file_contents is not just whitespace or empty
            with open("./output.txt", 'a', encoding='utf-8') as file:
                file.write(file_contents)
            print(file_contents)
            self.receive_data_queue.put(file_contents)


