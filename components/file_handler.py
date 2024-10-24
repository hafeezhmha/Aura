import pandas as pd

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