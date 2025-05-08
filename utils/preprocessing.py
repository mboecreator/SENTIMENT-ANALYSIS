import re
import emoji
from typing import List, Dict

def preprocess_text(text: str) -> str:
    """
    Preprocess the input text by handling emojis, slang, and cleaning the text.
    
    Args:
        text (str): The input text to preprocess
        
    Returns:
        str: The preprocessed text
    """
    # Convert emojis to text
    text = emoji.demojize(text)
    
    # Common slang replacements
    slang_dict = {
        r'\blit\b': 'exciting',
        r'\bwoke\b': 'aware',
        r'\bsavage\b': 'harsh',
        r'\bgoat\b': 'greatest',
        r'\bfomo\b': 'fear of missing out',
        r'\byolo\b': 'you only live once',
        r'\btbh\b': 'to be honest',
        r'\bimo\b': 'in my opinion',
        r'\bafaik\b': 'as far as I know',
        r'\bafaict\b': 'as far as I can tell',
        r'\bafaics\b': 'as far as I can see',
        r'\bafair\b': 'as far as I recall',
        r'\bafaiu\b': 'as far as I understand',
    }
    
    # Replace slang
    for slang, replacement in slang_dict.items():
        text = re.sub(slang, replacement, text, flags=re.IGNORECASE)
    
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_emojis(text: str) -> List[Dict]:
    """
    Extract and analyze emojis from the text.
    
    Args:
        text (str): The input text
        
    Returns:
        List[Dict]: List of dictionaries containing emoji and its meaning
    """
    # Emoji meanings mapping
    emoji_meanings = {
        '😊': 'happy',
        '😢': 'sad',
        '😡': 'angry',
        '😱': 'fear',
        '😮': 'surprise',
        '❤️': 'love',
        '👍': 'approval',
        '👎': 'disapproval',
        '😂': 'laughter',
        '😍': 'love',
        '😎': 'cool',
        '😴': 'sleepy',
        '😭': 'crying',
        '😤': 'frustrated',
        '😨': 'scared',
        '😳': 'embarrassed',
        '😋': 'delicious',
        '😷': 'sick',
        '😇': 'angelic',
        '😈': 'mischievous'
    }
    
    # Extract emojis using emoji.emoji_list
    emoji_list = emoji.emoji_list(text)
    emojis = []
    
    for emoji_data in emoji_list:
        emoji_char = emoji_data['emoji']
        meaning = emoji_meanings.get(emoji_char, 'neutral')
        emojis.append({
            'emoji': emoji_char,
            'meaning': meaning
        })
    
    return emojis 