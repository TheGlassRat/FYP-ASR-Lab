#Colab environment code, Do not run locally!!

import torch
from datasets import load_dataset, Audio, DatasetDict
from transformers import AutoProcessor
import os

# 1. Load the dataset
print("Loading dataset...")
ds = load_dataset("malaysia-ai/malay-conversational-speech-corpus")
print("Dataset loaded successfully.")
print(f"Initial dataset structure: {ds}")

# Rename 'filename' column to 'audio' so that the Audio feature can process it
ds = ds.rename_column("filename", "audio")

# Ensure the audio column is properly loaded and resampled to 16kHz
# Whisper models typically expect audio at 16kHz
ds = ds.cast_column("audio", Audio(sampling_rate=16000))
print(f"Dataset structure after casting audio column: {ds}")

# 2. Load the Whisper processor
# Using a small model for demonstration. You might want to choose a larger one for better performance.
model_name = "openai/whisper-small"
processor = AutoProcessor.from_pretrained(model_name)

# 3. Define a preprocessing function
def prepare_dataset(batch):
    # After casting and without num_proc, batch["audio"] is expected to be a dict
    audio_data = batch["audio"]

    # compute log-mel input features from input audio array 
    batch["input_features"] = processor.feature_extractor(audio_data["array"], sampling_rate=audio_data["sampling_rate"]).input_features[0]

    # encode target text to label ids using the 'Y' column
    batch["labels"] = processor.tokenizer(batch["Y"]).input_ids
    return batch

print("\nPreprocessing dataset...")

# Create train and validation splits from the original 'train' split
# 20% of the training data will be used for validation
train_test_split_ds = ds["train"].train_test_split(test_size=0.2, seed=42)

# Apply the preprocessing function to the new splits
# Removed num_proc to avoid serialization issues with Audio feature (defaults to 1 process)
train_ds = train_test_split_ds["train"].map(prepare_dataset, remove_columns=train_test_split_ds["train"].column_names)
validation_ds = train_test_split_ds["test"].map(prepare_dataset, remove_columns=train_test_split_ds["test"].column_names)

# Create a DatasetDict
processed_dataset = DatasetDict({
    "train": train_ds,
    "validation": validation_ds
})

print("\nDataset preprocessing complete.")
print("Processed dataset structure:")
print(processed_dataset)

# 4. Save the processed dataset locally to make it downloadable
output_dir = "./malay_whisper_dataset"
processed_dataset.save_to_disk(output_dir)

print(f"\nProcessed dataset saved to: {output_dir}")
print("You can now download the folder 'malay_whisper_dataset' from your Colab environment.")

# Example of how to load it back if needed:
# from datasets import load_from_disk
# reloaded_ds = load_from_disk("./malay_whisper_dataset")
# print("Reloaded dataset:", reloaded_ds)