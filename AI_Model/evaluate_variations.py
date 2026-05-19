import os
import torch
import librosa
import time
import matplotlib.pyplot as plt
import numpy as np
from datasets import load_dataset, Audio
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import evaluate
from tqdm import tqdm

# Constants
REAL_DATASET = "malaysia-ai/malay-conversational-speech-corpus"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def evaluate_model(model_path, processor, test_ds):
    model = WhisperForConditionalGeneration.from_pretrained(model_path).to(DEVICE)
    metric = evaluate.load("wer")
    
    predictions = []
    references = []
    total_time = 0
    # Calculate throughput based on 30s blocks.
    total_duration = 0 
    
    for batch in tqdm(test_ds, desc=f"Evaluating {model_path}"):
        input_features = torch.tensor([batch["input_features"]]).to(DEVICE, dtype=model.dtype)
        reference_text = processor.decode(batch["labels"], skip_special_tokens=True)
        
        # Audio is pre-processed into 30s chunks for Whisper
        total_duration += 30.0 
        
        start_time = time.perf_counter()
        with torch.no_grad():
            generated_ids = model.generate(input_features)
            transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        total_time += (time.perf_counter() - start_time)
            
        predictions.append(transcription)
        references.append(reference_text)
        
    # Final Metric Calculation
    # metric.compute returns a float (0.0 to 1.0), scale to %
    wer_value = metric.compute(predictions=predictions, references=references)
    wer_score = 100 * wer_value
    
    # RTFx calculation: Audio Duration / Processing Time
    rtfx = total_duration / total_time if total_time > 0 else 0
    
    print(f"\n[METRICS] {model_path}:")
    print(f" - WER: {wer_score:.2f}%")
    print(f" - RTFx: {rtfx:.2f}x (processed {total_duration:.1f}s in {total_time:.1f}s)")
    
    return wer_score, rtfx

def save_visualizations(results, variations):
    providers = list(results.keys())
    x = np.arange(len(variations))
    width = 0.35
    
    # 1. WER Plot
    plt.figure(figsize=(12, 6))
    for i, provider in enumerate(providers):
        wers = [results[provider][var][0] if var in results[provider] else 0 for var in variations]
        plt.bar(x + (i * width) - width/2, wers, width, label=f"{provider.capitalize()} WER")
    
    plt.xlabel('Dataset Variation')
    plt.ylabel('WER (%)')
    plt.title('Word Error Rate comparison')
    plt.xticks(x, variations)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(BASE_DIR, 'wer_comparison.png'))
    plt.close()

    # 2. RTFx Plot
    plt.figure(figsize=(12, 6))
    for i, provider in enumerate(providers):
        rtfs = [results[provider][var][1] if var in results[provider] else 0 for var in variations]
        plt.bar(x + (i * width) - width/2, rtfs, width, label=f"{provider.capitalize()} RTFx")
    
    plt.xlabel('Dataset Variation')
    plt.ylabel('Real Time Factor Multiplier (RTFx)')
    plt.title('Inference Speed Comparison (RTFx)')
    plt.xticks(x, variations)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(BASE_DIR, 'rtfx_comparison.png'))
    plt.close()
    print(f"Visualizations generated: wer_comparison.png, rtfx_comparison.png")

def run_benchmark():
    # Load Test Data (Real data subset not seen during training)
    print("Loading Benchmark Test Data (Malaysian Conversational)...")
    # Target the validation split directly
    dataset_path = os.path.join(BASE_DIR, "malay_conversational_speech_corpus", "validation")
    if not os.path.exists(dataset_path):
        dataset_path = os.path.join(BASE_DIR, "Dataset", "malay_conversational_speech_corpus", "validation")

    try:
        from datasets import load_from_disk
        ds = load_from_disk(dataset_path)
        print(f"Loaded dataset from: {dataset_path}")
    except Exception as e:
        print(f"Failed to load from disk: {e}. Loading from Hub: {REAL_DATASET}")
        # Use validation split instead of train
        ds = load_dataset(REAL_DATASET, split="validation", streaming=False)
    
    # Use the entire dataset for evaluation
    test_ds = ds
    
    variations = ["Baseline", "S100_R0", "S75_R25", "S50_R50", "S25_R75", "S0_R100"]
    huggingface_models = {
        "openai": "openai/whisper-small",
        "mesolitica": "mesolitica/malaysian-whisper-small-v2"
    }
    base_models = {
        "openai": "openai_small",
        "mesolitica": "mesolitica_small_v2"
    }
    
    results = {}
    
    for provider, prefix in base_models.items():
        results[provider] = {}
        if provider == "openai":
            proc = WhisperProcessor.from_pretrained("openai/whisper-small", language="Malay", task="transcribe")
        else:
            proc = WhisperProcessor.from_pretrained("mesolitica/malaysian-whisper-small-v2")
            
        for var in variations:
            if var == "Baseline":
                model_identifier = huggingface_models[provider]
                print(f"Evaluating Baseline model for {provider}: {model_identifier}")
                wer, rtfx = evaluate_model(model_identifier, proc, test_ds)
                results[provider][var] = (wer, rtfx)
                print(f"DEBUG: {provider} Baseline -> WER: {wer:.2f}%, RTFx: {rtfx:.2f}x")
            else:
                model_dir = os.path.join(BASE_DIR, "models", f"{prefix}_{var}")
                if os.path.exists(model_dir):
                    wer, rtfx = evaluate_model(model_dir, proc, test_ds)
                    results[provider][var] = (wer, rtfx)
                    print(f"Result for {provider} {var}: WER {wer:.2f}, RTFx {rtfx:.2f}")
                else:
                    print(f"Model variant {model_dir} not found. Skipping.")

    # Generate charts
    save_visualizations(results, variations)

    print("\n" + "="*50)
    print("FINAL COMPARISON RESULTS (WER & RTFx)")
    print("="*50)
    print(f"{'Variation':<15} | {'OpenAI (WER/RTFx)':<18} | {'Mesolitica (WER/RTFx)':<18}")
    print("-" * 60)
    for var in variations:
        o_res = f"{results['openai'][var][0]:.2f} / {results['openai'][var][1]:.2f}" if var in results['openai'] else "N/A"
        m_res = f"{results['mesolitica'][var][0]:.2f} / {results['mesolitica'][var][1]:.2f}" if var in results['mesolitica'] else "N/A"
        print(f"{var:<15} | {o_res:<18} | {m_res:<18}")

if __name__ == "__main__":
    run_benchmark()
