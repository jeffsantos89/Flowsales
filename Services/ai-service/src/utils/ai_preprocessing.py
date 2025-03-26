import re
import string
from typing import List
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

class AIPreprocessing:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.scaler = StandardScaler()

    def clean_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'<.*?>+', '', text)
        text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub(r'\n', '', text)
        text = re.sub(r'\w*\d\w*', '', text)
        return text

    def preprocess_texts(self, texts: List[str]) -> np.ndarray:
        cleaned_texts = [self.clean_text(text) for text in texts]
        tfidf_matrix = self.vectorizer.fit_transform(cleaned_texts)
        return tfidf_matrix.toarray()

    def preprocess_numerical(self, data: pd.DataFrame) -> np.ndarray:
        scaled_data = self.scaler.fit_transform(data)
        return scaled_data

    def preprocess(self, text_data: List[str], numerical_data: pd.DataFrame) -> dict:
        processed_texts = self.preprocess_texts(text_data)
        processed_numerical = self.preprocess_numerical(numerical_data)
        return {
            'text': processed_texts,
            'numerical': processed_numerical
        }

# Example usage:
# preprocessing = AIPreprocessing()
# text_data = ["Example text 1", "Example text 2"]
# numerical_data = pd.DataFrame({'feature1': [1, 2], 'feature2': [3, 4]})
# processed_data = preprocessing.preprocess(text_data, numerical_data)
# print(processed_data)