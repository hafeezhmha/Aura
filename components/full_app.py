import streamlit as st
import time
import pandas as pd
import requests
import re
import aiohttp
import asyncio
import io
import pyperclip
import time
from threading import Timer

class GoogleTransliterator:
  def __init__(self):
      self.lang_code_map = {
          'hi': 'hi', 'kn': 'kn', 'bn': 'bn', 'mr': 'mr', 'ml': 'ml',
          'or': 'or', 'ta': 'ta', 'sa': 'sa', 'ur': 'ur', 'gu': 'gu',
          'pa': 'pa', 'te': 'te'
      }
      self.cache = {}

  async def fetch_transliteration_suggestions_async(self, session, text, lang):
      cache_key = f"{lang}:{text}"
      if cache_key in self.cache:
          return self.cache[cache_key]

      lang_code = self.lang_code_map.get(lang, lang)
      
      text = self.preprocess_text(text)
      words = re.split(r'([&,()]+)', text)
      
      transliterated_words = []
      for word in words:
          if word.strip():
              url = f"https://inputtools.google.com/request?text={word.strip()}&itc={lang_code}-t-i0-und&num=1&cp=0&cs=1&ie=utf-8&oe=utf-8&app=demopage"
              
              try:
                  async with session.get(url) as response:
                      if response.status == 200:
                          data = await response.json()
                          if data and len(data) > 1 and len(data[1]) > 0 and len(data[1][0]) > 1:
                              transliterated_word = data[1][0][1][0]
                              transliterated_word = self.postprocess_text(transliterated_word, lang)
                              transliterated_words.append(transliterated_word)
                          else:
                              transliterated_words.append(word)
                      else:
                          print(f"Failed to fetch transliteration for '{word}' with status code {response.status}")
                          transliterated_words.append(word)
              except Exception as e:
                  print(f"Error transliterating '{word}': {str(e)}")
                  transliterated_words.append(word)
          else:
              transliterated_words.append(word)
      
      transliterated_text = ''.join(transliterated_words)
      self.cache[cache_key] = transliterated_text
      return transliterated_text

  def preprocess_text(self, text):
      return text.strip().lower()

  def postprocess_text(self, text, lang):
      return text

  async def fetch_all_transliterations(self, texts, lang):
      async with aiohttp.ClientSession() as session:
          tasks = [self.fetch_transliteration_suggestions_async(session, text, lang) for text in texts]
          return await asyncio.gather(*tasks)

  def transliterate_realtime(self, text, lang):
      lang_code = self.lang_code_map.get(lang, lang)
      words = re.findall(r'\w+|[^\w\s]', text)
      transliterated_words = []
      suggestions = []

      for word in words:
          if word.isalnum():
              url = f"https://inputtools.google.com/request?text={word}&itc={lang_code}-t-i0-und&num=5&cp=0&cs=1&ie=utf-8&oe=utf-8&app=demopage"
              try:
                  response = requests.get(url)
                  if response.status_code == 200:
                      data = response.json()
                      if data and len(data) > 1 and len(data[1]) > 0 and len(data[1][0]) > 1:
                          transliterated_word = data[1][0][1][0]
                          word_suggestions = data[1][0][1]
                          transliterated_words.append(transliterated_word)
                          suggestions.extend(word_suggestions)
                      else:
                          transliterated_words.append(word)
                  else:
                      transliterated_words.append(word)
              except Exception as e:
                  print(f"Error in real-time transliteration: {str(e)}")
                  transliterated_words.append(word)
          else:
              transliterated_words.append(word)

      transliterated_text = ' '.join(transliterated_words)
      return transliterated_text, suggestions

class FileHandler:
  def __init__(self, file):
      self.file = file
      self.df = self.load_file()

  def load_file(self):
      file_extension = self.file.name.split('.')[-1]
      if file_extension == 'parquet':
          return pd.read_parquet(self.file)
      elif file_extension == 'xlsx':
          return pd.read_excel(self.file)
      else:
          raise ValueError("Unsupported file format. Please upload a Parquet or Excel file.")

class Transliterator:
  def __init__(self):
      self.transliterator = GoogleTransliterator()

  def transliterate_file(self, input_file, lang_ids):
      file_extension = input_file.name.split('.')[-1]

      if file_extension == 'parquet':
          df = pd.read_parquet(input_file)
      elif file_extension == 'xlsx':
          df = pd.read_excel(input_file)
      else:
          raise ValueError("Unsupported file format. Please upload a Parquet or Excel file.")

      text_columns = df.select_dtypes(include=['object']).columns

      progress_bar = st.progress(0)

      total_operations = len(text_columns) * len(lang_ids) * len(df)
      processed_operations = 0

      for lang_id in lang_ids:
          for column in text_columns:
              status_message = st.empty()
              status_message.text(f"Transliterating {column} to {lang_id}...")
              
              new_column_name = f"transliterated_{lang_id}_{column}"
              texts = df[column].dropna().astype(str).tolist()

              try:
                  loop = asyncio.new_event_loop()
                  asyncio.set_event_loop(loop)
                  transliterated_texts = loop.run_until_complete(self.transliterator.fetch_all_transliterations(texts, lang_id))

                  transliteration_dict = dict(zip(texts, transliterated_texts))

                  df[new_column_name] = df[column].map(transliteration_dict).fillna(df[column])

                  print(f"Transliterated {len(texts)} texts for {lang_id} in column {column}")
                  print(f"Sample transliterations: {dict(list(transliteration_dict.items())[:5])}")

              except Exception as e:
                  print(f"Error transliterating {column} to {lang_id}: {str(e)}")
                  df[new_column_name] = df[column]

              processed_operations += len(texts)
              progress = min(processed_operations / total_operations, 1.0)
              progress_bar.progress(progress)

              status_message.text(f"Finished transliterating {column} to {lang_id}")

      progress_bar.progress(1.0)
      return df

  def transliterate_realtime(self, text, lang):
      return self.transliterator.transliterate_realtime(text, lang)
  
class TransliteratorApp:
  def __init__(self):
      self.transliterator = Transliterator()
      self.lang_options = {
          'en': 'English' , 'hi': 'Hindi', 'kn': 'Kannada', 'bn': 'Bengali', 'mr': 'Marathi',
          'ml': 'Malayalam', 'or': 'Odia', 'ta': 'Tamil', 'sa': 'Sanskrit',
          'ur': 'Urdu', 'gu': 'Gujarati', 'pa': 'Punjabi', 'te': 'Telugu'  # Added English for input/output
      }

  def run(self):
      st.title("Aura")
      
      tab1, tab2 = st.tabs(["Real-time Transliteration", "File Transliteration"])
      
      with tab1:
          self.real_time_transliteration()
      
      with tab2:
          self.file_transliteration()

  def real_time_transliteration(self):
    st.subheader("Real-time Transliteration")
    
    # New UI elements
    st.write("A Multilingual Transliteration System")
    st.write("Aura is a multilingual transliteration system that can transliterate between Indic languages. You can transliterate between any of the languages shown below.")

    # Input Text
    input_text = st.text_input("Input Text", placeholder="Enter some text in the source language")

    # Create a row for input language selection
    col1, col2 = st.columns(2)

    # Input Language Selection
    with col1:
        input_lang = st.radio("Input Language", list(self.lang_options.keys()), format_func=lambda x: self.lang_options[x], key="input_lang")

    # Output Language Selection (Removed English)
    with col2:
        output_lang_options = {k: v for k, v in self.lang_options.items() if k != 'en'}  # Exclude English
        output_lang = st.radio("Output Language", list(output_lang_options.keys()), format_func=lambda x: output_lang_options[x], key="output_lang")

    # Status Message
    status_message = st.empty()
    status_message.text("Status: ⚡ Model is Ready")

    # Prediction Button
    if st.button("Make Prediction"):
        transliterated_text, _ = self.transliterator.transliterate_realtime(input_text, output_lang)
        st.text_area("Transliterated Text", value=transliterated_text, height=150, disabled=True)

  def file_transliteration(self):
      st.subheader("File Transliteration")

      # Create two columns for the layout
      col1, col2 = st.columns([2, 3])

      # Column 1 (Left side) - Input options
      with col1:
          st.write("Upload a Parquet or Excel file and choose the languages for transliteration.")

          uploaded_file = st.file_uploader("Upload your file", type=["parquet", "xlsx"])
          
          if uploaded_file is not None:
              try:
                  file_handler = FileHandler(uploaded_file)
                  input_df = file_handler.df
                  st.write(f"Total rows: {len(input_df)}")
                  
                  selected_languages = st.multiselect("Select languages for transliteration", list(self.lang_options.keys()), default=['hi'])
                  output_format = st.radio("Select output format", ["XLSX", "CSV"])

                  if st.button("Transliterate"):
                      if input_df is not None and selected_languages:
                          start_time = time.time()
                          
                          with st.spinner("Transliterating..."):
                              transliterated_df = self.transliterator.transliterate_file(uploaded_file, selected_languages)
                          
                          end_time = time.time()
                          time_taken = end_time - start_time
                          st.success(f"Transliteration completed in {time_taken:.2f} seconds.")

                          # Update the right column with output preview
                          with col2:
                              st.subheader("Output Preview")
                              st.dataframe(transliterated_df.head())
                              st.write(f"Total rows: {len(transliterated_df)}")

                          if output_format == "XLSX":
                              output_file_path = "transliterated_output.xlsx"
                              transliterated_df.to_excel(output_file_path, index=False)
                              mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                          else:  # CSV
                              output_file_path = "transliterated_output.csv"
                              transliterated_df.to_csv(output_file_path, index=False)
                              mime = "text/csv"

                          with open(output_file_path, 'rb') as f:
                              st.download_button(
                                  f"Download Transliterated {output_format}",
                                  data=f,
                                  file_name=output_file_path,
                                  mime=mime
                              )
                      else:
                          st.warning("Please upload a file and select at least one language.")
              except ValueError as e:
                  st.error(str(e))

if __name__ == "__main__":
  app = TransliteratorApp()
  app.run()