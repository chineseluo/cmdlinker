import sys
from time import sleep
from tqdm import tqdm

# 字符画的高度
height = 10

# 字符画的宽度
width = 20

# 字符画的字符集
chars = [' ', '.', '"', '^', '*', ':', '=', '!', '+', 'i', '>', ',', '<', '?', '&', '#']


def generate_ascii_art(height, width, chars):
    for _ in tqdm(range(height), file=sys.stdout, ncols=100, desc='Generating ASCII Art'):
        line = ''.join(random.choice(chars) for _ in range(width))
        print(line)
        sleep(0.1)  # 用于控制输出速度，减少闪烁


if __name__ == "__main__":
    import random

    generate_ascii_art(height, width, chars)