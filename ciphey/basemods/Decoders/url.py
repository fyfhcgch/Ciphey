from typing import Dict, Optional
from urllib.parse import unquote_plus, unquote

import logging
from rich.logging import RichHandler

from ciphey.iface import Config, Decoder, ParamSpec, T, U, registry


@registry.register
class Url(Decoder[str]):
    def decode(self, ctext: T) -> Optional[U]:
        """
        Performs URL decoding
        Handles both standard %XX format and alternative =XX format
        """
        logging.debug("Attempting URL")
        result = ""
        try:
            # First try standard URL decoding
            result = unquote_plus(ctext, errors="strict")
            if result != ctext:
                logging.info(f"URL successful, returning '{result}'")
                return result
            
            # If standard decoding didn't change anything, check for =XX format
            # Replace =XX with %XX and try again
            if '=' in ctext:
                converted_text = ctext.replace('=', '%')
                result = unquote(converted_text, errors="strict")
                if result != ctext:
                    logging.info(f"URL (=XX format) successful, returning '{result}'")
                    return result
            
            return None
        except Exception:
            logging.debug("Failed to decode URL")
            return None

    @staticmethod
    def priority() -> float:
        return 0.8  # Increase priority to make URL decoding happen earlier

    def __init__(self, config: Config):
        super().__init__(config)

    @staticmethod
    def getParams() -> Optional[Dict[str, ParamSpec]]:
        return None

    @staticmethod
    def getTarget() -> str:
        return "url"
