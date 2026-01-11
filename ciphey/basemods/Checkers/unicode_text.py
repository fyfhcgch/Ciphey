from typing import Dict, Optional
import unicodedata
from ciphey.iface import Checker, Config, ParamSpec, T, registry

@registry.register
class UnicodeChecker(Checker[str]):
    """
    Checks if text contains meaningful Unicode characters (including Chinese, Japanese, Korean, etc.)
    """
    
    def check(self, text: T) -> Optional[str]:
        if not text or len(text.strip()) == 0:
            return None
        
        # For this checker, we want to identify text that looks like natural language
        # This includes Chinese characters, Latin letters, numbers, and reasonable punctuation
        
        text = text.strip()
        if len(text) < 3:  # Too short to be meaningful
            return None
        
        # Count different character types
        letter_count = 0  # All letters (including Chinese)
        upper_count = 0   # Uppercase Latin letters (often in random text)
        punct_count = 0   # Punctuation
        symbol_count = 0  # Symbols
        number_count = 0  # Numbers
        
        for char in text:
            category = unicodedata.category(char)
            if category.startswith('L'):  # Letters (any script)
                letter_count += 1
                if category == 'Lu':  # Uppercase letter
                    upper_count += 1
            elif category.startswith('N'):  # Numbers
                number_count += 1
            elif category.startswith('P'):  # Punctuation
                punct_count += 1
            elif category.startswith('S'):  # Symbols
                symbol_count += 1
        
        total_chars = len(text)
        
        # Calculate ratios
        letter_ratio = letter_count / total_chars
        upper_ratio = upper_count / total_chars if total_chars > 0 else 0
        punct_ratio = punct_count / total_chars
        
        # Criteria for meaningful text:
        # 1. At least 40% should be letters (allows for words/sentences)
        # 2. Not too many uppercase letters (common in random text)
        # 3. Reasonable punctuation ratio (not too much or too little)
        # 4. At least some letters to indicate words
        if (letter_ratio >= 0.4 and 
            letter_count >= 3 and 
            upper_ratio <= 0.6 and  # Don't allow too many uppercase
            punct_ratio <= 0.5):     # Don't allow too much punctuation
            return ""
        
        return None

    def getExpectedRuntime(self, text: T) -> float:
        return 1e-7 * len(text)

    def __init__(self, config: Config):
        super().__init__(config)

    @staticmethod
    def getParams() -> Optional[Dict[str, ParamSpec]]:
        return None