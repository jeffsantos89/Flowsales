import pandas as pd
from feature_engineering import feature_engineering

class DataPipeline:
    """ Pipeline completo de preparação de dados para Machine Learning """

    def __init__(self, numeric_columns, categorical_columns):
        self.numeric_columns = numeric_columns
        self.categorical_columns = categorical_columns

    def transform(self, df: pd.DataFrame):
        df = feature_engineering.transform_numeric(df, self.numeric_columns)
        df = feature_engineering.transform_categorical(df, self.categorical_columns)
        return df

data_pipeline = DataPipeline(numeric_columns=["age", "income"], categorical_columns=["gender"])
if __name__ == "__main__":
    # Exemplo de uso do pipeline
    data = {
        "age": [25, 32, 47],
        "income": [50000, 60000, 70000],
        "gender": ["M", "F", "M"]
    }
    df = pd.DataFrame(data)
    
    transformed_df = data_pipeline.transform(df)
    print(transformed_df)