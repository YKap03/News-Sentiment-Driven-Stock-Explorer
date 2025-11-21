"""
Model inference service: load model and make predictions.
"""
import pickle
import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
from services.feature_engineering import compute_features
from db.models import DailyPrice, NewsArticle


class ModelInference:
    """Model inference service."""
    
    def __init__(self, model_path: str = None, metrics_path: str = None):
        """
        Initialize model inference service.
        
        Args:
            model_path: Path to saved model pickle file
            metrics_path: Path to model metrics JSON file
        """
        if model_path is None:
            model_path = Path(__file__).parent.parent / "models" / "classifier.pkl"
        if metrics_path is None:
            metrics_path = Path(__file__).parent.parent / "models" / "model_metrics.json"
        
        self.model_path = Path(model_path)
        self.metrics_path = Path(metrics_path)
        self.model = None
        self.metrics = None
        self._load_model()
        self._load_metrics()
    
    def _load_model(self):
        """Load the trained model."""
        if self.model_path.exists():
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
        else:
            print(f"Warning: Model file not found at {self.model_path}")
    
    def _load_metrics(self):
        """Load model metrics."""
        if self.metrics_path.exists():
            with open(self.metrics_path, "r") as f:
                self.metrics = json.load(f)
        else:
            self.metrics = {}
    
    def get_metrics(self) -> Dict:
        """Get model metrics."""
        return self.metrics
    
    def predict_probabilities(
        self,
        prices: List[dict],
        articles: List[dict]
    ) -> Optional[pd.DataFrame]:
        """
        Predict probabilities of positive 3-day returns.
        
        Args:
            prices: List of DailyPrice objects
            articles: List of NewsArticle objects
            
        Returns:
            DataFrame with columns: date, prob_positive_return
        """
        if self.model is None:
            return None
        
        # Compute features
        features_df = compute_features(prices, articles)
        
        if len(features_df) == 0:
            return None
        
        # Prepare features
        feature_cols = [
            "sentiment_avg",
            "sentiment_rolling_mean_3d",
            "return_1d",
            "volatility_5d"
        ]
        
        X = features_df[feature_cols].fillna(0.0).values
        
        # Predict probabilities
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(X)[:, 1]  # Probability of positive class
        else:
            # Fallback for models without predict_proba
            predictions = self.model.predict(X)
            proba = predictions.astype(float)
        
        result = pd.DataFrame({
            "date": features_df["date"],
            "prob_positive_return": proba
        })
        
        return result


# Global instance (loaded at startup)
_model_inference: Optional[ModelInference] = None


def get_model_inference() -> ModelInference:
    """Get the global model inference instance."""
    global _model_inference
    if _model_inference is None:
        _model_inference = ModelInference()
    return _model_inference

