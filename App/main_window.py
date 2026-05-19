import os
import time
import shutil
import numpy as np
import sounddevice as sd
import soundfile as sf
import base64
from PySide6.QtWidgets import (
    QMainWindow, QMessageBox, QTableWidgetItem, 
    QFileDialog, QWidget, QLineEdit, QApplication
)
from PySide6.QtCore import Qt, QTimer, QSize, QThread, Signal
from PySide6.QtGui import QPixmap, QImage, QIcon, QPainter, QColor

import csv

from .ui_main import Ui_Main
from .ui_feedback import Ui_Feedback
from .ui_comparison import Ui_Comparison
from .ui_history import Ui_History
from .ui_settings import Ui_Settings
from .ui_validation_dialog import ValidationDialog
from .ui_busy_dialog import BusyDialog

from .Database.db_manager import DBManager
from AI_Model.model import WhisperASR
from .styles import DARK_THEME, LIGHT_THEME, SUCCESS, WARNING, DANGER

class TranscriptionThread(QThread):
    finished = Signal(str, float)
    error = Signal(str)

    def __init__(self, model, audio_np):
        super().__init__()
        self.model = model
        self.audio_np = audio_np

    def run(self):
        try:
            text, conf = self.model.transcribe_array(self.audio_np)
            self.finished.emit(text, conf)
        except Exception as e:
            self.error.emit(str(e))

class ComparisonThread(QThread):
    row_updated = Signal(int, str, str, str, str, str, str) # row, status, text, conf, lat, wer, rtfx
    finished = Signal()

    def __init__(self, models, audio_path, validation_text):
        super().__init__()
        self.models = models
        self.audio_path = audio_path
        self.validation_text = validation_text

    def run(self):
        try:
            audio_info = sf.info(self.audio_path)
            audio_duration = audio_info.duration
            audio_np, _ = sf.read(self.audio_path)
            
            # models is a list of (row_index, model_key, model_obj)
            for row_idx, model_key, model_obj in self.models:
                # Use perf_counter for precise benchmark measurement
                start = time.perf_counter()
                try:
                    text, conf = model_obj.transcribe_array(audio_np)
                    lat = time.perf_counter() - start
                    
                    # RTFx (Real-Time Factor Multiplier) = processed_audio_duration / latency
                    # Note: Current model implementation (transcribe_array) only processes the first 30s.
                    # We cap the duration at 30.0 for accuracy, as any audio beyond that is ignored by the engine.
                    processed_duration = min(audio_duration, 30.0)
                    rtfx = processed_duration / lat if lat > 0 else 0
                    error_rate = "-"
                    if self.validation_text:
                        try:
                            # Scale by 100 to match the benchmark evaluator (% scale)
                            error_rate = f"{WhisperASR.calculate_wer(self.validation_text, text) * 100:.2f}%"
                        except: error_rate = "Err"
                    
                    self.row_updated.emit(row_idx, "Completed", text, f"{conf*100:.1f}%", f"{lat:.2f}s", str(error_rate), f"{rtfx:.2f}x")
                except Exception as e:
                    self.row_updated.emit(row_idx, f"FAILED: {str(e)[:20]}", "-", "-", "-", "-", "-")
        except Exception as e:
            print(f"Comparison Thread Major Error: {e}")
        finally:
            self.finished.emit()

class ModelLoaderThread(QThread):
    progress_signal = Signal(str, int, str)
    finished_signal = Signal(str, object)

    def __init__(self, model_key):
        super().__init__()
        self.model_key = model_key

    def run(self):
        try:
            self.progress_signal.emit(self.model_key, 0, "Initializing...")
            model = WhisperASR(model_key=self.model_key)
            self.progress_signal.emit(self.model_key, 100, "Loaded")
            self.finished_signal.emit(self.model_key, model)
        except Exception as e:
            self.progress_signal.emit(self.model_key, 0, f"Error: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ASR system") 
        self.resize(1300, 950)

        # Storage
        self.assets_dir = os.path.join(os.path.dirname(__file__), "Assets")
        self.cache_dir = os.path.join(os.path.dirname(__file__), "Cache")
        self.storage_dir = os.path.join(os.path.dirname(__file__), "Recordings")
        
        self.clean_cache() # Clear at startup
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.storage_dir, exist_ok=True)

        # UI Shell
        self.ui = Ui_Main()
        self.setCentralWidget(self.ui)
        
        # Pages
        self.feedback_ui = Ui_Feedback()
        self.comparison_ui = Ui_Comparison()
        self.history_ui = Ui_History()
        self.settings_ui = Ui_Settings()
        
        self.ui.content_stack.addWidget(self.feedback_ui)
        self.ui.content_stack.addWidget(self.comparison_ui)
        self.ui.content_stack.addWidget(self.history_ui)
        self.ui.content_stack.addWidget(self.settings_ui)

        # Backend
        self.db = DBManager()
        self.models = {}
        self.is_dark = True
        self.available_model_keys = [
            "openai_base", "mesolitica_base",
            "openai_small_S100_R0", "openai_small_S75_R25", "openai_small_S50_R50", "openai_small_S25_R75", "openai_small_S0_R100",
            "mesolitica_small_v2_S100_R0", "mesolitica_small_v2_S75_R25", "mesolitica_small_v2_S50_R50", "mesolitica_small_v2_S25_R75", "mesolitica_small_v2_S0_R100"
        ]
        
        # Audio State
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.current_audio_path = None
        self.current_history_id = None
        self.validation_text = ""
        
        # Player State
        self.is_playing = False
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.update_playback_ui)
        self.active_player_refs = None

        # Smooth Recording Timer (60 fps)
        self.record_timer = QTimer()
        self.record_timer.timeout.connect(self.update_record_status)
        self.record_duration_ms = 0
        self.RECORD_LIMIT_MS = 30000

        self.apply_theme()
        self.connect_signals()
        self.init_model_loading()

    def clean_cache(self):
        """Silently cleans the cache directory without interrupting with permission errors."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
            return

        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    # Try to rename first, often overcomes lazy locks on Windows
                    temp_name = file_path + ".deleted"
                    os.rename(file_path, temp_name)
                    os.remove(temp_name)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path, ignore_errors=True)
            except Exception:
                pass # Skip if still in use

    def init_model_loading(self):
        self.model_ui_refs = {}
        self.loading_threads = []
        
        comp_table = self.comparison_ui.table
        comp_table.setRowCount(0)
        
        for key in self.available_model_keys:
            # Settings Page Status
            refs = self.settings_ui.add_model_status(key)
            self.model_ui_refs[key] = refs
            
            # Predict Page Selector
            self.feedback_ui.model_selector.addItem(key)
            
            # Comparison Hub Row
            row = comp_table.rowCount()
            comp_table.insertRow(row)
            comp_table.setRowHeight(row, 50)
            item = QTableWidgetItem(key)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked) 
            comp_table.setItem(row, 0, item)
            comp_table.setItem(row, 1, QTableWidgetItem("Initializing..."))
            comp_table.setItem(row, 2, QTableWidgetItem("-"))
            comp_table.setItem(row, 3, QTableWidgetItem("-"))
            comp_table.setItem(row, 4, QTableWidgetItem("-"))
            comp_table.setItem(row, 5, QTableWidgetItem("-"))
            comp_table.setItem(row, 6, QTableWidgetItem("-"))

            # Parallel Threaded Loader
            thread = ModelLoaderThread(key)
            thread.progress_signal.connect(self.on_model_progress)
            thread.finished_signal.connect(self.on_model_finished)
            thread.start()
            self.loading_threads.append(thread)

    def on_model_progress(self, key, val, status):
        prog, lbl = self.model_ui_refs[key]
        if val == 0: prog.setRange(0, 0)
        else:
            prog.setRange(0, 100)
            prog.setValue(val)
        lbl.setText(status)

    def on_model_finished(self, key, model_or_error):
        prog, lbl = self.model_ui_refs[key]
        comp_table = self.comparison_ui.table
        
        # Find row in comparison table
        row_idx = -1
        for i in range(comp_table.rowCount()):
            if comp_table.item(i, 0).text() == key:
                row_idx = i
                break

        if isinstance(model_or_error, WhisperASR):
            self.models[key] = model_or_error
            prog.setRange(0, 100)
            prog.setValue(100)
            lbl.setText("LOADED")
            lbl.setToolTip("Model is ready for inference")
            if row_idx != -1:
                st_item = QTableWidgetItem("Ready")
                st_item.setForeground(QColor("#4caf50"))
                comp_table.setItem(row_idx, 1, st_item)
            self.update_predict_status()
        else:
            # Error case
            prog.setRange(0, 100)
            prog.setValue(0)
            error_msg = str(model_or_error)
            lbl.setText(f"FAILED")
            lbl.setToolTip(error_msg)
            if row_idx != -1:
                err_item = QTableWidgetItem(f"LOAD ERROR")
                err_item.setToolTip(error_msg)
                err_item.setForeground(QColor("#cf6679"))
                comp_table.setItem(row_idx, 1, err_item)
            self.update_predict_status()

    def connect_signals(self):
        self.ui.nav_list.currentRowChanged.connect(self.switch_page)
        self.ui.theme_btn.clicked.connect(self.toggle_theme)

        # Transcription
        self.feedback_ui.record_btn.clicked.connect(self.toggle_recording)
        self.feedback_ui.upload_btn.clicked.connect(self.upload_audio)
        self.feedback_ui.predict_btn.clicked.connect(self.predict_pipeline)
        self.feedback_ui.play_btn.clicked.connect(self.toggle_playback_feedback)
        self.feedback_ui.model_selector.currentTextChanged.connect(self.update_predict_status)

        # Model Hub
        self.comparison_ui.compare_btn.clicked.connect(self.run_comparison)
        self.comparison_ui.val_btn.clicked.connect(self.open_validation_dialog)
        self.comparison_ui.export_btn.clicked.connect(self.export_comparison_csv)

        # Manager
        self.history_ui.table.itemSelectionChanged.connect(self.on_history_select)
        self.history_ui.play_pause_btn.clicked.connect(self.toggle_playback_history)
        self.history_ui.delete_btn.clicked.connect(self.delete_history_item)
        self.history_ui.delete_all_btn.clicked.connect(self.clear_history_db)
        self.history_ui.transcribe_selected_btn.clicked.connect(self.transcribe_history_item)
        self.history_ui.search_box.textChanged.connect(self.load_history_table)
        self.history_ui.export_btn.clicked.connect(self.export_history_csv)

    def switch_page(self, i):
        self.ui.content_stack.setCurrentIndex(i)
        if i == 2: self.load_history_table()

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()

    def apply_theme(self):
        theme = DARK_THEME if self.is_dark else LIGHT_THEME
        self.setStyleSheet(theme)
        
        ico_name = "icons8-lighton-48.png" if self.is_dark else "icons8-lightoff-48.png"
        theme_ico = self.get_colored_icon(os.path.join(self.assets_dir, ico_name), "#3b86ff")
        self.ui.theme_btn.setIcon(theme_ico)
        self.ui.theme_btn.setText("Light Mode" if self.is_dark else "Dark Mode")
        self.setup_icons()

    def get_colored_icon(self, path, color):
        if not os.path.exists(path): return QIcon()
        pix = QPixmap(path)
        painter = QPainter(pix)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pix.rect(), QColor(color))
        painter.end()
        return QIcon(pix)

    def setup_icons(self):
        c = "#ffffff" if self.is_dark else "#495057"
        prim = "#3b86ff"
        
        # Sidebar Icons
        self.ui.nav_list.item(0).setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-microphone-48.png"), c))
        self.ui.nav_list.item(1).setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-edit-48.png"), c))
        self.ui.nav_list.item(2).setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-history-48.png"), c))
        self.ui.nav_list.item(3).setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-search-50.png"), c))

        # Transcription Page
        self.feedback_ui.record_btn.setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-filled-circle-48.png"), "#ffffff"))
        self.feedback_ui.upload_btn.setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-exportcsv-48.png"), c))
        
        play_ico = self.get_colored_icon(os.path.join(self.assets_dir, "icons8-play-48.png"), c)
        self.feedback_ui.play_btn.setIcon(play_ico)
        self.feedback_ui.play_btn.setIconSize(QSize(32, 32))

        self.feedback_ui.rec_indicator.setPixmap(QPixmap(os.path.join(self.assets_dir, "icons8-recording-96.png")))
        self.feedback_ui.predict_btn.setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-tick-48.png"), "#ffffff"))

        # Manager Page
        self.history_ui.export_btn.setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-exportcsv-48.png"), c))
        self.history_ui.play_pause_btn.setIcon(play_ico)
        self.history_ui.play_pause_btn.setIconSize(QSize(32, 32))
        self.history_ui.delete_btn.setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-trash-48.png"), "#ffffff"))
        self.history_ui.delete_all_btn.setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-clear-48.png"), "#ffffff"))
        self.history_ui.transcribe_selected_btn.setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-edit-48.png"), c))

        # Search Icon
        search_ico = self.get_colored_icon(os.path.join(self.assets_dir, "icons8-search-50.png"), c)
        for act in self.history_ui.search_box.actions(): self.history_ui.search_box.removeAction(act)
        self.history_ui.search_box.addAction(search_ico, QLineEdit.LeadingPosition)

    # --- RECORDING ---

    def toggle_recording(self):
        if not self.recording: self.start_rec()
        else: self.stop_rec()

    def start_rec(self):
        try:
            self.clean_cache() # Clear before recording
            self.recording = True
            self.audio_data = []
            self.record_duration_ms = 0
            self.current_history_id = None
            
            # Disable interactions
            self.ui.sidebar.setEnabled(False)
            self.feedback_ui.upload_btn.setEnabled(False)
            self.feedback_ui.predict_btn.setEnabled(False)
            
            self.feedback_ui.record_btn.setText("Stop Recording")
            self.feedback_ui.record_btn.setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-square-full-64.png"), "#ffffff"))
            self.feedback_ui.record_btn.setProperty("recording", True)
            self.feedback_ui.record_btn.style().unpolish(self.feedback_ui.record_btn)
            self.feedback_ui.record_btn.style().polish(self.feedback_ui.record_btn)
            
            self.feedback_ui.progress_bar.setVisible(True)
            self.feedback_ui.progress_bar.setRange(0, self.RECORD_LIMIT_MS)
            self.feedback_ui.progress_bar.setValue(self.RECORD_LIMIT_MS)
            self.feedback_ui.rec_indicator.setVisible(True)
            self.feedback_ui.status_label.setText("RECORDING SPEECH...")
            
            self.record_timer.start(16) # ~60fps smooth
            self.stream = sd.InputStream(samplerate=16000, channels=1, callback=self.audio_cb)
            self.stream.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not start recording: {e}")
            self.stop_rec()

    def stop_rec(self):
        self.recording = False
        self.record_timer.stop()
        self.ui.sidebar.setEnabled(True)
        self.feedback_ui.upload_btn.setEnabled(True)
        self.feedback_ui.predict_btn.setEnabled(True)
        self.feedback_ui.record_btn.setText("Start Recording")
        self.feedback_ui.record_btn.setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-filled-circle-48.png"), "#ffffff"))
        self.feedback_ui.record_btn.setProperty("recording", False)
        self.feedback_ui.record_btn.style().unpolish(self.feedback_ui.record_btn)
        self.feedback_ui.record_btn.style().polish(self.feedback_ui.record_btn)
        self.feedback_ui.record_btn.setStyleSheet("")
        self.feedback_ui.progress_bar.setVisible(False)
        self.feedback_ui.rec_indicator.setVisible(False)
        self.feedback_ui.status_label.setText("READY")

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if self.audio_data:
            audio_np = np.concatenate(self.audio_data, axis=0).flatten()
            path = os.path.join(self.cache_dir, f"capture_{int(time.time())}.wav")
            sf.write(path, audio_np, 16000)
            self.load_audio_to_transcription(path)

    def audio_cb(self, data, frames, time, status):
        if self.recording: self.audio_data.append(data.copy())

    def update_record_status(self):
        self.record_duration_ms += 16
        val = self.RECORD_LIMIT_MS - self.record_duration_ms
        self.feedback_ui.progress_bar.setValue(max(0, val))
        
        pct = (val / self.RECORD_LIMIT_MS) * 100
        if pct > 60: color = SUCCESS
        elif pct > 30: color = WARNING
        else: color = DANGER
        self.feedback_ui.progress_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; border-radius: 3px; }}")
        
        if self.record_duration_ms >= self.RECORD_LIMIT_MS: self.stop_rec()

    # --- PIPELINE ---

    def upload_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Audio", "", "Audio (*.wav *.mp3)")
        if not path: return
        
        # Duration Check
        info = sf.info(path)
        if info.duration > 30:
            QMessageBox.warning(self, "Limit Exceeded", "Audio must be under 30 seconds.")
            return

        self.current_history_id = None
        self.clean_cache() # Clear before loading new
        self.load_audio_to_transcription(path)

    def load_audio_to_transcription(self, path):
        self.current_audio_path = path
        self.feedback_ui.player_card.setVisible(True)
        self.feedback_ui.status_label.setText(f"LOADED: {os.path.basename(path)}")
        
        # Generate Visuals
        visuals = WhisperASR.generate_visuals(path)
        if visuals:
            def decode(b64): return QPixmap.fromImage(QImage.fromData(base64.b64decode(b64)))
            self.feedback_ui.spec_label.setPixmap(decode(visuals["spectrogram"]).scaled(self.feedback_ui.spec_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.feedback_ui.mfcc_label.setPixmap(decode(visuals["mfcc"]).scaled(self.feedback_ui.mfcc_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def predict_pipeline(self):
        if not self.current_audio_path:
            QMessageBox.warning(self, "No Audio", "Record or upload audio first.")
            return
            
        model_key = self.feedback_ui.model_selector.currentText()
        
        if model_key not in self.models:
            QMessageBox.critical(self, "Model Error", f"Model '{model_key}' is not loaded yet or failed.")
            return

        model = self.models[model_key]
        self.feedback_ui.status_label.setText("PREDICTING...")
        self.feedback_ui.status_label.repaint()
        
        busy = BusyDialog(self, "Transcription", "Running AI inference... Please wait.", is_dark=self.is_dark)
        busy.show()
        QApplication.processEvents()
        
        try:
            audio_np, _ = sf.read(self.current_audio_path)
            self.inference_thread = TranscriptionThread(model, audio_np)
            
            def on_finished(text, conf):
                # Save to DB if it's new
                if self.current_history_id is None:
                    storage_filename = f"rec_{int(time.time()*1000)}.wav"
                    storage_path = os.path.join(self.storage_dir, storage_filename)
                    shutil.copy2(self.current_audio_path, storage_path)
                    self.db.insert(text, storage_path)
                
                # UI Update
                self.ui.nav_list.setCurrentRow(1)
                self.comparison_ui.transcription_box.setText(text)
                color = SUCCESS if conf > 0.8 else WARNING if conf > 0.5 else DANGER
                self.comparison_ui.confidence_label.setText(f"CONFIDENCE: {conf*100:.1f}%")
                self.comparison_ui.confidence_label.setStyleSheet(f"color: {color}; background: transparent;")
                self.feedback_ui.status_label.setText("READY")
                busy.close()

            def on_error(err):
                QMessageBox.critical(self, "Inference Error", f"Failed to transcribe: {err}")
                self.feedback_ui.status_label.setText("ERROR")
                busy.close()

            self.inference_thread.finished.connect(on_finished)
            self.inference_thread.error.connect(on_error)
            self.inference_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Setup Error", f"Failed to prepare audio: {e}")
            busy.close()

    # --- PLAYER ---

    def update_predict_status(self):
        model_key = self.feedback_ui.model_selector.currentText()
        if model_key in self.models:
            self.feedback_ui.model_status_tag.setText("READY")
            self.feedback_ui.model_status_tag.setStyleSheet("color: #4caf50; font-weight: bold; font-size: 11px;")
        else:
            # Check if it's currently failing or loading
            _, lbl = self.model_ui_refs.get(model_key, (None, None))
            status = lbl.text() if lbl else "NOT LOADED"
            self.feedback_ui.model_status_tag.setText(status)
            color = "#ffa726" if "Loading" in status else "#cf6679"
            self.feedback_ui.model_status_tag.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")

    def toggle_playback_feedback(self):
        if self.current_audio_path:
            self.play_audio(self.current_audio_path, self.feedback_ui.play_slider, self.feedback_ui.time_label, self.feedback_ui.play_btn)

    def toggle_playback_history(self):
        row = self.history_ui.table.currentRow()
        if row < 0: return
        path = self.history_ui.table.item(row, 3).text()
        if os.path.exists(path):
            self.play_audio(path, self.history_ui.audio_slider, self.history_ui.time_label, self.history_ui.play_pause_btn)

    def play_audio(self, path, slider, label, btn):
        c = "#ffffff" if self.is_dark else "#495057"
        if self.is_playing:
            sd.stop()
            self.is_playing = False
            self.playback_timer.stop()
            btn.setIcon(self.get_colored_icon(os.path.join(self.assets_dir, "icons8-play-48.png"), c))
            return

        try:
            audio, sr = sf.read(path)
            duration = len(audio) / sr
            self.active_player_refs = (slider, label, btn, duration)
            self.playback_start_time = time.time()
            self.is_playing = True
            sd.play(audio, sr)
            self.playback_timer.start(33) # Smooth 30fps
            pause_ico = self.get_colored_icon(os.path.join(self.assets_dir, "icons8-pause-48.png"), c)
            btn.setIcon(pause_ico)
            btn.setIconSize(QSize(32, 32))
        except: pass

    def update_playback_ui(self):
        c = "#ffffff" if self.is_dark else "#495057"
        slider, label, btn, duration = self.active_player_refs
        elapsed = time.time() - self.playback_start_time
        if elapsed >= duration:
            self.is_playing = False
            self.playback_timer.stop()
            play_ico = self.get_colored_icon(os.path.join(self.assets_dir, "icons8-play-48.png"), c)
            btn.setIcon(play_ico)
            btn.setIconSize(QSize(32, 32))
            return
        slider.setValue(int((elapsed/duration)*100))
        label.setText(f"{int(elapsed)//60:02d}:{int(elapsed)%60:02d} / {int(duration)//60:02d}:{int(duration)%60:02d}")

    # --- MANAGER ---

    def load_history_table(self, filter_text=""):
        data = self.db.fetch_all()
        
        # Apply filter if provided
        if filter_text:
            search = filter_text.lower()
            data = [
                row for row in data 
                if search in str(row[1]).lower() # Timestamp
                or search in str(row[2]).lower() # Transcription
            ]
            
        t = self.history_ui.table
        t.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setToolTip(str(val))
                t.setItem(i, j, item)

    def on_history_select(self):
        row = self.history_ui.table.currentRow()
        if row >= 0:
            self.history_ui.transcription_detail.setText(self.history_ui.table.item(row, 2).text())
            path = self.history_ui.table.item(row, 3).text()
            self.history_ui.path_display_label.setText(os.path.basename(path))
            self.history_ui.path_display_label.setToolTip(path)

    def delete_history_item(self):
        row = self.history_ui.table.currentRow()
        if row >= 0:
            if QMessageBox.question(self, "Confirm Delete", "Delete this record and its audio file?") == QMessageBox.Yes:
                self.db.delete(int(self.history_ui.table.item(row, 0).text()))
                self.load_history_table()

    def clear_history_db(self):
        if QMessageBox.question(self, "Confirm Clear", "Clear ALL historical records and files? This cannot be undone.") == QMessageBox.Yes:
            self.db.delete_all()
            self.load_history_table()

    def export_history_csv(self):
        data = self.db.fetch_all()
        if not data:
            QMessageBox.warning(self, "Export Error", "Database is empty. Nothing to export.")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if path:
            import csv
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Timestamp", "Transcription", "Audio Path"])
                writer.writerows(data)
            QMessageBox.information(self, "Success", f"Data exported successfully to:\n{path}")

    def transcribe_history_item(self):
        row = self.history_ui.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a record from the history table first.")
            return
        
        busy = BusyDialog(self, "Loading History", "Retrieving audio data and preparing visuals...", is_dark=self.is_dark)
        busy.show()
        QApplication.processEvents()
        
        try:
            self.current_history_id = int(self.history_ui.table.item(row, 0).text())
            path = self.history_ui.table.item(row, 3).text()
            text = self.history_ui.table.item(row, 2).text()
            
            if os.path.exists(path):
                self.current_audio_path = path
                # Transition to Transcription Page to allow re-analysis
                self.ui.nav_list.setCurrentRow(0) 
                self.load_audio_to_transcription(path)
                # Also populate Model Hub with the existing transcription as a starting point
                self.comparison_ui.transcription_box.setText(text)
        finally:
            busy.close()

    def open_validation_dialog(self):
        dialog = ValidationDialog(self, self.validation_text)
        if dialog.exec_():
            self.validation_text = dialog.get_text()
            self.comparison_ui.validation_display.setText(self.validation_text or "No validation text provided...")
            if self.validation_text:
                self.comparison_ui.validation_display.setStyleSheet("background: transparent; border: 1px solid #27ae60; color: #ffffff;")
            else:
                self.comparison_ui.validation_display.setStyleSheet("background: transparent; border: 1px solid #2a2a3a; color: #888;")

    def export_comparison_csv(self):
        comp_table = self.comparison_ui.table
        if comp_table.rowCount() == 0: return
        
        path, _ = QFileDialog.getSaveFileName(self, "Export Comparison", "", "CSV Files (*.csv)")
        if not path: return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = [comp_table.horizontalHeaderItem(i).text() for i in range(comp_table.columnCount())]
                writer.writerow(headers)
                
                for r in range(comp_table.rowCount()):
                    row_data = []
                    for c in range(comp_table.columnCount()):
                        item = comp_table.item(r, c)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            QMessageBox.information(self, "Export Success", f"Results saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to save CSV: {e}")

    def run_comparison(self):
        if not self.current_audio_path:
            QMessageBox.warning(self, "No Audio", "Upload or record audio first.")
            return

        # Start busy state
        self.comparison_ui.setEnabled(False)
        self.ui.sidebar.setEnabled(False)
        self.comparison_ui.status_display.setText("COMPARING MODELS...")
        self.comparison_ui.status_display.setStyleSheet("color: #f39c12; font-weight: bold;")

        busy = BusyDialog(self, "Model Comparison", "Running multi-model benchmark... Please wait.", is_dark=self.is_dark)
        busy.show()
        QApplication.processEvents()

        comp_table = self.comparison_ui.table
        
        # Reset table results before starting
        for i in range(comp_table.rowCount()):
            for j in range(1, 7):
                comp_table.setItem(i, j, QTableWidgetItem("-"))
        QApplication.processEvents()

        selected_models = []
        for i in range(comp_table.rowCount()):
            item = comp_table.item(i, 0)
            if item.checkState() == Qt.Checked:
                model_key = item.text()
                if model_key in self.models:
                    selected_models.append((i, model_key, self.models[model_key]))
                    comp_table.setItem(i, 1, QTableWidgetItem("Waiting..."))
                else:
                    comp_table.setItem(i, 1, QTableWidgetItem("NOT LOADED"))
                    for j in range(2, 7): comp_table.setItem(i, j, QTableWidgetItem("-"))

        if not selected_models:
            QMessageBox.warning(self, "No Models", "Select at least one loaded model for comparison.")
            self.comparison_ui.setEnabled(True)
            self.ui.sidebar.setEnabled(True)
            self.comparison_ui.status_display.setText("READY")
            self.comparison_ui.status_display.setStyleSheet("color: #888; font-weight: bold;")
            busy.close()
            return

        self.comp_thread = ComparisonThread(selected_models, self.current_audio_path, self.validation_text)
        
        def on_row_updated(row, status, text, conf, lat, wer, rtfx):
            st_item = QTableWidgetItem(status)
            if status == "Completed": st_item.setForeground(QColor("#4caf50"))
            elif "FAILED" in status: st_item.setForeground(QColor("#cf6679"))
            comp_table.setItem(row, 1, st_item)
            
            txt_item = QTableWidgetItem(text)
            txt_item.setToolTip(text)
            comp_table.setItem(row, 2, txt_item)
            
            comp_table.setItem(row, 3, QTableWidgetItem(conf))
            comp_table.setItem(row, 4, QTableWidgetItem(lat))
            comp_table.setItem(row, 5, QTableWidgetItem(wer))
            comp_table.setItem(row, 6, QTableWidgetItem(rtfx))

        def on_finished():
            self.comparison_ui.setEnabled(True)
            self.ui.sidebar.setEnabled(True)
            self.comparison_ui.status_display.setText("READY")
            self.comparison_ui.status_display.setStyleSheet("color: #888; font-weight: bold;")
            busy.close()

        self.comp_thread.row_updated.connect(on_row_updated)
        self.comp_thread.finished.connect(on_finished)
        self.comp_thread.start()



