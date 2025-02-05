import time
from typing import Dict, Tuple, Any
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import torch
import torch.nn.functional as F

class VectaraService:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base')
        self.classifier = pipeline(
            "text-classification",
            model='vectara/hallucination_evaluation_model',
            tokenizer=self.tokenizer,
            trust_remote_code=True
        )

    def predict(self, input_1: str, input_2: str) -> Tuple[float, int]:
        start_time = time.time()
        prompt = "<pad> Determine if the hypothesis is true given the premise?\n\nPremise: {text1}\n\nHypothesis: {text2}"
        input_pairs = [prompt.format(text1=input_1, text2=input_2)]
        
        try:
            full_scores = self.classifier(input_pairs, top_k=None)
            consistent_score = next(
                score_dict['score'] 
                for score_for_both_labels in full_scores 
                for score_dict in score_for_both_labels 
                if score_dict['label'] == 'consistent'
            )
            processing_time = int((time.time() - start_time) * 1000)
            return consistent_score, processing_time
        except Exception as e:
            raise RuntimeError(f"Prediction error: {e}")

class GibberishService:
    def __init__(self):
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "madhurjindal/autonlp-Gibberish-Detector-492513457"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            "madhurjindal/autonlp-Gibberish-Detector-492513457"
        )

    def predict(self, input_text: str) -> Tuple[Dict[str, float], str, int]:
        start_time = time.time()
        try:
            inputs = self.tokenizer(input_text, return_tensors="pt")
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1)
            
            predicted_index = torch.argmax(probs, dim=1).item()
            labels = self.model.config.id2label
            predicted_label = labels[predicted_index]
            
            probabilities = {
            'prob_clean': probs[0][0].item(),  
            'prob_mild_gibberish': probs[0][1].item(), 
            'prob_noise': probs[0][2].item(), 
            'prob_word_salad': probs[0][3].item()
        }
            
            processing_time = int((time.time() - start_time) * 1000)
            return probabilities, predicted_label, processing_time
        except Exception as e:
            raise RuntimeError(f"Prediction error: {e}")
