import streamlit as st
from components.file_handler import FileHandler
import time

class FileTransliterationUI:
  def __init__(self, transliterator):
      self.transliterator = transliterator
      self.lang_options = {
          'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada', 'bn': 'Bengali', 'mr': 'Marathi',
          'ml': 'Malayalam', 'or': 'Odia', 'ta': 'Tamil', 'sa': 'Sanskrit',
          'ur': 'Urdu', 'gu': 'Gujarati', 'pa': 'Punjabi', 'te': 'Telugu'
      }

  def display(self):
      st.subheader("File Transliteration")
      col1, col2 = st.columns([2, 3])

      with col1:
          st.write("Upload a Parquet or Excel file and choose the languages for transliteration.")
          st.markdown('<div class="file-upload">', unsafe_allow_html=True)  # Add breathing room
          uploaded_file = st.file_uploader("Upload your file", type=["parquet", "xlsx"])
          st.markdown('</div>', unsafe_allow_html=True)  # Close div

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

                          with col2:
                              st.subheader("Output Preview")
                              st.markdown('<div class="output-preview">', unsafe_allow_html=True)  # Add breathing room
                              st.dataframe(transliterated_df.head())
                              st.write(f"Total rows: {len(transliterated_df)}")
                              st.markdown('</div>', unsafe_allow_html=True)  # Close div

                          output_file_path = f"transliterated_output.{output_format.lower()}"
                          if output_format == "XLSX":
                              transliterated_df.to_excel(output_file_path, index=False)
                              mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                          else:  # CSV
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