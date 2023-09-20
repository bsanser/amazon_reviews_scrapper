from rich import print
import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nltk 

def main():
  plt.style.use('ggplot')
  df = pd.read_csv('B0BF1D2MCH-global-rating.csv')
  print(df.shape)

if __name__ == "__main__":
  main()