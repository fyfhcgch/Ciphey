"""
当铺密码解码器
将汉字转换为数字，然后根据情况进行ASCII或十六进制解码
"""

from typing import Optional, Dict
import re
from ciphey.iface import Config, Decoder, ParamSpec, T, U, registry

@registry.register
class Dangpu(Decoder[str]):
    """
    当铺密码解码器
    将汉字按照笔画出头数量转换为数字，然后解码
    """

    def __init__(self, config: Config):
        super().__init__(config)
        # 当铺密码映射表：汉字 -> 笔画出头数(对应数字)
        self.dangpu_map = {
            '口': '0', '田': '0',  # 0个出头
            '由': '1',  # 1个出头
            '中': '2',  # 2个出头
            '人': '3',  # 3个出头
            '工': '4',  # 4个出头
            '大': '5',  # 5个出头
            '王': '6',  # 6个出头
            '夫': '7',  # 7个出头
            '井': '8',  # 8个出头
            '羊': '9',  # 9个出头
        }

    def decode(self, ctext: T) -> Optional[U]:
        """
        解码当铺密码
        """
        # 按照空格分割文本，每个部分代表一个数字组
        parts = re.split(r'\s+', ctext.strip())
        
        if not parts or all(len(part.strip()) == 0 for part in parts):
            return None

        # 将每个部分的汉字转换为数字，然后组合成ASCII码
        ascii_text = ""
        
        for part in parts:
            if not part:
                continue
                
            # 将当前部分的汉字转换为数字序列
            digit_part = ""
            for char in part:
                if char in self.dangpu_map:
                    digit_part += self.dangpu_map[char]
                else:
                    # 如果遇到不在映射表中的汉字，返回空
                    return None
            
            if digit_part:
                try:
                    # 将整个部分的数字作为一个ASCII码
                    num = int(digit_part)
                    if 32 <= num <= 126:  # 可打印ASCII范围
                        ascii_text += chr(num)
                    else:
                        # 如果数字超出可打印范围，直接返回None
                        return None
                except ValueError:
                    return None

        if ascii_text:
            return ascii_text

        return None

    @staticmethod
    def priority() -> float:
        # 设置适当优先级，高于其他中文相关的解码器
        return 0.1

    @staticmethod
    def getTarget() -> str:
        # 当铺密码的目标是中文汉字序列
        return "dangpu"

    @staticmethod
    def getParams() -> Optional[Dict[str, ParamSpec]]:
        return None