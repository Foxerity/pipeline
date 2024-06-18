# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author: Huiqiang Xie
@File: text_preprocess.py
@Time: 2021/3/31 22:14
"""
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 16:44:08 2020

@author: hx301
"""
import re
import pickle
import argparse
import os
import json
from tqdm import tqdm
import jieba
import random


parser = argparse.ArgumentParser()
parser.add_argument('--input-data-dir', default='europarl/zhongqiang', type=str)
parser.add_argument('--output-train-dir', default='europarl/train_data.pkl', type=str)
parser.add_argument('--output-test-dir', default='europarl/test_data.pkl', type=str)
parser.add_argument('--output-vocab', default='europarl/vocab.json', type=str)

SPECIAL_TOKENS = {
    '<PAD>': 0,
    '<START>': 1,
    '<END>': 2,
    '<UNK>': 3,
}


def process(text_path):
    fop = open(text_path, 'r', encoding='utf8')
    raw_data = fop.read()
    sentences = raw_data.strip().split('\n')
    raw_data_input = [data for data in sentences]
    fop.close()
    return raw_data_input


def tokenize(s, delim=' ', add_start_token=True, add_end_token=True,
             punct_to_keep=None, punct_to_remove=None, remove_digits=True):
    """
    Tokenize a sequence, converting a string s into a list of (string) tokens by
    splitting on the specified delimiter. Optionally keep or remove certain
    punctuation marks and add start and end tokens.
    """
    if punct_to_keep is not None:
        for p in punct_to_keep:
            s = s.replace(p, '%s%s' % (delim, p))

    if punct_to_remove is not None:
        for p in punct_to_remove:
            s = s.replace(p, '')

    if remove_digits:
        s = re.sub(r'\d+', '零', s)

    tokens = jieba.lcut(s)
    if add_start_token:
        tokens.insert(0, '\u003cSTART\u003e')
    if add_end_token:
        tokens.append('\u003cEND\u003e')
    return tokens


def build_vocab(sequences, token_to_idx={}, min_token_count=1, delim=' ',
                punct_to_keep=None, punct_to_remove=None, remove_digits=True):
    token_to_count = {}

    for seq in sequences:
        seq_tokens = tokenize(seq, delim=delim, punct_to_keep=punct_to_keep,
                              punct_to_remove=punct_to_remove,
                              add_start_token=False, add_end_token=False, remove_digits=remove_digits)
        for token in seq_tokens:
            if token not in token_to_count:
                token_to_count[token] = 0
            token_to_count[token] += 1

    for token, count in sorted(token_to_count.items()):
        if count >= min_token_count:
            token_to_idx[token] = len(token_to_idx)

    return token_to_idx


def encode(seq_tokens, token_to_idx, allow_unk=False):
    seq_idx = []
    for token in seq_tokens:
        if token not in token_to_idx:
            if allow_unk:
                token = '<UNK>'
            else:
                raise KeyError('Token "%s" not in vocab' % token)
        seq_idx.append(token_to_idx[token])
    return seq_idx


def decode(seq_idx, idx_to_token, delim=None, stop_at_end=True):
    tokens = []
    for idx in seq_idx:
        tokens.append(idx_to_token[idx])
        if stop_at_end and tokens[-1] == '<END>':
            break
    if delim is None:
        return tokens
    else:
        return delim.join(tokens)


def main(args):
    data_dir = './'
    args.input_data_dir = data_dir + args.input_data_dir
    args.output_train_dir = data_dir + args.output_train_dir
    args.output_test_dir = data_dir + args.output_test_dir
    args.output_vocab = data_dir + args.output_vocab

    sentences = []
    print('Preprocess Raw Text')
    for fn in tqdm(os.listdir(args.input_data_dir)):
        if not fn.endswith('.txt'): continue
        process_sentences = process(os.path.join(args.input_data_dir, fn))
        sentences += process_sentences

    # remove the same sentences
    # a = {}
    # for set in sentences:
    #     if set not in a:
    #         a[set] = 0
    #     a[set] += 1
    # sentences = list(a.keys())
    # print('Number of sentences: {}'.format(len(sentences)))

    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    digits_pattern = re.compile(r'\d+')
    decimal_pattern = re.compile(r'\d+\.\d+')
    cn_sentences = []
    float_numbers = []
    int_numbers = []
    for string in sentences:
        # 使用正则表达式找到所有汉字和数字
        chinese_matches = chinese_pattern.findall(string)
        decimal_matches = decimal_pattern.findall(string)
        new_chinese_string = re.sub(decimal_pattern, '寄', string)
        digits_matches = digits_pattern.findall(new_chinese_string)
        new_chinese_string = re.sub(digits_pattern, '零', new_chinese_string)

        cn_sentences.append(new_chinese_string)

        for match in digits_matches:
            int_numbers.append(float(match))

            # 对于小数，它们已经是浮点数格式，直接保存
        for match in decimal_matches:
            float_numbers.append(float(match))
    # print(cn_sentences)
    # print(int_numbers)
    # print(float_numbers)

    print('Build Vocab')
    token_to_idx = build_vocab(
        cn_sentences, SPECIAL_TOKENS,
        punct_to_keep=[';', ','], punct_to_remove=['?', '.']
    )
    print(token_to_idx)

    vocab = {'token_to_idx': token_to_idx}
    print('Number of words in Vocab: {}'.format(len(token_to_idx)))
    print(vocab)

    # save the vocab
    if args.output_vocab != '':
        with open(args.output_vocab, 'w') as f:
            json.dump(vocab, f)

    print('Start encoding txt')
    results = []
    for seq in tqdm(cn_sentences):
        words = tokenize(seq, punct_to_keep=[';', ','], punct_to_remove=['?', '.'], remove_digits=True)
        tokens = [token_to_idx[word] for word in words]
        results.append(tokens)
    # print(results)

    random.shuffle(results)

    print('Writing Data')
    train_data = results[: round(len(results) * 0.9)]
    test_data = results[round(len(results) * 0.9):]

    with open(args.output_train_dir, 'wb') as f:
        pickle.dump(train_data, f)
    with open(args.output_test_dir, 'wb') as f:
        pickle.dump(test_data, f)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
