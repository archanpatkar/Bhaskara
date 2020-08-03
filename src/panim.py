import time

BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7

def clrscr():
    print("\033[2J",sep='',end='',flush=True)

def showcursor():
    print("\033[?25h",sep='',end='',flush=True)

def hidecursor():
    print("\033[?25l",sep='',end='',flush=True)

def foreground(color):
    print("\033[3",color,"m",sep='',end='',flush=True)

def background(color):
    print("\033[4",color,"m",sep='',end='',flush=True)

def gotoxy(x,y):
    print("\033[",y,";",x,"H",sep='',end='',flush=True)

def bold(str):
    return "\033[1m{}".format(str)

# echo -e "\e[3mitalic\e[0m"
# echo -e "\e[3m\e[1mbold italic\e[0m"
# echo -e "\e[4munderline\e[0m"
# echo -e "\e[9mstrikethrough\e[0m"
# echo -e "\e[31mHello World\e[0m"
# echo -e "\x1B[31mHello World\e[0m"

def sleep(n):
    time.sleep(n)

def wait(echo = True):
    if(echo):
        input("\nPress Enter to Continue")
    else:
        input("\n")

def putchar(ch):
    if(len(ch) == 1):
        print(ch,sep='',end='',flush=True)