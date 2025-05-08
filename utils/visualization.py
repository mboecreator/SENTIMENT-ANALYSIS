import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import re
from typing import Dict, List

def create_sentiment_chart(sentiment_result: Dict) -> Dict:
    """
    Create a pie chart for sentiment distribution.
    
    Args:
        sentiment_result (Dict): Sentiment analysis results
        
    Returns:
        Dict: Chart data for Plotly
    """
    labels = ['Positive', 'Neutral', 'Negative']
    values = [0, 0, 0]
    
    sentiment = sentiment_result['sentiment'].lower()
    if sentiment == 'positive':
        values[0] = 1
    elif sentiment == 'neutral':
        values[1] = 1
    else:
        values[2] = 1
    
    return {
        'type': 'pie',
        'data': {
            'labels': labels,
            'values': values
        },
        'layout': {
            'title': 'Sentiment Distribution',
            'height': 400
        }
    }

def create_emotion_chart(emotions: List[str]) -> Dict:
    """
    Create a bar chart for emotion distribution.
    
    Args:
        emotions (List[str]): List of detected emotions
        
    Returns:
        Dict: Chart data for Plotly
    """
    # Count occurrences of each emotion
    emotion_counts = {}
    for emotion in emotions:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    return {
        'type': 'bar',
        'data': {
            'x': list(emotion_counts.keys()),
            'y': list(emotion_counts.values())
        },
        'layout': {
            'title': 'Emotion Distribution',
            'height': 400,
            'xaxis': {'title': 'Emotion'},
            'yaxis': {'title': 'Count'}
        }
    } 