#-------------------------------------------------------------------------------
# Py Name:      TermColorText.py
# Author:       BikerDroid
# Created:      01-08-2016
# Revision:     16-08-2016
#-------------------------------------------------------------------------------
# Requirements:
# Python 3.x (developed in Python 3.5.1)
# ctype # Core Python3
# Uses windll for Windows and ANSI for Linux/Darwin systems
#-------------------------------------------------------------------------------
# Usage:
# tct = TermColorText('[ Terminal Color Text ]')
# tct.print('This','is','a','Test',3.1415,FG='green')
# tct.print('This','is','a','Test',3.1415,FG='white',BG='cyan',bold=True)
#-------------------------------------------------------------------------------
class TermColorText():
    """Simple Cross Platform (Windows, Linux, Darwin) Terminal/DOS-Prompt Text Color Class."""
    def __init__(self,terminal_title='',windows_terminal_color=''):
        
        from platform import system as os_type
        self.win_terminal_color = windows_terminal_color
        self.terminal_title = terminal_title
        self.os_type = os_type()
        
        # Windows
        self.win_fg = {'black': 0x00,'blue': 0x01,'green': 0x02,'cyan': 0x03,'red': 0x04,'magenta': 0x05,'yellow': 0x06,'grey': 0x07,'white': 0x07,'bold': 0x08}
        self.win_bg = {'black': 0x00,'blue': 0x10,'green': 0x20,'cyan': 0x30,'red': 0x40,'magenta': 0x50,'yellow': 0x60,'grey': 0x70,'white': 0x70,'bold': 0x80}        
        
        # Linux, Darwin
        self.beep = '\007'
        self.esc  = '\x1b['
        self.end  = '\x1b[0;0m'
        self.attrib  = {'reset': '0m','bright': '1m','bold': '1m','dim': '2m','italic': '3m','underscore': '4m','blink': '5m','blink2': '6m','reverse': '7m','hidden': '8m'}
        self.ansi_fg = {'black': '30m','red': '31m','green': '32m','yellow': '33m','blue': '34m','magenta': '35m','cyan': '36m','white': '37m','grey': '37m','default': '39m'}
        self.ansi_bg = {'black': '40m','red': '41m','green': '42m','yellow': '43m','blue': '44m','magenta': '45m','cyan': '46m','white': '47m','grey': '47m','default': '49m'}

        if self.os_type == 'Windows': # Init Windows
            
            from ctypes import windll, Structure, wintypes, c_ushort, byref
            from ctypes.wintypes import _COORD, _SMALL_RECT, WORD
            
            self.STD_INPUT_HANDLE  = -10
            self.STD_OUTPUT_HANDLE = -11
            self.STD_ERROR_HANDLE  = -12
    
            self.std_out_handle = windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
            self.SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
            self.GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

            class CONSOLE_SCREEN_BUFFER_INFO(Structure):
                _fields_ = [('dwSize',_COORD),('dwCursorPosition',_COORD),('wAttributes',c_ushort),('srWindow',_SMALL_RECT),('dwMaximumWindowSize',_COORD)]
            
            self.csbi = CONSOLE_SCREEN_BUFFER_INFO()
            self.csbi_byref = byref(self.csbi)
            
            self.default_colors = self.get_text_attr()
            self.default_fc = list(self.win_fg.keys())[list(self.win_fg.values()).index(self.default_colors & 0x07)]
            self.default_bc = list(self.win_bg.keys())[list(self.win_bg.values()).index(self.default_colors & 0x70)]
            
        self.set_terminal_title()
        self.set_win_terminal_color(self.win_terminal_color)

    def set_win_terminal_color(self,color):
        from os import system
        if len(color):
            if self.os_type == 'Windows':
                system('color '+color)
            
    def set_terminal_title(self):
        from os import system
        if len(self.terminal_title):
            if self.os_type == 'Windows':
                system('title '+self.terminal_title)
            else:
                print('\x1b]0;'+self.terminal_title+'\x07',flush=True) #\x1b]2;
                    
    def get_text_attr(self): # Windows
        self.GetConsoleScreenBufferInfo(self.std_out_handle,self.csbi_byref)
        return self.csbi.wAttributes
    
    def set_text_color(self,color): #Windows
        return self.SetConsoleTextAttribute(self.std_out_handle,color)

    def print(self,*args,FG=None,BG=None,bold=False):
        if self.os_type == 'Windows':
            if not FG: FG = self.default_fc
            if not BG: BG = self.default_bc
            FG = str(FG).lower().strip()
            BG = str(BG).lower().strip()
            if bold:
                self.set_text_color((self.win_fg['bold'] | self.win_fg[FG]) | self.win_bg[BG])
            else:
                self.set_text_color( self.win_fg[FG] | self.win_bg[BG])
            ends = ' '
            if len(args):
                for x, s in enumerate(args):
                    if x == len(args)-1: ends = ''
                    print(s,end=ends,flush=True)
            self.set_text_color(self.default_colors)
            print('')
        else: # Linux, Darwin 
            if not FG:
                FG = 'default'
            else:
                FG = str(FG).lower().strip()
                if not FG in self.ansi_fg: FG = 'default'
            if not BG:
                BG = 'default'
            else:
                BG = str(BG).lower().strip()
                if not BG in self.ansi_bg: BG = 'default'
            if bold:
                print(self.esc+self.attrib['bold'].strip('m')+';'+self.ansi_fg[FG].strip('m')+';'+self.ansi_bg[BG],end='',flush=True)
            else:
                print(self.esc+str(self.ansi_fg[FG]).strip('m')+';'+str(self.ansi_bg[BG]),end='',flush=True)
            ends = ' '
            if len(args):
                for x, s in enumerate(args):
                    if x == len(args)-1: ends = ''
                    print(s,end=ends,flush=True)
            self.set_text_color(self.default_colors)
            print(self.end)
# End class TermColorText()

def test():
    a = 'This'
    b = 'is'
    c = 'a'
    d = 'Color'
    e = '!!!'
    pi = 3.14
    
    tct = TermColorText('[ Terminal Color Text ]')
    
    tct.print(a,b,c,d,'Test',1,e,pi,FG='green')
    tct.print(a,b,c,d,'Test',2,e,pi,FG='green',bold=True)
    tct.print(a,b,c,d,'Test',3,e,pi)
    tct.print(a,b,c,d,'Test',4,e,pi,bold=True)
    tct.print(a,b,c,d,'Test',5,e,pi,FG='yellow')
    tct.print(a,b,c,d,'Test',6,e,pi,FG='yellow',bold=True)
    tct.print(a,b,c,d,'Test',7,e,pi,FG='blue')
    tct.print(a,b,c,d,'Test',8,e,pi,FG='blue',bold=True)
    tct.print(a,b,c,d,'Test',9,e,pi,FG='red')
    tct.print(a,b,c,d,'Test',10,e,pi,FG='red',bold=True)
    tct.print(a,b,c,d,'Test',11,e,pi,FG='cyan')
    tct.print(a,b,c,d,'Test',12,e,pi,FG='cyan',bold=True)
    tct.print(a,b,c,d,'Test',13,e,pi,FG='magenta')
    tct.print(a,b,c,d,'Test',14,e,pi,FG='magenta',bold=True)
    tct.print(a,b,c,d,'Test',15,e,pi,FG='green',BG='red')
    tct.print(a,b,c,d,'Test',16,e,pi,FG='white',BG='red',bold=True)
    tct.print(a,b,c,d,'Test',17,e,pi,FG='cyan',BG='blue',bold=True)
    tct.print(a,b,c,d,'Test',18,e,pi,FG='yellow',BG='green',bold=True)
    tct.print(a,b,c,d,'Test',19,e,pi,FG='white',BG='cyan',bold=True)
    tct.print()
    input('>>> Hit [Enter] to Exit <<<')
    
# ----------------------------------------------------------------------------------------
if __name__ == '__main__':
    test()
