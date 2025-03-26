from sklearn.ensemble import IsolationForest

class FraudDetection:
    """
    Detecta transações fraudulentas usando Isolation Forest.
    """

    def __init__(self, data):
        self.data = data

    def detect_anomalies(self):
        model = IsolationForest(contamination=0.05, random_state=42)
        self.data["fraudulent"] = model.fit_predict(self.data)
        return self.data
        def __init__(self, data, contamination=0.05, random_state=42, n_estimators=100):
            """
            Initialize fraud detection model with configurable parameters.
            
            Args:
                data: DataFrame with transaction data
                contamination: The proportion of outliers in the data set (float between 0 and 0.5)
                random_state: Random state for reproducibility
                n_estimators: Number of base estimators in the ensemble
            """
            self.data = data.copy()  # Create copy to avoid modifying original data
            self.contamination = contamination
            self.random_state = random_state
            self.n_estimators = n_estimators
            self.model = None
            self.is_fitted = False

        def preprocess_data(self):
            """Preprocess data by handling missing values and scaling features."""
            self.data = self.data.fillna(self.data.mean())
            return self

        def fit(self, X):
            """Fit the isolation forest model."""
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=self.random_state,
                n_estimators=self.n_estimators,
                n_jobs=-1  # Utilize all CPU cores
            )
            self.model.fit(X)
            self.is_fitted = True
            return self

        def detect_anomalies(self):
            """
            Detect fraudulent transactions.
            
            Returns:
                DataFrame with predictions (-1 for fraudulent, 1 for normal)
            """
            if not self.is_fitted:
                self.preprocess_data()
                self.fit(self.data)
            
            predictions = self.model.predict(self.data)
            self.data["fraudulent"] = predictions
            self.data["fraud_score"] = self.model.score_samples(self.data)
            
            return self.data