import time
import asyncio
import streamlit as st
from components.google_transliterator import GoogleTransliterator
from components.file_handler import FileHandler

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

                  processed_operations += len(texts)
                  progress = min(processed_operations / total_operations, 1.0)
                  progress_bar.progress(progress)

                  status_message.text(f"Finished transliterating {column} to {lang_id}")

              except Exception as e:
                  df[new_column_name] = df[column]
                  st.error(f"Error transliterating {column} to {lang_id}: {str(e)}")

      progress_bar.progress(1.0)
      return df

  def transliterate_realtime(self, text, lang):
      return self.transliterator.transliterate_realtime(text, lang)