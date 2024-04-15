import json
import argparse
from utils import DEFAULT_LABELED_FILE

def run(json_file):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print("Error loading inputs:", e)
        exit(1)
    model = data["model"]
    labels = data["labels"]
    lines = []
    for label in labels:
        word = label['word']
        response = '-'.join(label['response'])
        tags = '-'.join(label['label'])
        lines.append(f"{word},{response},{tags}")
    
    print(model)
    print("---------------------------------------")
    print("Word,Response,Labels")
    print("\n".join(lines))
    print("---------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interact with the language model")
    parser.add_argument("--json_file", type=str, default=DEFAULT_LABELED_FILE,
                        help="Words file name")
    args = parser.parse_args()

    run(args.json_file)