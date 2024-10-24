import streamlit as st
from components.transliterator import Transliterator
from components.real_time_ui import RealTimeTransliterationUI
from components.file_transliteration_ui import FileTransliterationUI

# Set the favicon and page title
st.set_page_config(page_title="Aura", page_icon="favicon.png", layout="wide")

# Load custom CSS
def load_css(file_name):
  with open(file_name) as f:
      st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the CSS file
load_css("styles.css")  # Ensure this file is in the same directory as app.py

class TransliteratorApp:
  def __init__(self):
      self.transliterator = Transliterator()
      self.real_time_ui = RealTimeTransliterationUI(self.transliterator)
      self.file_ui = FileTransliterationUI(self.transliterator)

  def run(self):
      st.title("📜- Aura")
      tab1, tab2 = st.tabs(["Real-time Transliteration", "File Transliteration"])
      
      with tab1:
          self.real_time_ui.display()
      
      with tab2:
          self.file_ui.display()

if __name__ == "__main__":
  app = TransliteratorApp()
  app.run()