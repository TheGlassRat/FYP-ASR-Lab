# FYP-ASR-Lab
This repo is to store the ASR Lab system for FYP, due to file size limitations. Support and Access is provided until December 31 2026, afterwards, this repo will no longer be supported. 


Setting up 
1. Download/Clone the repository, install the neccessary libraries (requirements.txt).
2. Run generate_additional_data.py and malay_conversational_preprocess in Google Colab environment.
3. Download the dataset (folder containing .arrow files) to place these folders in AI_Model/Dataset directory.
   - You can check dataset intergrity by specifying the file path (Dataset, malay_conversational_speech_corpus, validation) in dataset_integrity_check.py and run it.
4. Run training_mesolitica_smallv2.py and training_openai_small.py.
   - If you want to evaluate the models, run evaluate_variations.py and it will produce a comparison table and visualisations.
5. Your models are ready and the application is ready to use.


