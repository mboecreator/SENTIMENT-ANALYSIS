from transformers import pipeline
import numpy as np

def analyze_sentiment(text, analyzer):
    """
    Analyze the sentiment of the given text using the provided analyzer.
    
    Args:
        text (str): The text to analyze
        analyzer: The sentiment analysis pipeline
        
    Returns:
        dict: Dictionary containing sentiment analysis results
    """
    # Get sentiment prediction
    result = analyzer(text)[0]
    
    # Map the label to a more readable format
    label_mapping = {
        'LABEL_0': 'negative',
        'LABEL_1': 'neutral',
        'LABEL_2': 'positive'
    }
    
    sentiment = label_mapping.get(result['label'], result['label'])
    confidence = result['score']
    
    return {
        'sentiment': sentiment,
        'confidence': float(confidence),
        'text': text
    }

def analyze_emotions(text):
    """
    Analyze the emotions in the given text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        list: List of detected emotions
    """
    # This is a simplified emotion analysis
    # In a real application, you would use a more sophisticated model
    emotions = []
    
    # Check for joy-related words
    joy_words = ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love']
    if any(word in text.lower() for word in joy_words):
        emotions.append('joy')
    
    # Check for anger-related words
    anger_words = ['angry', 'mad', 'furious', 'hate', 'terrible', 'awful', 'bad']
    if any(word in text.lower() for word in anger_words):
        emotions.append('anger')
    
    # Check for sadness-related words
    sadness_words = ['sad', 'unhappy', 'depressed', 'cry', 'tears', 'sorry']
    if any(word in text.lower() for word in sadness_words):
        emotions.append('sadness')
    
    # Check for fear-related words
    fear_words = ['scared', 'afraid', 'fear', 'worried', 'anxious', 'nervous']
    if any(word in text.lower() for word in fear_words):
        emotions.append('fear')
    
    # Check for surprise-related words
    surprise_words = ['surprised', 'wow', 'amazing', 'incredible', 'unbelievable']
    if any(word in text.lower() for word in surprise_words):
        emotions.append('surprise')
    
    # If no specific emotions detected, return neutral
    if not emotions:
        emotions.append('neutral')
    
    return emotions 