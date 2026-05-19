import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

class AudioProcessor:
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