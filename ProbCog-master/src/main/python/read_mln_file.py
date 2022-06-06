import functional_terms8 as funct_term
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
    label = ttk.Label(popup, text=msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()
 #................Read lines in python..................
# Using readlines()
file1 = open('trial.mln', 'r')
Lines = file1.readlines()
file1.close()

for i, line in enumerate(Lines):
    arguments_inside_functional_terms = funct_term.finding_functional_terms(line.strip())
    print("arguments_inside_functional_terms ", len(arguments_inside_functional_terms))
    if len(arguments_inside_functional_terms) > 0:
        print("i ", i)
        print(arguments_inside_functional_terms)
        converted_formula = funct_term.converting_fol(line.strip())
        print("converted_formula ", converted_formula)
        Lines[i] = converted_formula + "\n"
        popupmsg("Add predicates under predicate declaration")
file1.close()

new_file = open('trial.mln', "w+")
for line in Lines:
    new_file.write(line)

new_file.close()

