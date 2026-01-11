import re
import time
from typing import Dict, Optional, Tuple

import logging
from rich.logging import RichHandler

from ciphey.iface import Config, Decoder, ParamSpec, T, U, WordList, registry


@registry.register
class Ook(Decoder[str]):
    def decode(self, ctext: T) -> Optional[U]:
        """
        Takes a ciphertext and treats it as an Ook! program,
        converting it to Brainfuck and interpreting it,
        saving the output as a string to return.

        Ook! is an esoteric programming language that is very similar to Brainfuck.
        It uses three tokens: "Ook.", "Ook!", and "Ook?" to represent Brainfuck instructions.
        The mapping is as follows:
        - Ook. Ook. -> >
        - Ook! Ook! -> <
        - Ook. Ook! -> +
        - Ook! Ook. -> -
        - Ook. Ook? -> .
        - Ook? Ook. -> ,
        - Ook! Ook? -> [
        - Ook? Ook! -> ]

        Details:
            * This implementation wraps the memory pointer for ">" and "<"
            * It is time-limited to 60 seconds, to prevent hangups
            * The program starts with 100 memory cells, chosen arbitrarily
        """

        logging.debug("Attempting ook")

        # Convert Ook to Brainfuck
        brainfuck_code = self.ook_to_brainfuck(ctext)
        if brainfuck_code is None:
            logging.debug("Failed to convert Ook to Brainfuck")
            return None

        # Now interpret the Brainfuck code
        result = ""
        memory = [0] * 100
        codeptr, memptr = 0, 0  # Instruction pointer and stack pointer
        timelimit = 60  # The timeout in seconds

        bracemap, isbf = self.bracemap_and_check(brainfuck_code)

        # If it doesn't appear to be valid brainfuck code
        if not isbf:
            logging.debug("Failed to interpret brainfuck due to invalid characters")
            return None

        # Get start time
        start = time.time()

        while codeptr < len(brainfuck_code):

            current = time.time()

            # Return none if we've been running for over a minute
            if current - start > timelimit:
                logging.debug("Failed to interpret brainfuck due to timing out")
                return None

            cmd = brainfuck_code[codeptr]

            if cmd == "+":
                if memory[memptr] < 255:
                    memory[memptr] = memory[memptr] + 1
                else:
                    memory[memptr] = 0

            elif cmd == "-":
                if memory[memptr] > 0:
                    memory[memptr] = memory[memptr] - 1
                else:
                    memory[memptr] = 255

            elif cmd == ">":
                if memptr == len(memory) - 1:
                    memory.append(0)
                memptr += 1

            elif cmd == "<":
                if memptr == 0:
                    memptr = len(memory) - 1
                else:
                    memptr -= 1

            # If we're at the beginning of the loop and the memory is 0, exit the loop
            elif cmd == "[" and memory[memptr] == 0:
                codeptr = bracemap[codeptr]

            # If we're at the end of the loop and the memory is >0, jmp to the beginning of the loop
            elif cmd == "]" and memory[memptr]:
                codeptr = bracemap[codeptr]

            # Store the output as a string instead of printing it out
            elif cmd == ".":
                result += chr(memory[memptr])

            # Handle input command - set memory to 0 (or some default value) to avoid hanging
            elif cmd == ",":
                # For automated decryption, we assume null byte or skip input
                memory[memptr] = 0

            codeptr += 1

        logging.info(f"Ook successful, returning '{result}'")
        return result

    def ook_to_brainfuck(self, ook_program: str) -> Optional[str]:
        """
        Converts an Ook! program to Brainfuck.
        """
        # Define the Ook to Brainfuck mapping based on standard Ook! specification
        ook_map = {
        "ook. ook?": ">",
        "ook? ook.": "<",
        "ook. ook.": "+",
        "ook! ook!": "-",
        "ook! ook.": ".",
        "ook. ook!": ",",
        "ook! ook?": "[",
        "ook? ook!": "]",
    }

        # Clean up the input - remove extra whitespace and normalize
        cleaned = ook_program.lower().strip()
        
        # Split into tokens based on spaces
        tokens = cleaned.split()
        
        # Group tokens into pairs
        brainfuck_code = []
        i = 0
        while i < len(tokens) - 1:
            pair = f"{tokens[i]} {tokens[i+1]}"
            if pair in ook_map:
                brainfuck_code.append(ook_map[pair])
                i += 2  # Move to next pair
            else:
                # Skip invalid pairs - could be noise or incomplete input
                i += 1
        
        if not brainfuck_code:
            return None
            
        return "".join(brainfuck_code)

    def bracemap_and_check(self, program: str) -> Tuple[Optional[Dict], bool]:
        """
        Create a bracemap of brackets in the program, to compute jmps.
        Maps open -> close brackets as well as close -> open brackets.

        Also returns True if the program is valid Brainfuck code. If False, we
        won't even try to run it.
        """

        open_stack = []
        bracemap = dict()
        legal_instructions = {"+", "-", ">", "<", "[", "]", ".", ","}
        legal_count = 0

        # If the program actually outputs anything (contains ".")
        prints = False

        for idx, instruction in enumerate(program):
            # If instruction is brainfuck or whitespace, it counts
            if instruction in legal_instructions or re.match(r"\s", instruction):
                legal_count += 1

            if not prints and instruction == ".":
                # If there are no "." instructions then this program will not output anything
                prints = True

            elif instruction == "[":
                open_stack.append(idx)

            elif instruction == "]":
                try:
                    opbracket = open_stack.pop()
                    bracemap[opbracket] = idx
                    bracemap[idx] = opbracket
                except IndexError:
                    # Mismatched braces, not a valid program
                    # Closing braces > opening braces
                    return (None, False)

        # 1. All characters are instructions or whitespace
        # 2. There are no extra open braces
        # 3. There is at least one character to be "printed"
        # (result is >=1 in length)
        is_brainfuck = legal_count == len(program) and len(open_stack) == 0 and prints

        return bracemap, is_brainfuck

    @staticmethod
    def priority() -> float:
        # Increase priority to ensure Ook is tested when text contains Ook patterns
        return 0.25
    
    def getParams() -> Optional[Dict[str, ParamSpec]]:
        return {
            "dict": ParamSpec(
                desc="Ook alphabet (default English)",
                req=False,
                default="cipheydists::list::englishAlphabet",
            )
        }

    @staticmethod
    def getTarget() -> str:
        return "ook"
    
    def fitness(self, text: str) -> float:
        """
        Determines how likely the input text is to be an Ook program.
        Looks for the characteristic pattern of Ook tokens.
        """
        # Count occurrences of Ook tokens
        ook_dot_count = text.lower().count('ook.')
        ook_exclamation_count = text.lower().count('ook!')
        ook_question_count = text.lower().count('ook?')
        
        total_chars = len(text)
        
        if total_chars == 0:
            return 0.0
        
        # Calculate the proportion of Ook tokens in the text
        ook_token_proportion = (ook_dot_count + ook_exclamation_count + ook_question_count) / total_chars
        
        # Check if the text contains Ook tokens
        # We lower the threshold since Ook programs also contain whitespace, newlines, etc.
        if ook_token_proportion > 0.1:  # At least 10% of the text should be Ook tokens
            # Additional check: ensure we have all three types of tokens
            if ook_dot_count > 0 and ook_exclamation_count > 0 and ook_question_count > 0:
                # Return a score that reflects both the proportion and the balance of tokens
                min_tokens = min(ook_dot_count, ook_exclamation_count, ook_question_count)
                max_tokens = max(ook_dot_count, ook_exclamation_count, ook_question_count)
                balance_score = min_tokens / max_tokens if max_tokens > 0 else 0
                
                # Combine proportion and balance scores
                return ook_token_proportion * 0.7 + balance_score * 0.3
        
        return 0.0

    def __init__(self, config: Config):
        super().__init__(config)
        self.ALPHABET = config.get_resource(self._params()["dict"], WordList)

    @staticmethod
    def getParams() -> Optional[Dict[str, ParamSpec]]:
        return {
            "dict": ParamSpec(
                desc="Ook alphabet (default English)",
                req=False,
                default="cipheydists::list::englishAlphabet",
            )
        }

    @staticmethod
    def getTarget() -> str:
        return "ook"