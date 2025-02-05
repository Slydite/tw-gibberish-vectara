from pydantic import BaseModel, Field
from datetime import datetime

from typing import Optional

class VectaraPredictionRequest(BaseModel):
    input_1: str = Field(..., description="First input text for comparison")
    input_2: str = Field(..., description="Second input text for comparison")

class GibberishPredictionRequest(BaseModel):
    input_text: str = Field(..., description="Input text to analyze for gibberish")

class VectaraResult(BaseModel):
    prediction_id: str
    input_1: str
    input_2: str
    output_score: float
    timestamp: datetime
    processing_time_ms: int
    status: str

class GibberishResult(BaseModel):
    prediction_id: str
    input_text: str
    predicted_label: str
    prob_clean: float
    prob_mild_gibberish: float
    prob_noise: float
    prob_word_salad: float
    timestamp: datetime
    processing_time_ms: int
    status: str

    
