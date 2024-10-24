# Aura

**Aura** is a multilingual real-time transliteration system designed to facilitate seamless text transliteration between multiple Indic languages. 

## Features

- **Multilingual Support**: Easily transliterate text between major Indic languages, including Hindi, Kannada, Bengali, Marathi, Malayalam, Odia, Tamil, Urdu, Gujarati, Punjabi, and Telugu.
- **Real-Time Processing**: Experience fast and accurate transliteration of text as you type.
- **User-Friendly Interface**: Intuitive design makes it accessible for users of all skill levels.
- **Customization Options**: Modify themes and configurations to suit your preferences.

## Installation

To run Aura locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hafeezhmha/Aura.git
   cd Aura
2. **Set up a virtual environment (optional but recommended)**:
   ```bash
   conda create -n env_name python=3.10
3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
4. **Run the application**:
   ```bash
   streamlit run app.py
# Usage
Once the application is running, you can input text in the designated field and select the target language for transliteration. The results will be displayed in real time, allowing for easy adjustments and corrections.
Furthermore, you can also upload any XLSX data to get it transliterated to your desired language.

# Configuration
Customize the appearance and settings of Aura by modifying the .streamlit/config.toml file. You can define themes, colors, and other configurations to enhance your user experience.

# Contributing
Contributions are welcome! If you have suggestions for improvements or would like to report a bug, please open an issue or submit a pull request.

Fork the repository.
Create your feature branch (git checkout -b feature/new-feature).
Commit your changes (git commit -m 'Add some feature').
Push to the branch (git push origin feature/new-feature).
Open a pull request.
