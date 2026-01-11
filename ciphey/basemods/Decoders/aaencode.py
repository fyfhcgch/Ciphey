import re
import subprocess
import tempfile
import os
from typing import Dict, Optional

import logging
from rich.logging import RichHandler

from ciphey.iface import Config, Decoder, ParamSpec, T, U, registry


@registry.register
class AaEncode(Decoder[str]):
    """
    Decodes aaEncode encoding
    aaEncode is a JavaScript obfuscation technique that uses Japanese hiragana and katakana characters
    """
    
    def decode(self, ctext: T) -> Optional[U]:
        """
        Attempts to decode aaEncode encoded string
        """
        # Check if the text contains aaEncode characteristics
        if not self.is_aaencoded(ctext):
            return None
            
        try:
            # Decode the aaEncode string using JavaScript execution
            return self.execute_aaencode(ctext)
        except Exception:
            return None

    def is_aaencoded(self, text: str) -> bool:
        """
        Checks if the given text looks like aaEncoded string
        """
        # aaEncode typically uses specific Unicode characters in a particular pattern
        # Look for the characteristic aaEncode pattern with high density of special characters
        
        if len(text) < 100:  # aaEncode is typically quite long
            return False
            
        # Count aaEncode typical characters (full-width Latin, half-width Katakana, etc.)
        # These include characters like: ﾟ ω ゝ Θ Д etc.
        special_unicode_chars = len(re.findall(r'[\uFF65-\uFFDC\uFFE8-\uFFEE\u3000-\u303F\uFF00-\uFFEF]', text))
        
        # Also look for specific aaEncode characters
        specific_chars = len(re.findall(r'[ﾟωﾉΘДεｏｃ]', text))
        
        # Calculate ratios
        special_ratio = special_unicode_chars / len(text)
        specific_ratio = specific_chars / len(text)
        
        # aaEncode typically has both special Unicode characters and specific aaEncode characters
        # Using a combination of criteria to reduce false positives
        return (special_ratio >= 0.15) or (specific_ratio >= 0.05)

    def execute_aaencode(self, aaencode_code: str) -> Optional[str]:
        """
        Executes aaEncode string by using JavaScript engine
        """
        try:
            # Simple direct execution without complex output capture
            # This matches the successful test we ran earlier
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
                f.write(aaencode_code)
                temp_file = f.name
                
            try:
                # Execute the JavaScript code using Node.js
                result = subprocess.run(['node', temp_file], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=15)
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    if output and len(output) > 0:
                        # Remove quotes if they surround the output
                        output = output.strip()
                        if output.startswith("'") and output.endswith("'"):
                            output = output[1:-1]  # Remove surrounding quotes
                        return output
                    else:
                        # If stdout is empty, maybe the result is in stderr
                        if result.stderr and len(result.stderr.strip()) > 0:
                            return result.stderr.strip()
                else:
                    # If the first method fails, try inline execution
                    result2 = subprocess.run(['node', '-e', aaencode_code], 
                                           capture_output=True, 
                                           text=True, 
                                           timeout=15)
                    if result2.returncode == 0:
                        output = result2.stdout.strip()
                        if output and len(output) > 0:
                            # Remove quotes if they surround the output
                            output = output.strip()
                            if output.startswith("'") and output.endswith("'"):
                                output = output[1:-1]  # Remove surrounding quotes
                            return output
                return None
            finally:
                # Clean up the temporary file
                os.unlink(temp_file)
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # If Node.js is not available or execution fails, return None
            return None

    @staticmethod
    def priority() -> float:
        # Lower priority since it requires external execution
        return 0.1

    def __init__(self, config: Config):
        super().__init__(config)

    @staticmethod
    def getParams() -> Optional[Dict[str, ParamSpec]]:
        return None

    @staticmethod
    def getTarget() -> str:
        return "aaencode"