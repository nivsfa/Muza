import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import GPT2Tokenizer

import pickle
import os


def read_data(lyrics_path='data/lyrics-data.csv', artists_path='data/artists-data.csv'):
    # Read English lyrics
    print('Reading data...')
    lyrics_data = pd.read_csv(lyrics_path)
    lyrics_data = lyrics_data[lyrics_data['language'] == 'en']
    # Read popular artists
    artists_data = pd.read_csv(artists_path)
    artists_data = artists_data[artists_data['Popularity'] > 5]
    data = lyrics_data.merge(artists_data[['Artist', 'Genres', 'Link']], left_on='ALink', right_on='Link', how='inner')
    data = data.drop(columns=['ALink','SLink','language','Link'])
    return data


def preprocess(data):
    print('Preprocessing...')
    # Keep only not-too-long songs
    data = data[data['Lyric'].apply(lambda x: len(x.split(' ')) < 350)]
    return data


def split_train_test(data):
    # TODO: split using traintestsplit or something
    print('Splitting data to train and test sets...')
    test_set = data.sample(n = 200)
    train_set = data.loc[~data.index.isin(test_set.index)]

    test_set = test_set.reset_index()
    train_set = train_set.reset_index()
    return train_set, test_set


def trim_test_set(test_set):
    # Trim last 20 words in each lyric in the test set (for evaluation)
    test_set['True_end_lyrics'] = test_set['Lyric'].str.split().str[-20:].apply(' '.join)
    test_set['Lyric'] = test_set['Lyric'].str.split().str[:-20].apply(' '.join)
    return test_set


class SongLyrics(Dataset):  
    def __init__(self, control_code, truncate=False, gpt2_type="gpt2", max_length=1024):

        self.tokenizer = GPT2Tokenizer.from_pretrained(gpt2_type)
        self.lyrics = []

        for row in control_code:
          self.lyrics.append(torch.tensor(
                self.tokenizer.encode(f"<|{control_code}|>{row[:max_length]}<|endoftext|>")
            ))               
        if truncate:
            self.lyrics = self.lyrics[:20000]
        self.lyrics_count = len(self.lyrics)
        
    def __len__(self):
        return self.lyrics_count

    def __getitem__(self, item):
        return self.lyrics[item]


if __name__ == '__main__':
    # Create or read train-test split data
    train_test_path = 'data/train-test-data.pickle'
    if not os.path.isfile(train_test_path):
        data = read_data()
        data = preprocess(data)
        train_set, test_set = split_train_test(data)
        test_set = trim_test_set(test_set)
        with open(train_test_path, 'wb') as handle:
            pickle.dump((train_set, test_set), handle)
            print(f'Train and test sets were saved successfully to {train_test_path}.')
    else:
        print('Loading train and test sets...')
        with open(train_test_path, 'rb') as handle:
            train_set, test_set = pickle.load(handle)
    # Create or read train dataset
    dataset_path = 'data/train-dataset.pickle'
    if not os.path.isfile(dataset_path):
        print('Tokenizing lyrics...')
        train_dataset = SongLyrics(train_set['Lyric'], truncate=True, gpt2_type="gpt2")
        with open(dataset_path, 'wb') as handle:
            print(f'Train dataset was saved successfully to {dataset_path}.')
            pickle.dump(train_dataset, handle)
    else:
        print('Loading train dataset...')
        with open(dataset_path, 'rb') as handle:
            train_dataset = pickle.load(handle)
    print(train_dataset.lyrics_count)