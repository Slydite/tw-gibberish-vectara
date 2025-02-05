import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Any


class DatabaseManager():
    def __init__(self, db_url: str):  
        self.db_url = db_url  
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(self.db_url)  
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logging.info("Database connected successfully.")
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            raise

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
            logging.info("Cursor closed.")
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")

    def save_vectara_result(self, input_1: str, input_2: str, output_score: float,
                          processing_time_ms: int, status: str) -> str:
        prediction_id = str(uuid4()) # Convert UUID to string
        try:
            query = """
                INSERT INTO vectara_results
                (prediction_id, input_1, input_2, output_score, processing_time_ms, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING prediction_id
            """
            self.cursor.execute(query, (prediction_id, input_1, input_2, output_score,
                                      processing_time_ms, status))
            self.conn.commit()
            logging.info(f"Vectara result saved with prediction_id: {prediction_id}")
            return str(prediction_id)
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error saving Vectara result: {e}")
            raise

    def save_gibberish_result(self, input_text: str, predicted_label: str,
                            probabilities: Dict[str, float], processing_time_ms: int,
                            status: str) -> str:
        prediction_id = str(uuid4()) # Convert UUID to string
        try:
            query = """
                INSERT INTO gibberish_results
                (prediction_id, input_text, predicted_label, prob_clean, prob_mild_gibberish,
                prob_noise, prob_word_salad, processing_time_ms, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING prediction_id
            """
            self.cursor.execute(query, (prediction_id, input_text, predicted_label,
                                      probabilities['prob_clean'], probabilities['prob_mild_gibberish'],
                                        probabilities['prob_noise'], probabilities['prob_word_salad'],
                                      processing_time_ms, status))
            self.conn.commit()
            logging.info(f"Gibberish result saved with prediction_id: {prediction_id}")
            return str(prediction_id)
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error saving Gibberish result: {e}")
            raise

    def get_vectara_results(self, limit: int = 100) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM vectara_results
            ORDER BY timestamp DESC
            LIMIT %s
        """
        self.cursor.execute(query, (limit,))
        results = self.cursor.fetchall()
        logging.info(f"Retrieved {len(results)} Vectara results.")
        return results

    def get_gibberish_results(self, limit: int = 100) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM gibberish_results
            ORDER BY timestamp DESC
            LIMIT %s
        """
        self.cursor.execute(query, (limit,))
        results = self.cursor.fetchall()
        logging.info(f"Retrieved {len(results)} Gibberish results.")
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    db_url = "postgresql://postgres:password@localhost:5432/trustwise_db" 

    db_manager = DatabaseManager(db_url)

    try:
        db_manager.connect()

        # Test save_vectara_result
        vectara_prediction_id = db_manager.save_vectara_result(
            input_1="test input 1",
            input_2="test input 2",
            output_score=0.95,
            processing_time_ms=150,
            status="success"
        )
        logging.info(f"Saved Vectara result with ID: {vectara_prediction_id}")

        # Test save_gibberish_result
        gibberish_prediction_id = db_manager.save_gibberish_result(
            input_text="This is a test sentence.",
            predicted_label="clean",
            probabilities={
                "clean": 0.9,
                "mild_gibberish": 0.05,
                "noise": 0.03,
                "word_salad": 0.02
            },
            processing_time_ms=120,
            status="success"
        )
        logging.info(f"Saved Gibberish result with ID: {gibberish_prediction_id}")

        # Test get_vectara_results
        vectara_results = db_manager.get_vectara_results(limit=5)
        logging.info(f"Vectara Results: {vectara_results}")

        # Test get_gibberish_results
        gibberish_results = db_manager.get_gibberish_results(limit=5)
        logging.info(f"Gibberish Results: {gibberish_results}")


    except Exception as e:
        logging.error(f"An error occurred during testing: {e}")
    finally:
        db_manager.disconnect()