import functional_terms10 as funct_term
from collections import defaultdict
from pickletools import string1
from re import L
from itertools import combinations
d = defaultdict(list)
import ctypes
import tkinter as tk
from tkinter import ttk

def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text = msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()
    
def change_functional_terms(filepath):
    file1 = open(filepath, 'r')
    Lines = file1.readlines()
    file1.close()
    predicate_list = []
    for i, line in enumerate(Lines):
        if line.strip():
            converted_formula, arguments_inside_functional_terms = funct_term.converting_fol(line.strip())
            # print("converted_formula ", converted_formula)
            Lines[i] = converted_formula + "\n"
            if bool (arguments_inside_functional_terms) == True:
                for key, value in arguments_inside_functional_terms.items():
                    predicate_list.append(key) 
    if  len(predicate_list) > 0:  
        msg = "Add predicate " 
        for i in list(set(predicate_list)):
            msg += i + "_proposition(), \n"
        msg += " with appropriate arguments under predicate declaration"
        popupmsg(msg)    
    file1.close()

    new_file = open(filepath, "w+")
    for line in Lines:
        new_file.write(line)
    new_file.close()
    return new_file

# change_functional_terms("trial31.mln")