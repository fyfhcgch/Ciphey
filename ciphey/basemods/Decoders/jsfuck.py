import re
import subprocess
import tempfile
import os
from typing import Dict, Optional

import logging
from rich.logging import RichHandler

from ciphey.iface import Config, Decoder, ParamSpec, T, U, registry


@registry.register
class JSFuck(Decoder[str]):
    """
    Decodes JSFuck encoding
    JSFuck is an esoteric programming language that uses only the characters [, ], (, ), !, and +
    """
    
    def decode(self, ctext: T) -> Optional[U]:
        """
        Attempts to decode JSFuck encoded string
        """
        # Check if the text contains only valid JSFuck characters
        if not self.is_jsfuck_encoded(ctext):
            return None
            
        try:
            # Execute the JSFuck code using JavaScript engine
            return self.execute_jsfuck(ctext)
        except Exception:
            return None

    def is_jsfuck_encoded(self, text: str) -> bool:
        """
        Checks if the given text looks like JSFuck encoded string
        """
        # Remove whitespace and check if only valid JSFuck characters remain
        cleaned = re.sub(r'\s+', '', text)
        # JSFuck uses only these characters: [ ] ( ) ! + and sometimes .
        if not cleaned:
            return False
            
        # Check if all characters are valid JSFuck characters
        valid_chars = set('[]()!+.0123456789')
        if not all(c in valid_chars for c in cleaned):
            return False
            
        # Additional check: JSFuck is typically quite long due to the verbose nature
        # of representing everything with [!+()]
        if len(cleaned) < 50:  # Too short to likely be JSFuck
            return False
            
        # Check for balanced brackets and parentheses
        bracket_count = 0
        paren_count = 0
        for char in cleaned:
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            elif char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                
        # Brackets and parentheses should be balanced
        return bracket_count == 0 and paren_count == 0

    def execute_jsfuck(self, jsfuck_code: str) -> Optional[str]:
        """
        Executes JSFuck code by using JavaScript engine
        """
        try:
            # Create a temporary file with the JSFuck code to execute
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                # Capture console output by overriding console.log
                f.write(f'''
                const fs = require('fs');
                const util = require('util');
                
                // Override console.log to capture output
                let capturedOutput = '';
                const originalLog = console.log;
                console.log = function(...args) {{
                    capturedOutput += args.map(arg => util.inspect(arg)).join(' ') + '\\n';
                }};
                
                // The JSFuck code
                {jsfuck_code}
                
                // Write the captured output to stdout
                process.stdout.write(capturedOutput.trim());
                ''')
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
                        return output
                    else:
                        # If stdout is empty, maybe the result is in stderr
                        if result.stderr and len(result.stderr.strip()) > 0:
                            return result.stderr.strip()
                else:
                    # Try a fallback approach without capturing console.log
                    result2 = subprocess.run(['node', '-e', jsfuck_code], 
                                           capture_output=True, 
                                           text=True, 
                                           timeout=15)
                    if result2.returncode == 0:
                        output = result2.stdout.strip()
                        if output and len(output) > 0:
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
        return "jsfuck"