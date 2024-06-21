# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 09:47:54 2020

@author: HQ Xie
utils.py
"""
import os 
import math
import struct
import argparse
import torch
import json
import time
import torch.nn as nn
import numpy as np
from w3lib.html import remove_tags
from nltk.translate.bleu_score import sentence_bleu
from main_utils.processes.send.send_text_utils.models.mutual_info import sample_batch, mutual_information
from collections import Counter
from tqdm import tqdm
import re
from main_utils.processes.send.send_text_utils.preprocess_text import tokenize
import gzip
import pickle

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

parser = argparse.ArgumentParser()

parser.add_argument('--data-dir', default='main_utils/processes/send/send_text_utils/europarl/train_data.pkl', type=str)
parser.add_argument('--vocab-file', default='main_utils/processes/send/send_text_utils/europarl/vocab.json', type=str)
parser.add_argument('--checkpoint-path', default='checkpoints/deepsc-AWGN', type=str)
parser.add_argument('--channel', default='AWGN', type=str)
parser.add_argument('--MAX-LENGTH', default=50, type=int)
parser.add_argument('--MIN-LENGTH', default=4, type=int)
parser.add_argument('--d-model', default=128, type=int)
parser.add_argument('--dff', default=512, type=int)
parser.add_argument('--num-layers', default=4, type=int)
parser.add_argument('--num-heads', default=8, type=int)


# 加载词典
args = parser.parse_args()
args.vocab_file = './' + args.vocab_file
args.vocab_file = r"/home/samaritan/Desktop/pipeline_final/pipeline/main_utils/processes/send/send_text_utils/europarl/vocab.json"
vocab = json.load(open(args.vocab_file, 'rb'))
token_to_idx = vocab['token_to_idx']
idx_to_token = dict(zip(token_to_idx.values(), token_to_idx.keys()))
num_vocab = len(token_to_idx)
pad_idx = token_to_idx["<PAD>"]
start_idx = token_to_idx["<START>"]
end_idx = token_to_idx["<END>"]

class BleuScore():
    def __init__(self, w1, w2, w3, w4):
        self.w1 = w1 # 1-gram weights
        self.w2 = w2 # 2-grams weights
        self.w3 = w3 # 3-grams weights
        self.w4 = w4 # 4-grams weights
    
    def compute_blue_score(self, real, predicted):
        score = []
        for (sent1, sent2) in zip(real, predicted):
            sent1 = remove_tags(sent1).split()
            sent2 = remove_tags(sent2).split()
            score.append(sentence_bleu([sent1], sent2, 
                          weights=(self.w1, self.w2, self.w3, self.w4)))
        return score
            

class LabelSmoothing(nn.Module):
    "Implement label smoothing."
    def __init__(self, size, padding_idx, smoothing=0.0):
        super(LabelSmoothing, self).__init__()
        self.criterion = nn.CrossEntropyLoss()
        self.padding_idx = padding_idx
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.size = size
        self.true_dist = None
        
    def forward(self, x, target):
        assert x.size(1) == self.size
        true_dist = x.data.clone()
        # 将数组全部填充为某一个值
        true_dist.fill_(self.smoothing / (self.size - 2)) 
        # 按照index将input重新排列 
        true_dist.scatter_(1, target.data.unsqueeze(1), self.confidence) 
        # 第一行加入了<strat> 符号，不需要加入计算
        true_dist[:, self.padding_idx] = 0 #
        mask = torch.nonzero(target.data == self.padding_idx)
        if mask.dim() > 0:
            true_dist.index_fill_(0, mask.squeeze(), 0.0)
        self.true_dist = true_dist
        return self.criterion(x, true_dist)


class NoamOpt:
    "Optim wrapper that implements rate."
    def __init__(self, model_size, factor, warmup, optimizer):
        self.optimizer = optimizer
        self._step = 0
        self.warmup = warmup
        self.factor = factor
        self.model_size = model_size
        self._rate = 0
        self._weight_decay = 0
        
    def step(self):
        "Update parameters and rate"
        self._step += 1
        rate = self.rate()
        weight_decay = self.weight_decay()
        for p in self.optimizer.param_groups:
            p['lr'] = rate
            p['weight_decay'] = weight_decay
        self._rate = rate
        self._weight_decay = weight_decay
        # update weights
        self.optimizer.step()
        
    def rate(self, step = None):
        "Implement `lrate` above"
        if step is None:
            step = self._step
            
        # if step <= 3000 :
        #     lr = 1e-3
            
        # if step > 3000 and step <=9000:
        #     lr = 1e-4
             
        # if step>9000:
        #     lr = 1e-5
         
        lr = self.factor * \
            (self.model_size ** (-0.5) *
            min(step ** (-0.5), step * self.warmup ** (-1.5)))
  
        return lr
    

        # return lr
    
    def weight_decay(self, step = None):
        "Implement `lrate` above"
        if step is None:
            step = self._step
            
        if step <= 3000 :
            weight_decay = 1e-3
            
        if step > 3000 and step <=9000:
            weight_decay = 0.0005
             
        if step>9000:
            weight_decay = 1e-4

        weight_decay =   0
        return weight_decay

            
class SeqtoText:
    def __init__(self, vocb_dictionary, end_idx):
        self.reverse_word_map = dict(zip(vocb_dictionary.values(), vocb_dictionary.keys()))
        self.end_idx = end_idx
        
    def sequence_to_text(self, list_of_indices):
        # Looking up words in dictionary
        words = []
        for idx in list_of_indices:
            if idx == self.end_idx:
                break
            else:
                words.append(self.reverse_word_map.get(idx))
        words = ' '.join(words)
        return(words) 


class Channels():

    def AWGN(self, Tx_sig, n_var):
        Rx_sig = Tx_sig + torch.normal(0, n_var, size=Tx_sig.shape).to(device)
        return Rx_sig

    def Rayleigh(self, Tx_sig, n_var):
        shape = Tx_sig.shape
        H_real = torch.normal(0, math.sqrt(1/2), size=[1]).to(device)
        H_imag = torch.normal(0, math.sqrt(1/2), size=[1]).to(device)
        H = torch.Tensor([[H_real, -H_imag], [H_imag, H_real]]).to(device)
        Tx_sig = torch.matmul(Tx_sig.view(shape[0], -1, 2), H)
        Rx_sig = self.AWGN(Tx_sig, n_var)
        # Channel estimation
        Rx_sig = torch.matmul(Rx_sig, torch.inverse(H)).view(shape)

        return Rx_sig

    def Rician(self, Tx_sig, n_var, K=1):
        shape = Tx_sig.shape
        mean = math.sqrt(K / (K + 1))
        std = math.sqrt(1 / (K + 1))
        H_real = torch.normal(mean, std, size=[1]).to(device)
        H_imag = torch.normal(mean, std, size=[1]).to(device)
        H = torch.Tensor([[H_real, -H_imag], [H_imag, H_real]]).to(device)
        Tx_sig = torch.matmul(Tx_sig.view(shape[0], -1, 2), H)
        Rx_sig = self.AWGN(Tx_sig, n_var)
        # Channel estimation
        Rx_sig = torch.matmul(Rx_sig, torch.inverse(H)).view(shape)

        return Rx_sig

def initNetParams(model):
    '''Init net parameters.'''
    for p in model.parameters():
        if p.dim() > 1:
            nn.init.xavier_uniform_(p)
    return model
         
def subsequent_mask(size):
    "Mask out subsequent positions."
    attn_shape = (1, size, size)
    # 产生下三角矩阵
    subsequent_mask = np.triu(np.ones(attn_shape), k=1).astype('uint8')
    return torch.from_numpy(subsequent_mask)

    
def create_masks(src, trg, padding_idx):

    src_mask = (src == padding_idx).unsqueeze(-2).type(torch.FloatTensor) #[batch, 1, seq_len]

    trg_mask = (trg == padding_idx).unsqueeze(-2).type(torch.FloatTensor) #[batch, 1, seq_len]
    look_ahead_mask = subsequent_mask(trg.size(-1)).type_as(trg_mask.data)
    combined_mask = torch.max(trg_mask, look_ahead_mask)
    
    return src_mask.to(device), combined_mask.to(device)

def loss_function(x, trg, padding_idx, criterion):
    
    loss = criterion(x, trg)
    mask = (trg != padding_idx).type_as(loss.data)
    # a = mask.cpu().numpy()
    loss *= mask
    
    return loss.mean()

def PowerNormalize(x):
    
    x_square = torch.mul(x, x)
    power = torch.mean(x_square).sqrt()
    if power > 1:
        x = torch.div(x, power)
    
    return x


def SNR_to_noise(snr):
    snr = 10 ** (snr / 10)
    noise_std = 1 / np.sqrt(2 * snr)

    return noise_std

def train_step(model, src, trg, n_var, pad, opt, criterion, channel, mi_net=None):
    model.train()

    trg_inp = trg[:, :-1]
    trg_real = trg[:, 1:]

    channels = Channels()
    opt.zero_grad()
    
    src_mask, look_ahead_mask = create_masks(src, trg_inp, pad)
    
    enc_output = model.encoder(src, src_mask)
    channel_enc_output = model.channel_encoder(enc_output)
    Tx_sig = PowerNormalize(channel_enc_output)

    if channel == 'AWGN':
        Rx_sig = channels.AWGN(Tx_sig, n_var)
    elif channel == 'Rayleigh':
        Rx_sig = channels.Rayleigh(Tx_sig, n_var)
    elif channel == 'Rician':
        Rx_sig = channels.Rician(Tx_sig, n_var)
    else:
        raise ValueError("Please choose from AWGN, Rayleigh, and Rician")

    channel_dec_output = model.channel_decoder(Rx_sig)
    dec_output = model.decoder(trg_inp, channel_dec_output, look_ahead_mask, src_mask)
    pred = model.dense(dec_output)
    
    # pred = model(src, trg_inp, src_mask, look_ahead_mask, n_var)
    ntokens = pred.size(-1)
    
    #y_est = x +  torch.matmul(n, torch.inverse(H))
    #loss1 = torch.mean(torch.pow((x_est - y_est.view(x_est.shape)), 2))

    loss = loss_function(pred.contiguous().view(-1, ntokens), 
                         trg_real.contiguous().view(-1), 
                         pad, criterion)

    if mi_net is not None:
        mi_net.eval()
        joint, marginal = sample_batch(Tx_sig, Rx_sig)
        mi_lb, _, _ = mutual_information(joint, marginal, mi_net)
        loss_mine = -mi_lb
        loss = loss + 0.0009 * loss_mine
    # loss = loss_function(pred, trg_real, pad)

    loss.backward()
    opt.step()

    return loss.item()


def train_mi(model, mi_net, src, n_var, padding_idx, opt, channel):
    mi_net.train()
    opt.zero_grad()
    channels = Channels()
    src_mask = (src == padding_idx).unsqueeze(-2).type(torch.FloatTensor).to(device)  # [batch, 1, seq_len]
    enc_output = model.encoder(src, src_mask)
    channel_enc_output = model.channel_encoder(enc_output)
    Tx_sig = PowerNormalize(channel_enc_output)

    if channel == 'AWGN':
        Rx_sig = channels.AWGN(Tx_sig, n_var)
    elif channel == 'Rayleigh':
        Rx_sig = channels.Rayleigh(Tx_sig, n_var)
    elif channel == 'Rician':
        Rx_sig = channels.Rician(Tx_sig, n_var)
    else:
        raise ValueError("Please choose from AWGN, Rayleigh, and Rician")

    joint, marginal = sample_batch(Tx_sig, Rx_sig)
    mi_lb, _, _ = mutual_information(joint, marginal, mi_net)
    loss_mine = -mi_lb

    loss_mine.backward()
    torch.nn.utils.clip_grad_norm_(mi_net.parameters(), 10.0)
    opt.step()

    return loss_mine.item()

def val_step(model, src, trg, n_var, pad, criterion, channel):
    channels = Channels()
    trg_inp = trg[:, :-1]
    trg_real = trg[:, 1:]

    src_mask, look_ahead_mask = create_masks(src, trg_inp, pad)

    enc_output = model.encoder(src, src_mask)
    channel_enc_output = model.channel_encoder(enc_output)
    Tx_sig = PowerNormalize(channel_enc_output)

    if channel == 'AWGN':
        Rx_sig = channels.AWGN(Tx_sig, n_var)
    elif channel == 'Rayleigh':
        Rx_sig = channels.Rayleigh(Tx_sig, n_var)
    elif channel == 'Rician':
        Rx_sig = channels.Rician(Tx_sig, n_var)
    else:
        raise ValueError("Please choose from AWGN, Rayleigh, and Rician")

    channel_dec_output = model.channel_decoder(Rx_sig)
    dec_output = model.decoder(trg_inp, channel_dec_output, look_ahead_mask, src_mask)
    pred = model.dense(dec_output)

    # pred = model(src, trg_inp, src_mask, look_ahead_mask, n_var)
    ntokens = pred.size(-1)
    loss = loss_function(pred.contiguous().view(-1, ntokens), 
                         trg_real.contiguous().view(-1), 
                         pad, criterion)
    # loss = loss_function(pred, trg_real, pad)
    
    return loss.item()
    
def greedy_decode(model, src, n_var, max_len, padding_idx, start_symbol, channel):
    """ 
    这里采用贪婪解码器，如果需要更好的性能情况下，可以使用beam search decode
    """
    # create src_mask
    channels = Channels()
    src_mask = (src == padding_idx).unsqueeze(-2).type(torch.FloatTensor).to(device) #[batch, 1, seq_len]

    enc_output = model.encoder(src, src_mask)
    channel_enc_output = model.channel_encoder(enc_output)
    Tx_sig = PowerNormalize(channel_enc_output)

    if channel == 'AWGN':
        Rx_sig = channels.AWGN(Tx_sig, n_var)
    elif channel == 'Rayleigh':
        Rx_sig = channels.Rayleigh(Tx_sig, n_var)
    elif channel == 'Rician':
        Rx_sig = channels.Rician(Tx_sig, n_var)
    else:
        raise ValueError("Please choose from AWGN, Rayleigh, and Rician")
            
    #channel_enc_output = model.blind_csi(channel_enc_output)
          
    memory = model.channel_decoder(Rx_sig)
    
    outputs = torch.ones(src.size(0), 1).fill_(start_symbol).type_as(src.data)

    for i in range(max_len - 1):
        # create the decode mask
        trg_mask = (outputs == padding_idx).unsqueeze(-2).type(torch.FloatTensor) #[batch, 1, seq_len]
        look_ahead_mask = subsequent_mask(outputs.size(1)).type(torch.FloatTensor)
#        print(look_ahead_mask)
        combined_mask = torch.max(trg_mask, look_ahead_mask)
        combined_mask = combined_mask.to(device)

        # decode the received signal
        dec_output = model.decoder(outputs, memory, combined_mask, None)
        pred = model.dense(dec_output)
        
        # predict the word
        prob = pred[: ,-1:, :]  # (batch_size, 1, vocab_size)
        #prob = prob.squeeze()

        # return the max-prob index
        _, next_word = torch.max(prob, dim = -1)
        #next_word = next_word.unsqueeze(1)
        
        #next_word = next_word.data[0]
        outputs = torch.cat([outputs, next_word], dim=1)

    return outputs


def most_frequent_element_int(tensor1, tensor2, tensor3, tensor4, tensor5):
    # 假设所有输入张量形状相同
    shape = tensor1.shape

    # 初始化估计的tensor数组，这里使用float32以保持与输入张量兼容
    estimated_tensor = torch.zeros(shape, dtype=torch.float32)

    # 32位浮点数的位数，包括符号位
    num_bits = 32

    # 对每个位置进行处理
    for i in range(shape[0]):
        # 获取该位置上五个元素的值，并将它们转换为整数
        values = [int(tensor[i].item()) for tensor in [tensor1, tensor2, tensor3, tensor4, tensor5]]

        # 初始化每一位的计数
        bit_counts = [0] * num_bits

        # 统计每一位的出现次数
        for value in values:
            # 如果值是负数，取其补码
            if value < 0:
                value &= (1 << num_bits) - 1  # 取32位补码

            # 将整数转换为32位二进制字符串
            binary_str = format(value, '032b')

            # 迭代32位并统计
            for j in range(num_bits):
                bit_counts[j] += int(binary_str[j], 2)

        # 按位选择最常见的比特
        estimated_binary_str = ''.join(['1' if count >= 3 else '0' for count in bit_counts])

        # 将估计的二进制字符串转换回整数
        estimated_value = int(estimated_binary_str, 2)

        # 存储估计的值
        estimated_tensor[i] = estimated_value

    return estimated_tensor


def most_frequent_element_float(tensor1, tensor2, tensor3, tensor4, tensor5):
    # 确保所有tensor的形状相同
    assert all(
        t.shape == tensor1.shape for t in [tensor2, tensor3, tensor4, tensor5]), "Tensor shapes must be the same."

    # 初始化中位数张量，与输入tensor有相同的形状和dtype
    median_tensor = torch.zeros_like(tensor1, dtype=torch.float32)

    # 对每个位置计算中位数
    for i in range(tensor1.size(0)):  # 假设tensor1是第一个维度
        values = torch.cat([
            tensor1[i].unsqueeze(0),
            tensor2[i].unsqueeze(0),
            tensor3[i].unsqueeze(0),
            tensor4[i].unsqueeze(0),
            tensor5[i].unsqueeze(0)
        ])
        median_value = torch.median(values).item()  # 计算中位数并转换为Python标量
        median_tensor[i] = round(median_value, 1)  # 四舍五入到一位小数

    return median_tensor


def replace_and_return(string_list_of_lists, tensor_zero, tensor_ji):
    # 初始化结果列表
    result = []

    # 将tensor转换为字符串列表，并格式化为一位小数的字符串
    zero_str_list = [str(int(num)) for num in tensor_zero]
    ji_str_list = ['{:.1f}'.format(num) for num in tensor_ji]

    # 遍历输入的列表中的每个子列表
    for string_list in string_list_of_lists:
        # 对子列表中的每个字符串进行处理
        new_strings = []
        for s in string_list:
            # 替换所有的"零"为tensor_zero中的元素
            while "饕" in s:
                if zero_str_list:
                    s = s.replace("饕", zero_str_list.pop(0), 1)
                else:
                    break  # 如果没有更多的元素来替换，就停止替换

            # 替换所有的"寄"为tensor_ji中的元素
            while "餮" in s:
                if ji_str_list:
                    s = s.replace("餮", ji_str_list.pop(0), 1)
                else:
                    break  # 如果没有更多的元素来替换，就停止替换

            # 将处理后的字符串添加到新字符串列表中
            new_strings.append(s)

        # 将处理后的子列表添加到结果列表中
        result.append(new_strings)

    return result


def float_to_bin(float_num):
    """将双精度浮点数转换为64位二进制字符串"""
    if not isinstance(float_num, float):
        raise TypeError("Input must be a float number")
    # 将float转换为二进制字符串，大端格式的双精度浮点数
    packed = struct.pack('!d', float_num)  # '!d' 表示大端格式的双精度浮点数
    # 将字节转换为二进制字符串，并拼接
    bin_str = ''.join(format(byte, '08b') for byte in packed)
    return bin_str



def calculate_ber_bitwise(tensor1, tensor2):
    """
    计算两个tensor型数组之间的按位误码率。

    参数:
    tensor1 (torch.Tensor): 第一个tensor数组，应为float64类型。
    tensor2 (torch.Tensor): 第二个tensor数组，大小和类型应与tensor1相同。

    返回:
    float: 误码率的数值。
    """
    if tensor1.shape != tensor2.shape:
        raise ValueError("The tensors must have the same shape.")

    # 将tensor中的每个浮点数转换为64位二进制字符串
    bin1 = [float_to_bin(num.item()) for num in tensor1]
    bin2 = [float_to_bin(num.item()) for num in tensor2]

    # 计算不同位数的总数
    error_bits = sum(bin(int(bin_a, 2)) != bin(int(bin_b, 2)) for bin_a, bin_b in zip(bin1, bin2))

    # 总位数 = 张量元素数量 * 64
    total_bits = tensor1.numel() * 64

    # 计算误码率
    ber = error_bits / total_bits

    return ber

########################################################################################################################
def split_sentences(sentences):
    # 分隔中文，整数，小数
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    digits_pattern = re.compile(r'\d+')
    decimal_pattern = re.compile(r'\d+\.\d+')
    cn_sentences = []
    float_numbers = []
    int_numbers = []
    for string in sentences:
        # 扣中文
        chinese_matches = chinese_pattern.findall(string)
        decimal_matches = decimal_pattern.findall(string)
        new_chinese_string = re.sub(decimal_pattern, ' 餮 ', string)
        digits_matches = digits_pattern.findall(new_chinese_string)
        new_chinese_string = re.sub(digits_pattern, ' 餮 ', new_chinese_string)
        cn_sentences.append(new_chinese_string)

        # 扣整数
        for match in digits_matches:
            int_numbers.append(float(match))

        # 扣小数
        for match in decimal_matches:
            float_numbers.append(float(match))

    # 中文转token
    results = []
    for seq in tqdm(cn_sentences):
        words = tokenize(seq, punct_to_keep=[';', ','], punct_to_remove=['?', '.'], remove_digits=True)
        tokens = [token_to_idx[word] for word in words]
        results.append(tokens)

    return results, int_numbers, float_numbers


# def list_to_bytes(lst):
#     # 将列表转换为JSON字符串
#     pickle_str = pickle.dumps(lst)
#     # 将JSON字符串转换为字节流
#     byte_stream = gzip.compress(pickle_str)
#     return byte_stream


# def bytes_to_list(byte_stream):
#     # 将字节流解码为JSON字符串
#     pickle_str = gzip.decompress(byte_stream)
#     # 将JSON字符串解析为列表对象
#     lst = pickle.loads(pickle_str)
#     return lst

def list_2_to_byte_stream(two_d_list):
    byte_stream = b''
    for row in two_d_list:
        for num in row:
            byte_stream += struct.pack('>f', num)  # 大端模式的32位浮点数
    return byte_stream


def byte_stream_to_list_2(byte_stream, num_sublists, num_elements_per_sublist):
    num_bytes_per_element = 4  # 32位浮点数占用4字节
    recovered_2d_list = []

    for _ in range(num_sublists):
        row = []
        for _ in range(num_elements_per_sublist):
            bytes_chunk = byte_stream[:num_bytes_per_element]
            row.append(struct.unpack('>f', bytes_chunk)[0])
            byte_stream = byte_stream[num_bytes_per_element:]
        recovered_2d_list.append(row)

    return recovered_2d_list


def pad_byte_stream(byte_stream, target_length):
    padding_length = target_length - len(byte_stream)

    if padding_length > 0:
        padding = b'\x00' * padding_length
        padded_byte_stream = byte_stream + padding
    else:
        padded_byte_stream = byte_stream  # 不需要补充，直接返回原始字节流

    return padded_byte_stream


def bits_to_floats(bit_stream):
    # 确保比特流长度是4的倍数
    if len(bit_stream) % 32 != 0:
        raise ValueError("比特流长度不是32的倍数")

    # 将比特流分割成每32位一组的子串
    bit_chunks = [bit_stream[i:i+32] for i in range(0, len(bit_stream), 32)]

    # 将每组子串转换为浮点数
    recovered_floats = []
    for bit_chunk in bit_chunks:
        # 将二进制字符串转换为整数，然后转换为4字节的字节串
        bytes_chunk = bytes(int(bit_chunk, 2).to_bytes(4, byteorder='big'))
        # 解析字节串为浮点数
        float_value = struct.unpack('>f', bytes_chunk)[0]
        recovered_floats.append(float_value)

    return recovered_floats


def remove_from_first_zero(byte_stream):
    # 查找第一个字节0的位置
    zero_index = byte_stream.find(b'\x00')

    # 如果找到了字节0，删除它以及之后的所有内容
    if zero_index != -1:
        modified_byte_stream = byte_stream[:zero_index]
    else:
        # 如果没有找到字节0，返回原始字节流
        modified_byte_stream = byte_stream

    return modified_byte_stream


def list_to_bytes(lst):
    Tx_sig, int_1, int_2, int_3,int_4, int_5, float_1, float_2, float_3, float_4, float_5, str_1 = lst
    byte_Tx_sig = list_2_to_byte_stream(Tx_sig[0])
    byte_Tx_sig = pad_byte_stream(byte_Tx_sig, 608)
    byte_int_1 = b''.join(struct.pack('>f', num) for num in int_1)
    byte_int_1 = pad_byte_stream(byte_int_1, 24)
    byte_int_2 = b''.join(struct.pack('>f', num) for num in int_2)
    byte_int_2 = pad_byte_stream(byte_int_2, 24)
    byte_int_3 = b''.join(struct.pack('>f', num) for num in int_3)
    byte_int_3 = pad_byte_stream(byte_int_3, 24)
    byte_int_4 = b''.join(struct.pack('>f', num) for num in int_4)
    byte_int_4 = pad_byte_stream(byte_int_4, 24)
    byte_int_5 = b''.join(struct.pack('>f', num) for num in int_5)
    byte_int_5 = pad_byte_stream(byte_int_5, 24)
    byte_float_1 = b''.join(struct.pack('>f', num) for num in float_1)
    byte_float_1 = pad_byte_stream(byte_float_1, 4)
    byte_float_2 = b''.join(struct.pack('>f', num) for num in float_2)
    byte_float_2 = pad_byte_stream(byte_float_2, 4)
    byte_float_3 = b''.join(struct.pack('>f', num) for num in float_3)
    byte_float_3 = pad_byte_stream(byte_float_3, 4)
    byte_float_4 = b''.join(struct.pack('>f', num) for num in float_4)
    byte_float_4 = pad_byte_stream(byte_float_4, 4)
    byte_float_5 = b''.join(struct.pack('>f', num) for num in float_5)
    byte_float_5 = pad_byte_stream(byte_float_5, 4)
    byte_str = str_1.encode('utf-8')
    byte_stream = byte_Tx_sig + byte_int_1 + byte_int_2 + byte_int_3 + byte_int_4 + byte_int_5 + byte_float_1 + byte_float_2 + byte_float_3 + byte_float_4 + byte_float_5 + byte_str

    return byte_stream


def bytes_to_list(byte_stream):
    first = remove_from_first_zero(byte_stream[0:608])
    Rx_sig = [byte_stream_to_list_2(first, len(first) // 16, 4)]
    int_1 = bits_to_floats(''.join(f'{byte:08b}' for byte in byte_stream[608:632]))
    int_2 = bits_to_floats(''.join(f'{byte:08b}' for byte in byte_stream[632:656]))
    int_3 = bits_to_floats(''.join(f'{byte:08b}' for byte in byte_stream[656:680]))
    int_4 = bits_to_floats(''.join(f'{byte:08b}' for byte in byte_stream[680:704]))
    int_5 = bits_to_floats(''.join(f'{byte:08b}' for byte in byte_stream[704:728]))
    float_1 = bits_to_floats(''.join(f'{byte:08b}' for byte in byte_stream[728:732]))
    float_2 = bits_to_floats(''.join(f'{byte:08b}' for byte in byte_stream[732:736]))
    float_3 = bits_to_floats(''.join(f'{byte:08b}' for byte in byte_stream[736:740]))
    float_4 = bits_to_floats(''.join(f'{byte:08b}' for byte in byte_stream[740:744]))
    float_5 = bits_to_floats(''.join(f'{byte:08b}' for byte in byte_stream[744:748]))
    str_1 = byte_stream[748:].decode('utf-8', errors='replace')
    lst = [Rx_sig, int_1, int_2, int_3, int_4, int_5, float_1, float_2, float_3, float_4, float_5, str_1]
    return lst