import re
import aiohttp
import asyncio
import requests

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
                          transliterated_words.append(word)
              except Exception as e:
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
                  transliterated_words.append(word)
          else:
              transliterated_words.append(word)

      transliterated_text = ' '.join(transliterated_words)
      return transliterated_text, suggestions