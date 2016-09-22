#-------------------------------------------------------------------------------
# Py Name:      TermColorText.py
# Author:       BikerDroid
# Created:      01-08-2016
# Revision:     22-09-2016
#-------------------------------------------------------------------------------
# Revision:
# 22-09-2016 : Added get_visual_screen_size(), clear_line()
#-------------------------------------------------------------------------------
# Requirements:
# Python 3.5.x (developed in Python 3.5.1)
# ctype  # Core Python3
# struct # Core Python3
#-------------------------------------------------------------------------------
# Example:
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
            
            from ctypes import windll, Structure, wintypes, c_ushort, byref, c_ulong, c_int, c_char, c_long, pointer
            from ctypes.wintypes import _COORD, _SMALL_RECT
            from struct import unpack

            self._COORD = _COORD
            self._SMALL_RECT = _SMALL_RECT
            self.Structure = Structure
            self.c_int  = c_int
            self.c_char = c_char
            self.byref = byref
            self.c_ushort = c_ushort
            self.c_ulong = c_ulong
            self.c_long = c_long
            self.pointer = pointer
            self.unpack = unpack
            
            class CONSOLE_SCREEN_BUFFER_INFO(self.Structure):
                _fields_ = [('dwSize',self._COORD),('dwCursorPosition',self._COORD),('wAttributes',self.c_ushort),('srWindow',self._SMALL_RECT),('dwMaximumWindowSize',self._COORD)]

            class CONSOLE_CURSOR_INFO(self.Structure):
                _fields_ = [('dwSize',self.c_ulong), ('bVisible', self.c_int)]

            self.STD_INPUT_HANDLE  = -10
            self.STD_OUTPUT_HANDLE = -11
            self.STD_ERROR_HANDLE  = -12
            
            self.csbi = CONSOLE_SCREEN_BUFFER_INFO()
            self.csbi_byref = byref(self.csbi)
            self.std_out_handle = windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
            self.SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
            self.GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
                        
            self.cci = CONSOLE_CURSOR_INFO()
            self.cci_byref = byref(self.cci)
            self.SetConsoleCursorPosition = windll.kernel32.SetConsoleCursorPosition
            self.GetConsoleCursorInfo = windll.kernel32.GetConsoleCursorInfo(self.std_out_handle, self.cci_byref)
            self.SetConsoleCursorInfo = windll.kernel32.SetConsoleCursorInfo

            self.FillConsoleOutputCharacterA = windll.kernel32.FillConsoleOutputCharacterA
            self.FillConsoleOutputAttribute = windll.kernel32.FillConsoleOutputAttribute
            
            self.init_screen_size = self.get_visual_screen_size()
            
            self.default_colors = self.get_text_attr()
            self.default_fc = list(self.win_fg.keys())[list(self.win_fg.values()).index(self.default_colors & 0x07)]
            self.default_bc = list(self.win_bg.keys())[list(self.win_bg.values()).index(self.default_colors & 0x70)]
            
            self.set_win_terminal_color(self.win_terminal_color)
            
        self.set_terminal_title()
        
    def get_visual_screen_size(self):
        if self.os_type == 'Windows':
            if self.GetConsoleScreenBufferInfo(self.std_out_handle,self.csbi_byref):
                (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = self.unpack("hhhhHhhhhhh", self.csbi)
                sizex = right - left + 1
                sizey = bottom - top + 1
                return sizex, sizey
            else:
                return 0,0
        else:
            pass
        
    def clear_line(self,y):
        if self.os_type == 'Windows':
            sx, sy = self.get_visual_screen_size()
            clrstr = ' '*(sx-1)
            self.gotoxy(1,y)
            self.print(clrstr)
            self.gotoxy(1,y)

    def clear_screen(self):
        if self.os_type == 'Windows':
            clear_start = self._COORD(0,0)
            clear_length = self.csbi.dwSize.X * self.csbi.dwSize.Y
            self.SetConsoleCursorPosition(self.std_out_handle, clear_start)
            chars_written = self.c_int()
            self.FillConsoleOutputCharacterA(self.std_out_handle, self.c_char(32), clear_length, clear_start, self.byref(chars_written))
            self.FillConsoleOutputAttribute(self.std_out_handle, self.csbi.wAttributes, clear_length, clear_start, self.byref(chars_written))
            self.SetConsoleCursorPosition(self.std_out_handle, clear_start)
            print('',end='',flush=True) # Not really needed.
        else:
            print('\x1b[2J\x1b[H',flush=True)
            
    def show_cursor(self):
        if self.os_type == 'Windows':
            self.cci.bVisible = True
            self.SetConsoleCursorInfo(self.std_out_handle,self.cci_byref)
        else:
            print('\x1b[?25h',flush=True)
        
    def hide_cursor(self):
        if self.os_type == 'Windows':
            self.cci.bVisible = False
            self.SetConsoleCursorInfo(self.std_out_handle,self.cci_byref)
        else:
            print('\x1b[?25l',flush=True)

    def set_win_terminal_color(self,color):
        from os import system
        if self.os_type == 'Windows':
            if len(color):
                system('color '+color)
            
    def set_terminal_title(self,titletxt=''):
        from os import system
        if not len(titletxt): titletxt = self.terminal_title
        if len(titletxt):
            if self.os_type == 'Windows':
                system('title '+titletxt)
            else:
                print('\x1b]0;'+titletxt+'\x07',flush=True) #\x1b]2;
                    
    def get_text_attr(self): # Windows
        if self.os_type == 'Windows':
            self.GetConsoleScreenBufferInfo(self.std_out_handle,self.csbi_byref)
            return self.csbi.wAttributes
    
    def set_text_color(self,color): #Windows
        if self.os_type == 'Windows':
            return self.SetConsoleTextAttribute(self.std_out_handle,color)
        
    def get_cursor_xy(self):
        if self.os_type == 'Windows':
            self.GetConsoleScreenBufferInfo(self.std_out_handle,self.csbi_byref)
            x = self.csbi.dwCursorPosition.X + 1
            y = self.csbi.dwCursorPosition.Y + 1
            return x, y
        else:
            pass
    
    def gotoxy(self,x=1,y=1):
        if x <= 0: x = 1
        if y <= 0: y = 1
        if self.os_type == 'Windows':
            #new_pos = self._COORD(min(max(0, self.csbi.dwCursorPosition.X + x_offset),self.csbi.dwSize.X), min(max(0, self.csbi.dwCursorPosition.Y + y_offset),self.csbi.dwSize.Y))
            new_pos = self._COORD(x-1,y-1)
            self.SetConsoleCursorPosition(self.std_out_handle,new_pos)
        else:
            print('\033['+str(x)+'x;'+str(y)+'H',flush=True)
    
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
            
    def printxy(self,x,y,*args,FG=None,BG=None,bold=False):
        self.gotoxy(x,y)
        self.print(*args,FG=FG,BG=BG,bold=bold)
# End class TermColorText()

def test():
    from time import sleep
    
    a = 'This'
    b = 'is'
    c = 'a'
    d = 'Color'
    e = '!!!'
    pi = 3.14
    s = a+' '+b+' '+c+' '+d+' Test '+e+' '
    
    tct = TermColorText('[ Terminal Color Text ]')
    sleep(2)
    
    tct.clear_screen()
    
    tct.set_terminal_title('X,Y='+str(tct.get_cursor_xy()))
    sleep(2)
    
    tct.hide_cursor()
    sleep(2)
    
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

    tct.set_terminal_title('X,Y='+str(tct.get_cursor_xy()))
    sleep(2)

    tct.gotoxy(35,10)
    tct.set_terminal_title('X,Y='+str(tct.get_cursor_xy()))
    sleep(2)
    
    input('>> Hit [Enter] to Exit <<')

    tct.clear_screen()

    tct.set_terminal_title('X,Y='+str(tct.get_cursor_xy()))
    sleep(2)

    s = 'Goodbye!'
    scrx, scry = tct.get_visual_screen_size()
    center_y = scry//2
    center_x = (scrx//2)-(len(s)//2)
    tct.printxy(center_x,center_y,s,FG='green',bold=True)
    
    tct.set_terminal_title('X,Y='+str(center_x)+','+str(center_y) )
    sleep(2)

    tct.gotoxy(1,center_y+2)
    
    tct.set_terminal_title('X,Y='+str(tct.get_cursor_xy()))

    tct.show_cursor()
    sleep(3)
    
# ----------------------------------------------------------------------------------------
if __name__ == '__main__':
    test()
