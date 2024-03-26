import pandas as pd


def find_words(string, df):
    words_2find = string.split()

    result = df[df['long_name'].apply(lambda x: any(x.lower().startswith(str(word.lower())) for word in words_2find))]
    result = result.sort_values(by='overall', ascending=False)
    result = result.head(5)