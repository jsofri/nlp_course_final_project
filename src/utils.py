import os
import json
from typing import Union
from together import Together
from pydantic import BaseModel, Field

# constants

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
ROOT_FOLDER = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ROOT_FOLDER, "data")
CACHE_DIR = os.path.join(ROOT_FOLDER, "cache")
DEFAULT_AUTOGENERATED_SYLLABLES_FILE = os.path.join(DATA_DIR, "autogenerated_syllables.json")
DEFAULT_AUTOGENERATED_WORDS_FILE = os.path.join(DATA_DIR, "autogenerated_words.json")
DEFAULT_AUTOGENERATED_EXPERIMENT_FILE = os.path.join(DATA_DIR, "autogenerated_experiment.json")
DEFAULT_LABELED_FILE = os.path.join(DATA_DIR, "labeled_experiment.json")
API_TOKEN_FILE = os.path.join(ROOT_FOLDER, "api_token.txt")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


# classes


class Syllable:
    def __init__(self, syllable: str, template: str):
        self.syllable = syllable
        self.template = template

    def to_json(self) -> dict[str, str]:
        return {
            "syllable": self.syllable,
            "template": self.template
        }

    @staticmethod
    def list_to_json(syllables) -> list[dict]:
        return [s.to_json() for s in syllables]

    @staticmethod
    def json_to_list(json_data) -> list["Syllable"]:
        return [Syllable(syllable=s["syllable"], template=s["template"]) for s in json_data]


class Word:
    def __init__(self, syllables: list["Syllable"]):
        self.syllables = syllables
        self.word = ''.join([s.syllable for s in syllables])

    def to_json(self) -> dict:
        return {
            "word": self.word,
            "syllables": [s.to_json() for s in self.syllables]
        }

    @staticmethod
    def from_json(data: dict) -> "Word":
        return Word(syllables=Syllable.json_to_list(data["syllables"]))

    @staticmethod
    def list_to_json(words: list["Word"]) -> list[dict]:
        return [w.to_json() for w in words]

    @staticmethod
    def json_to_list(data: list[dict]) -> list["Word"]:
        return [Word(Syllable.json_to_list(w["syllables"])) for w in data]


class InstructionContainer:
    def __init__(self, instruction: str, word: Word):
        self.instruction = instruction
        self.word = word
        self.full_prompt = f"{instruction} \"{word.word}\""
        self.response = {}

    def to_json(self) -> dict:
        return {
            "instruction": self.instruction,
            "word": self.word.to_json(),
            "response": self.response,
            "full_prompt": self.full_prompt
        }

    @classmethod
    def generate_cls(cls, instruction: str, word: Word, response: dict, full_prompt: str) -> "InstructionContainer":
        obj = cls(instruction, word)
        obj.response = response
        obj.full_prompt = full_prompt
        return obj

    @staticmethod
    def list_to_json(responses: list["InstructionContainer"]) -> list[dict]:
        return [r.to_json() for r in responses]

    @staticmethod
    def json_to_list(json_data: list[dict]) -> list["InstructionContainer"]:
        return [InstructionContainer.generate_cls(r["instruction"], Word.from_json(r["word"]),
                                                  r["response"], r["full_prompt"]) for r in json_data]


class PromptsGenerator:
    def __init__(self):
        self.notes = None
        self.instructions = self.DEFAULT_PROMPT

    def get_instruction_wrapper(self, word: Word) -> InstructionContainer:
        return InstructionContainer(instruction=self.instructions, word=word)


class Experiment:
    def __init__(self, instructions: list[InstructionContainer], model_name: str):
        self.instructions = instructions
        self.model_name = model_name

    def to_json(self):
        data = {
            "instruction_containers": InstructionContainer.list_to_json(self.instructions),
            "model_name": self.model_name
        }
        return data

    @staticmethod
    def from_json(data: dict) -> "Experiment":
        results = InstructionContainer.json_to_list(data["instruction_containers"])
        model_name = data["model_name"]
        return Experiment(results, model_name)

# together API related code

__KEY_SYLLABLES = "syllables"
__KEY_EXPLANATION = "explanation"
__SYSTEM_CONTENT = f"The response should be in JSON, the final answer in '{__KEY_SYLLABLES}' (single key), "\
                   f"and any explanation in '{__KEY_EXPLANATION}'."
class __User(BaseModel):
    syllables: str = Field(description="syllables")
    explanation: str = Field(description="explanation")


__api_key = os.environ.get("TOGETHER_API_KEY")
if not __api_key:
    with open(API_TOKEN_FILE, "r") as f:
        __api_key = f.read().strip()

__client = Together(api_key=__api_key)


def chat_completion(question: str, model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    as_json: bool=True) -> Union[str, dict]:
    # based on https://github.com/togethercomputer/together-python
    if as_json:
        response = __client.chat.completions.create(
        model=model,
        response_format={"type": "json_object", "schema": __User.model_json_schema()},
        messages=[{"role": "system", "content": __SYSTEM_CONTENT},
                  {"role": "user", "content": question}],
        )
        result = json.loads(response.choices[0].message.content)
    else:
        response = __client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
        )
        result = response.choices[0].message.content
    return result
