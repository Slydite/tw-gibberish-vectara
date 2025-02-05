from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
import logging
from models import ( 
    VectaraPredictionRequest, GibberishPredictionRequest,
    VectaraResult, GibberishResult
)
from services import VectaraService, GibberishService
from database import DatabaseManager
import sys
import os
import json
from datetime import datetime

sys.path.append(os.getcwd())
router = APIRouter()

DATABASE_URL = os.environ.get("DATABASE_URL")


db = DatabaseManager(DATABASE_URL)

vectara_service = VectaraService()
gibberish_service = GibberishService()

@router.post(
    "/predict/vectara",
    response_model=VectaraResult,
    summary="Predict Vectara Score",
    description="""
    Predicts a Vectara score based on two input texts.

    This endpoint takes two text inputs and uses the Vectara service to calculate a similarity score.
    It then saves the inputs and the resulting score to the database.
    """, 
    tags=["Predictions"], 
    responses={ 
        status.HTTP_200_OK: {
            "description": "Successful prediction",
            "content": {
                "application/json": {
                    "example": {
                        "prediction_id": 123,
                        "input_1": "Text input one",
                        "input_2": "Text input two",
                        "output_score": 0.95,
                        "timestamp": "2024-01-01T12:00:00",
                        "processing_time_ms": 50,
                        "status": "success"
                    }
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error during prediction",
            "content": {
                "application/json": {
                    "example": {"detail": "Database connection error or Vectara service failure"}
                }
            },
        },
    },
)
async def predict_vectara(request: VectaraPredictionRequest):
    try:
        db.connect()
        score, processing_time = vectara_service.predict(request.input_1, request.input_2)

        prediction_id = db.save_vectara_result(
            input_1=request.input_1,
            input_2=request.input_2,
            output_score=score,
            processing_time_ms=processing_time,
            status="success"
        )

        return {
            "prediction_id": prediction_id,
            "input_1": request.input_1,
            "input_2": request.input_2,
            "output_score": score,
            "timestamp": datetime.now(),
            "processing_time_ms": processing_time,
            "status": "success"
        }
    except Exception as e:
        logging.error(f"Vectara prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()

@router.post(
    "/predict/gibberish",
    response_model=GibberishResult,
    summary="Predict Gibberish Text", 
    description="""
    Predicts if the input text is gibberish or not.

    This endpoint uses the Gibberish service to analyze the provided text and determine
    the probability of it being gibberish. It also saves the input and prediction results in the database.
    """, 
    tags=["Predictions"], 
    responses={
        status.HTTP_200_OK: {
            "description": "Successful gibberish prediction",
            "content": {
                "application/json": {
                    "example": {
                        "prediction_id": 456,
                        "input_text": "This is a sample text.",
                        "predicted_label": "not gibberish",
                        "gibberish_probability": 0.1,
                        "not_gibberish_probability": 0.9,
                        "timestamp": "2024-01-01T12:01:00",
                        "processing_time_ms": 30,
                        "status": "success"
                    }
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error during gibberish prediction",
            "content": {
                "application/json": {
                    "example": {"detail": "Error processing text with Gibberish service"}
                }
            },
        },
    },
)
async def predict_gibberish(request: GibberishPredictionRequest):
    try:
        db.connect()
        probabilities, predicted_label, processing_time = gibberish_service.predict(
            request.input_text
        )

        prediction_id = db.save_gibberish_result(
            input_text=request.input_text,
            predicted_label=predicted_label,
            probabilities=probabilities,
            processing_time_ms=processing_time,
            status="success"
        )

        return {
            "prediction_id": prediction_id,
            "input_text": request.input_text,
            "predicted_label": predicted_label,
            **probabilities,
            "timestamp": datetime.now(),
            "processing_time_ms": processing_time,
            "status": "success"
        }
    except Exception as e:
        logging.error(f"Gibberish prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()

@router.get(
    "/results/vectara",
    response_model=List[VectaraResult],
    summary="Get Vectara Prediction Results", 
    description="""
    Retrieves a list of all Vectara prediction results from the database.

    This endpoint fetches all stored Vectara prediction results, including inputs, scores, timestamps, and processing times.
    """, 
    tags=["Results"], 
    responses={
        status.HTTP_200_OK: {
            "description": "List of Vectara prediction results",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "prediction_id": 123,
                            "input_1": "Text input one",
                            "input_2": "Text input two",
                            "output_score": 0.95,
                            "timestamp": "2024-01-01T12:00:00",
                            "processing_time_ms": 50,
                            "status": "success"
                        },
                        {
                            "prediction_id": 124,
                            "input_1": "Another text input one",
                            "input_2": "Another text input two",
                            "output_score": 0.88,
                            "timestamp": "2024-01-02T10:30:00",
                            "processing_time_ms": 60,
                            "status": "success"
                        }
                    ]
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error while fetching Vectara results",
            "content": {
                "application/json": {
                    "example": {"detail": "Database query error"}
                }
            },
        },
    },
)
async def get_vectara_results():
    try:
        db.connect()
        return db.get_vectara_results()
    except Exception as e:
        logging.error(f"Error fetching Vectara results: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()

@router.get(
    "/results/gibberish",
    response_model=List[GibberishResult],
    summary="Get Gibberish Prediction Results", 
    description="""
    Retrieves a list of all Gibberish prediction results from the database.

    This endpoint fetches all stored Gibberish prediction results, including inputs, predicted labels, probabilities, timestamps, and processing times.
    """, 
    tags=["Results"], 
    responses={
        status.HTTP_200_OK: {
            "description": "List of Gibberish prediction results",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "prediction_id": 456,
                            "input_text": "This is a sample text.",
                            "predicted_label": "not gibberish",
                            "gibberish_probability": 0.1,
                            "not_gibberish_probability": 0.9,
                            "timestamp": "2024-01-01T12:01:00",
                            "processing_time_ms": 30,
                            "status": "success"
                        },
                        {
                            "prediction_id": 457,
                            "input_text": "asdf jkl;",
                            "predicted_label": "gibberish",
                            "gibberish_probability": 0.98,
                            "not_gibberish_probability": 0.02,
                            "timestamp": "2024-01-02T11:15:00",
                            "processing_time_ms": 25,
                            "status": "success"
                        }
                    ]
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error while fetching Gibberish results",
            "content": {
                "application/json": {
                    "example": {"detail": "Database query error"}
                }
            },
        },
    },
)
async def get_gibberish_results():
    try:
        db.connect()
        return db.get_gibberish_results()
    except Exception as e:
        logging.error(f"Error fetching Gibberish results: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.disconnect()