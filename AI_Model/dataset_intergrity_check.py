import os
from datasets import load_from_disk
from transformers import WhisperProcessor

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Dataset",
    "malay_conversational_speech_corpus",
    "validation"
)

#ds = load_dataset("malaysia-ai/malay-conversational-speech-corpus")
#ds = load_dataset("malaysia-ai/malaysian-youtube")
#ds = load_dataset("mesolitica/IMDA-STT")

MODEL_NAME = "mesolitica/malaysian-whisper-tiny"

print("Loading dataset from:", DATASET_PATH)

dataset = load_from_disk(DATASET_PATH)

print("\nDataset loaded successfully")
print(dataset)

print("\nNum rows:", len(dataset))
print("Columns:", dataset.column_names)

sample = dataset[0]

print("\nSAMPLE KEYS:", sample.keys())

print("\nINPUT FEATURES CHECK")
print("Type:", type(sample["input_features"]))
print("Length:", len(sample["input_features"]))

print("\nLABELS CHECK")
print("Type:", type(sample["labels"]))
print("Length:", len(sample["labels"]))

print("\nLoading processor...")
processor = WhisperProcessor.from_pretrained(MODEL_NAME)

print("\nLABEL DECODING CHECK")
decoded = processor.tokenizer.decode(sample["labels"], skip_special_tokens=True)

print(decoded)

print("\n--- REPORT ---")

issues = []

if len(sample["input_features"]) == 0:
    issues.append("Empty input_features")

if len(sample["labels"]) == 0:
    issues.append("Empty labels")

if decoded.strip() == "":
    issues.append("Decoded labels empty or mismatch with tokenizer")

if issues:
    print("ISSUES FOUND:")
    for i in issues:
        print("-", i)
else:
    print("Dataset is structurally valid for Whisper training")