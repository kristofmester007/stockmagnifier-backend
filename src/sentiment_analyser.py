import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax

class SentimentAnalyzer:
    """
    A class for analyzing sentiment using the FinBERT model.
    """

    def __init__(self):
        """
        Initializes the SentimentAnalyzer by loading the model and tokenizer.
        """
        print("Loading FinBERT model...")
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

    def __del__(self):
        """
        Deletes the model and tokenizer to free up memory (if necessary).
        """
        del self.model
        del self.tokenizer
        print("FinBERT resources released.")

    def analyze_sentiment(self, text):
        """
        Analyzes the sentiment of the input text and returns a numerical sentiment score.
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = self.model(**inputs)
        scores = softmax(outputs.logits.detach().numpy(), axis=1)
        scores_list = scores[0].tolist()

        positive = scores_list[0]
        negative = scores_list[1]
        neutral = scores_list[2]

        dominant_index = np.argmax(scores)

        final_score = 0

        if dominant_index == 0:  # Dominantly positive
            final_score = positive - negative - (neutral/2)
        elif dominant_index == 1:  # Dominantly negative
            final_score = (-negative) + positive + (neutral/2)
        else:  # Dominantly neutral
            final_score = (positive - negative)/2
        
        #print(f"\n{text}\npositive: {positive}, neutral: {neutral}, negative: {negative}\nfinal score: {final_score}")
        return final_score