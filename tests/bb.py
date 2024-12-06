import sys
import time
from time import sleep
from tqdm import tqdm


def ccc():
    print("###")
    # time.sleep(5)

def generate_ascii_art(height=10):
    for _ in tqdm(range(height), file=sys.stdout, ncols=100, desc='Generating CMD object'):
        # line = ''.join(random.choice(chars) for _ in range(width))
        # print(line)
        ccc()
        sleep(0.1)  # 用于控制输出速度，减少闪烁


if __name__ == "__main__":
    import random

    generate_ascii_art(height)