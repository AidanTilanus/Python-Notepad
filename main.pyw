import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import re
import configparser
import pyperclip
from plyer import notification
import subprocess

NOTEPAD_NAME = 'Notepad'

class Notepad:
    def __init__(self, root, config_file='notepad_config.ini'):
        self.root = root
        self.root.title(NOTEPAD_NAME)
        self.root.geometry('400x300')
        
        #config
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        #Vars
        self.autosaveBool = tk.BooleanVar(value=False)
        
        self.load_config()
        
        # Add text
        self.text_field = tk.Text(self.root, height=400, width=300) 
        self.text_field.pack()
        self.text_field.focus_set()
        
        # Add menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Add file menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='New', command=self.new_file, accelerator='Ctrl+N')
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Save', command=self.save_file, accelerator='Ctrl+S')
        self.file_menu.add_command(label='Save As', command=self.save_file_as, accelerator='Ctrl+Shift+S')
        self.file_menu.add_command(label='Open', command=self.open_file, accelerator='Ctrl+O')
        
        # Add settings menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Settings', menu=self.settings_menu)
        self.settings_menu.add_checkbutton(label='Auto Save', variable=self.autosaveBool)
        
        # Add tools menu
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Tools', menu=self.tools_menu)
        self.tools_menu.add_command(label='Copy Text', command=self.copy_text, accelerator='Ctrl+Shift+C')

        # Create a submenu for run types
        self.run_types = tk.Menu(self.tools_menu, tearoff=False)

        self.tools_menu.add_cascade(label="Run", menu=self.run_types)
        self.run_types.add_command(label="Python", command=lambda: self.run_script('python'))
        self.run_types.add_command(label="Perl", command=lambda: self.run_script('perl'))
        self.run_types.add_command(label="Ruby", command=lambda: self.run_script('ruby'))
        self.run_types.add_command(label="Bash", command=lambda: self.run_script('bash'))
        self.run_types.add_command(label="PHP", command=lambda: self.run_script('php'))
        self.run_types.add_command(label="Node.js", command=lambda: self.run_script('node'))
        
        #Add key commands
        self.root.bind('<Control-n>', self.new_file)
        self.root.bind('<Control-N>', self.new_file)
        
        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-S>', self.save_file)
        
        self.root.bind('<Control-Shift-s>', self.save_file_as)
        self.root.bind('<Control-Shift-S>', self.save_file_as)
        
        self.root.bind('<Control-o>', self.open_file)
        self.root.bind('<Control-O>', self.open_file)
        
        self.root.bind('<Control-Shift-c>', self.copy_text)
        self.root.bind('<Control-Shift-C>', self.copy_text)
        
        #setup drag and drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.dnd_open)
        
        #misc
        root.protocol('WM_DELETE_WINDOW', self.close_notepad)
        
        self.current_file_path = None
        self.text_field.delete(1.0, tk.END)
        
        self.autosave()

    def new_file(self, event=None):
        saved = self.check_if_saved()
        if saved or saved == None:
            self.text_field.delete(1.0, tk.END)
            self.current_file_path = None

    def save_file(self, event=None):
        if self.current_file_path:
            with open(self.current_file_path, 'w') as file:
                file.write(self.text_field.get(1.0, tk.END))
        else:
            file_save_path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
            if file_save_path:
                with open(file_save_path, 'w') as file:
                    file.write(self.text_field.get(1.0, tk.END))
                    
                self.current_file_path = file_save_path

    def save_file_as(self, event=None):
        self.current_file_path = None
        self.save_file()
    
    def open_file(self, event=None):
        self.current_file_path = filedialog.askopenfilename(filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if self.current_file_path:
            try:
                with open(self.current_file_path, 'r') as file:
                    self.text_field.delete(1.0, tk.END)
                    self.text_field.insert(tk.END, file.read())
            except:
                self.show_load_error()
                
    def dnd_open(self, event=None):
        self.current_file_path = event.data
        self.current_file_path = re.sub(r'[\{\}]', '', self.current_file_path)
        try:
            with open(self.current_file_path, 'r') as file:
                self.text_field.delete(1.0, tk.END)
                self.text_field.insert(tk.END, file.read())
        except:
            self.show_load_error()
            
    def show_load_error(self):
        messagebox.showerror('Notepad', "couldn't read the file!")
        self.new_file()
            
    def autosave(self):
        if self.autosaveBool.get():
            if self.current_file_path:
                self.save_file()
            
        self.root.after(60000, self.autosave)
        
    def copy_text(self, event=None):
        pyperclip.copy(self.text_field.get("1.0", tk.END))
        notification.notify(title=NOTEPAD_NAME, message="Copied all the text in the file use Ctrl+V to paste the text.", timeout=10)
        
    def close_notepad(self):
        saved = self.check_if_saved()
        if saved or saved == None:
            self.save_config()
            self.root.destroy()
        
    def load_config(self):
        try:
            self.config.read(self.config_file)
            
            self.autosaveBool.set(self.config.getboolean('Settings', 'autosave'))
            
        except configparser.Error as e:
            pass

    def save_config(self):
        try:
            self.config['Settings'] = {'autosave': self.autosaveBool.get()}

            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
        except configparser.Error as e:
            messagebox.showerror('Notepad', e)
        
    def check_if_saved(self):
        if self.current_file_path:
            if self.autosaveBool.get():
                self.save_file()
                return True
            else:
                with open(self.current_file_path, 'r') as file:
                    file_content = file.read().strip()

                text_field_content = self.text_field.get(1.0, tk.END).strip()

                if file_content != text_field_content:
                    self.saveMessage = messagebox.askyesnocancel('Notepad', 'Do you want to save changes before closing?')
                    if self.saveMessage is True:
                        self.save_file()
                        return True
                    elif self.saveMessage is False:
                        return True
                    else: # Handle the case when the user cancels the operation
                        return False
        else:
            if self.text_field.get(1.0, tk.END).strip():
                self.saveMessage = messagebox.askyesnocancel('Notepad', 'Do you want to save changes before closing?')
                if self.saveMessage is True:
                    self.save_file()
                    return True
                elif self.saveMessage is False:
                    return True
                else: # Handle the case when the user cancels the operation
                    return False
            else:
                return True
            
    def run_script(self, language):
        if self.current_file_path:
            subprocess.Popen(["start", "cmd", "/k", language, self.current_file_path], shell=True)
        else:
            messagebox.showerror('Notepad', "file is not saved!")


if __name__ == '__main__':
    root = TkinterDnD.Tk()
    notepad = Notepad(root)
    root.mainloop()
