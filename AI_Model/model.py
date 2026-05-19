import os
import torch
import threading
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from datasets import Audio
from jiwer import wer

# Global lock to prevent simultaneous transformers loading
load_lock = threading.Lock()

class WhisperASR:
    """
    Unified Inference Engine for Malaysian Multilingual ASR Research.
    Handles Model loading, Audio Processing (Visuals), and Metrics (WER).
    """
    def __init__(self, model_key="mesolitica_base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        current_dir = os.path.dirname(__file__)
        
        self.model_map = {
            "openai_base": "openai/whisper-small",
            "mesolitica_base": "mesolitica/malaysian-whisper-small-v2",
        }
        
        if model_key in self.model_map:
            load_path = self.model_map[model_key]
        else:
            load_path = os.path.join(current_dir, "models", model_key)
            if not os.path.exists(load_path):
                alt_path = os.path.join(os.getcwd(), "AI_Model", "models", model_key)
                if os.path.exists(alt_path):
                    load_path = alt_path

        display_path = os.path.relpath(load_path) if os.path.isabs(load_path) else load_path
        print(f"LOADING ENGINE: {model_key} FROM {display_path}")
        
        try:
            with load_lock:
                self.processor = AutoProcessor.from_pretrained(load_path)
                self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    load_path,
                    low_cpu_mem_usage=False,
                    device_map=None
                )
            
            self.model = self.model.to(self.device).to(dtype=torch.float32)
            self.model.eval()
            print(f"SUCCESS: {model_key} READY")
        except Exception as e:
            print(f"FAILURE: Could not load {model_key} - {e}")
            raise RuntimeError(f"Model Load Failed ({model_key}): {str(e)}")

        self.audio = Audio(sampling_rate=16000)

    def transcribe_array(self, audio_array):
        """
        Transcribes audio array. Handles Malay/English code-switching.
        """
        inputs = self.processor(audio_array, sampling_rate=16000, return_tensors="pt")
        input_features = inputs["input_features"].to(self.device, dtype=torch.float32)

        with torch.no_grad():
            generated_outputs = self.model.generate(
                input_features,
                max_length=128,
                task="transcribe",
                return_dict_in_generate=True,
                output_scores=True
            )

        generated_ids = generated_outputs.sequences
        text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        scores = generated_outputs.scores
        if not scores:
            return text.strip(), 0.0

        token_probs = []
        seq_len = generated_ids.shape[1]
        num_scores = len(scores)
        prefix_len = seq_len - num_scores
        
        for i in range(num_scores):
            token_id = generated_ids[0][prefix_len + i]
            probs = torch.softmax(scores[i][0], dim=-1)
            prob = probs[token_id].item()
            token_probs.append(prob)
        
        confidence = sum(token_probs) / len(token_probs) if token_probs else 0.8
        return text.strip(), float(confidence)

    @staticmethod
    def calculate_wer(reference, hypothesis):
        """
        Calculates Word Error Rate (WER) using jiwer.
        """
        try:
            return wer(reference, hypothesis)
        except Exception as e:
            print(f"WER Calculation error: {e}")
            return 1.0

    @staticmethod
    def generate_visuals(audio_path):
        """
        Generates spectrogram and MFCC visualizations for a given audio file.
        Returns a dict of base64 encoded PNG strings.
        """
        try:
            y, sr = librosa.load(audio_path, sr=16000)
            
            # 1. Spectrogram
            plt.figure(figsize=(10, 4))
            S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
            S_dB = librosa.power_to_db(S, ref=np.max)
            librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000)
            plt.title('Mel-frequency Spectrogram')
            plt.tight_layout()
            
            spec_io = io.BytesIO()
            plt.savefig(spec_io, format='png')
            spec_io.seek(0)
            spec_base64 = base64.b64encode(spec_io.read()).decode('utf-8')
            plt.close()
            
            # 2. MFCC
            plt.figure(figsize=(10, 4))
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            librosa.display.specshow(mfccs, x_axis='time')
            plt.title('MFCC')
            plt.tight_layout()
            
            mfcc_io = io.BytesIO()
            plt.savefig(mfcc_io, format='png')
            mfcc_io.seek(0)
            mfcc_base64 = base64.b64encode(mfcc_io.read()).decode('utf-8')
            plt.close()
            
            return {
                "spectrogram": spec_base64,
                "mfcc": mfcc_base64
            }
        except Exception as e:
            print(f"Visualization error: {e}")
            return None