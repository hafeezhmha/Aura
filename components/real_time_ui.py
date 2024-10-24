import streamlit as st

class RealTimeTransliterationUI:
  def __init__(self, transliterator):
      self.transliterator = transliterator
      self.lang_options = {
          'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada', 'bn': 'Bengali', 'mr': 'Marathi',
          'ml': 'Malayalam', 'or': 'Odia', 'ta': 'Tamil', 'sa': 'Sanskrit',
          'ur': 'Urdu', 'gu': 'Gujarati', 'pa': 'Punjabi', 'te': 'Telugu'
      }

  def display(self):
      st.subheader("Real-time Transliteration")
      st.write("A Multilingual Transliteration System")
      input_text = st.text_input("Input Text", placeholder="Enter some text in the source language")

      col1, col2 = st.columns(2)
      with col1:
          st.write("Input Language:")
          input_lang = st.radio("", list(self.lang_options.keys()), format_func=lambda x: self.lang_options[x], key="input_lang")
      with col2:
          st.write("Output Language:")
          output_lang_options = {k: v for k, v in self.lang_options.items() if k != 'en'}
          output_lang = st.radio("", list(output_lang_options.keys()), format_func=lambda x: output_lang_options[x], key="output_lang")

      status_message = st.empty()
      status_message.text("Status: ⚡ We are now live!")
      if st.button("Make Prediction", key="make_prediction"):
          transliterated_text, _ = self.transliterator.transliterate_realtime(input_text, output_lang)
          st.markdown("<h3 style='color: #ECB176;'>Transliterated Text</h3>", unsafe_allow_html=True)
          st.markdown(f"<p style='color: #FED8B1;'>{transliterated_text}</p>", unsafe_allow_html=True)    
