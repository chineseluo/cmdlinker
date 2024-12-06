from termcolor import colored
import pyfiglet

# 字符串颜色
figlet_text = pyfiglet.Figlet()
color_text = figlet_text.renderText('Hello World')
print(colored(color_text, 'red'))

