import os
import torch
import re
from datasets import load_from_disk, interleave_datasets, concatenate_datasets
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)
import evaluate
from dataclasses import dataclass
from typing import Any, Dict, List, Union

# =========================================================
# CONFIG
# =========================================================
torch.set_default_dtype(torch.float32)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Local Paths
DATA_PATH = os.path.join(BASE_DIR, "Dataset", "whisper_bilingual_feedback_ready")
GROUNDING_DATA_PATH = os.path.join(BASE_DIR, "Dataset", "malay_conversational_speech_corpus", "train")

MODEL_ID = "mesolitica/malaysian-whisper-small-v2"
processor = WhisperProcessor.from_pretrained(MODEL_ID)

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any
    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        input_features = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
        label_features = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        batch["labels"] = labels
        return batch

def compute_metrics(pred):
    metric = evaluate.load("wer")
    label_ids = pred.label_ids
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
    preds = processor.tokenizer.batch_decode(pred.predictions, skip_special_tokens=True)
    refs = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)
    return {"wer": metric.compute(predictions=preds, references=refs)}

# =========================================================
# LOADING DATA
# =========================================================
print("Loading Local Datasets...")
synth_ds = load_from_disk(DATA_PATH)
real_ds = load_from_disk(GROUNDING_DATA_PATH)
cols = ["input_features", "labels"]

# =========================================================
# EXPERIMENT LOOP (5 VARIATIONS)
# =========================================================
proportions = [
    (1.0, 0.0), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.0, 1.0)
]
TOTAL_SAMPLES = 800 

for s_ratio, r_ratio in proportions:
    s_label = int(s_ratio * 100)
    r_label = int(r_ratio * 100)
    variant_name = f"mesolitica_small_v2_S{s_label}_R{r_label}"
    output_dir = os.path.join(BASE_DIR, "models", variant_name)
    
    print(f"\nTraining Mesolitica Variant: {variant_name}")
    
    s_count = int(TOTAL_SAMPLES * s_ratio)
    r_count = int(TOTAL_SAMPLES * r_ratio)
    
    shards = []
    if s_count > 0: shards.append(synth_ds.shuffle(seed=42).select(range(min(s_count, len(synth_ds)))).select_columns(cols))
    if r_count > 0: shards.append(real_ds.shuffle(seed=42).select(range(min(r_count, len(real_ds)))).select_columns(cols))
    
    train_ds = concatenate_datasets(shards).shuffle(seed=42)

    model = WhisperForConditionalGeneration.from_pretrained(MODEL_ID).to(DEVICE)
    model.config.forced_decoder_ids = None

    # Mixed precision handling
    has_cuda = torch.cuda.is_available()
    bf16_ready = has_cuda and torch.cuda.is_bf16_supported()

    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=2,
        num_train_epochs=1,
        learning_rate=1e-5,
        warmup_steps=20,
        eval_strategy="no",
        save_strategy="epoch",
        save_total_limit=1,
        predict_with_generate=False,
        fp16=has_cuda and not bf16_ready,
        bf16=bf16_ready,
        push_to_hub=False,
        report_to="none",
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        data_collator=DataCollatorSpeechSeq2SeqWithPadding(processor),
    )

    trainer.train()
    model.save_pretrained(output_dir)
    processor.save_pretrained(output_dir)
    print(f"Mesolitica Variant saved to {output_dir}")
