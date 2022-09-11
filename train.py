import argparse
import os
import pickle
import random
import string
from constants import START, END, N, RUSSIAN_ALPHABET
from typing import List


def list_to_str(lst: list) -> str:
    return " ".join(lst)


def str_to_list(stg: str) -> list:
    return stg.split()


def check(symbol: str) -> bool:
    return (symbol in string.printable or symbol in RUSSIAN_ALPHABET) and not ()


def tokenize(tokens: str) -> List[str]:
    tokens = tokens.lower()
    tokens = "".join(list(filter(check, list(tokens))))

    for symbol in string.punctuation:
        tokens = tokens.replace(symbol, f" {symbol} ")
    tokens = tokens.split()

    tokens = [START] * (N - 1) + tokens + [END] * (N - 1)
    return tokens


class NGramModel:
    def __init__(self):
        self.n_grams = dict()

    def fit(self, tokens: List[str]):
        for i in range(N, len(tokens) - N + 1):
            n_gram = list_to_str(tokens[i - N: i])
            word = tokens[i]
            if self.n_grams.get(n_gram, None) is None:
                self.n_grams[n_gram] = {}
            if self.n_grams[n_gram].get(word, None) is None:
                self.n_grams[n_gram][word] = 0
            self.n_grams[n_gram][word] += 1

    def generate(self, prefix: str, text_len: int) -> str:
        if len(prefix.split()) > text_len:
            return "Error: Prefix length is longer than text length"
        generated_text = prefix
        if len(prefix) == 0:
            cur_n_gram = str_to_list(random.choice(list(self.n_grams.keys())))
        else:
            cur_n_gram = tokenize(generated_text)[-N - 2:-2]
        for i in range(text_len - len(prefix)):
            print(cur_n_gram)
            print(self.n_grams.get(list_to_str(cur_n_gram), None))

            if self.n_grams.get(list_to_str(cur_n_gram), None) is None:
                cur_n_gram = str_to_list(random.choice(list(self.n_grams.keys())))
                if cur_n_gram[0].isalpha():
                    generated_text += f". {list_to_str(cur_n_gram)}"
                else:
                    generated_text += list_to_str(cur_n_gram)

            weights = list(self.n_grams[list_to_str(cur_n_gram)].values())
            all_cnt = sum(weights)
            for j in range(len(weights)):
                weights[j] /= all_cnt
            next_word = random.choices(list(self.n_grams[list_to_str(cur_n_gram)].keys()), weights)
            next_word = list_to_str(next_word)

            if next_word in string.punctuation:
                generated_text += next_word
            else:
                generated_text += f" {next_word}"

            cur_n_gram = cur_n_gram[1:] + [next_word]

        fixed_generated_text = ""

        j = 0
        while generated_text[j] not in RUSSIAN_ALPHABET and generated_text[j] not in string.ascii_letters:
            j += 1

        for i in range(j, len(generated_text)):
            if generated_text[max(0, i - 2)] in ".!?" or i == j:
                fixed_generated_text += generated_text[i].upper()
            else:
                fixed_generated_text += generated_text[i]

        if fixed_generated_text[-1] not in ".!?":
            fixed_generated_text += "."

        return fixed_generated_text


def save(model: NGramModel, path: str) -> None:
    with open(path, "wb") as file:
        pickle.dump(model, file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Model training")
    parser.add_argument("--input-dir", type=str, default="stdin",
                        help="path to the directory containing the texts. Default - stdin")
    parser.add_argument("--model", type=str, help="path to the file where the model is saved")
    args = parser.parse_args()

    gen_model = NGramModel()
    if args.input_dir == "stdin":
        text = tokenize(input())
        gen_model.fit(text)
    else:
        cnt = 0
        for text_filename in os.listdir(args.input_dir):
            cnt += 1
            with open(f"{args.input_dir}/{text_filename}", "r", encoding="utf-8") as textfile:
                text = textfile.read()
            gen_model.fit(tokenize(text))
    save(gen_model, args.model)
