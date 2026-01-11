from typing import Dict, Optional

import logging
from rich.logging import RichHandler

try:
    from zmq.utils import z85
    Z85_AVAILABLE = True
except ImportError:
    z85 = None
    Z85_AVAILABLE = False

from ciphey.iface import Config, Decoder, ParamSpec, T, U, registry


@registry.register
class Z85(Decoder[str]):
    def decode(self, ctext: T) -> Optional[U]:
        """
        Performs Z85 decoding
        """
        if not Z85_AVAILABLE:
            logging.debug("Z85 not available (zmq not installed)")
            return None
        ctext_len = len(ctext)
        if ctext_len % 5:
            logging.debug(
                f"Failed to decode Z85 because length must be a multiple of 5, not '{ctext_len}'"
            )
            return None
        try:
            return z85.decode(ctext).decode("utf-8")
        except Exception:
            return None

    @staticmethod
    def priority() -> float:
        # Not expected to show up often, but also very fast to check.
        return 0.05

    def __init__(self, config: Config):
        super().__init__(config)

    @staticmethod
    def getParams() -> Optional[Dict[str, ParamSpec]]:
        return None

    @staticmethod
    def getTarget() -> str:
        return "z85"
