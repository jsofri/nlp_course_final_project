from utils import DEFAULT_LABELED_FILE
from data_labeler import Label
import argparse
import json


class Score:
    def __init__(self, label: Label):
        self.num_of_TP = sum(1 for entry in label.labels for lab in entry if lab == "TP")
        self.num_of_FP = sum(1 for entry in label.labels for lab in entry if lab == "FP")
        self.num_of_FN = sum(1 for entry in label.labels for lab in entry if lab == "FN")
        self.num_of_pass = sum(1 for entry in label.labels for lab in entry if lab == "Pass")

        self.num_of_labels = sum(1 for entry in label.labels for _ in entry)

        self.num_of_correct_words = sum(1 for entry in label.labels if all(lab == "TP" for lab in entry))
        self.num_of_words = label.index

    def word_accuracy(self) -> float:
        """
        This accuracy is based on the whole word as follows:
        num of fully-correct decomposed words divided by the number of words

        :return: accuracy
        """
        return self.num_of_correct_words / (self.num_of_words - self.num_of_pass)

    def syllable_accuracy(self) -> float:
        """
        This accuracy is based on the syllables as follows:
        num of correct syllable divided by the number all the syllables found

        :return: accuracy
        """
        return self.num_of_TP / (self.num_of_labels - self.num_of_pass)

    def precision(self) -> float:
        return self.num_of_TP / (self.num_of_TP + self.num_of_FP)

    def recall(self):
        return self.num_of_TP / (self.num_of_TP + self.num_of_FN)

    def f1(self):
        precision = self.precision()
        recall = self.recall()

        return 2 * (precision * recall) / (precision + recall)

    def get_score(self):
        print(f'Accuracy word: {self.word_accuracy()}')
        print(f'Accuracy syllable: {self.syllable_accuracy()}')
        print(f'Precision: {self.precision()}')
        print(f'Recall: {self.recall()}')
        print(f'F1: {self.f1()}')

    """
    Other possible metrics:
    
    Word Error Rate (WER): Measures the proportion of words that are incorrectly decomposed by the model, considering substitutions, insertions, and deletions.
    
    Syllable Error Rate (SER): Similar to WER, but focuses on syllables rather than words.
    
    Mean Absolute Error (MAE): Calculates the average absolute difference between the number of syllables in the model's output and the correct number of syllables.
    
    Root Mean Squared Error (RMSE): Similar to MAE, but takes the square root of the average squared differences between the number of syllables in the model's output and the correct number of syllables.
    """


def run(labels_file: str):
    try:
        with open(labels_file, 'r') as f:
            data = json.load(f)
        labels = Label.from_json(data)
    except Exception as e:
        print("Error loading inputs:", e)
        exit(1)

    score: Score = Score(labels)
    score.get_score()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Score of the data")
    parser.add_argument("--labels", type=str, default=DEFAULT_LABELED_FILE,
                        help="Labels file name")
    '''
    parser.add_argument("--output_file", type=str, default=DEFAULT_SCORE_FILE,
                        help="Output file name")
    '''

    args = parser.parse_args()
    run(args.labels)
