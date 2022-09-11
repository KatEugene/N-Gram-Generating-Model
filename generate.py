import argparse
import pickle
from train import NGramModel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generating texts")
    parser.add_argument("--model", type=str, help="path to the file from which the model is loaded")
    parser.add_argument("--prefix", type=str, default="",
                        help="one or more words that will be the beginning of the text")
    parser.add_argument("--length", type=int, help="length of text (including length of prefix)")
    args = parser.parse_args()

    with open(args.model, "rb") as file:
        model = pickle.load(file)

    text = model.generate(args.prefix, args.length)
    print(text)
