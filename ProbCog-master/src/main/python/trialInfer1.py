import change_funct_terms as funct
from mlnQueryTool import MLNInfer
from collections import defaultdict
from pickletools import string1
from re import L
from itertools import combinations
d = defaultdict(list)
import ctypes
import tkinter as tk
from tkinter import ttk

#check the functional terms and chage if it has
filepath ="trial31.mln"
funct.change_functional_terms(filepath)

#infering MLN
inf = MLNInfer()
# mlnFiles = ["smoking.mln"]
# db = "smokingDB.db"
mlnFiles = [filepath]
db = "trial21.db"  

queries = "cooperate(Polites, SecureCity)"
# queries = "Cancer"
# queries = " individual_ethos(x, Ethos2) ^ cooperate(x, SecureCity)"
# queries = "individual_ethos(x, Ethos1) ^ cooperate(x, SecureCity)"
output_filename = "results.txt"
allResults = {}
tasks = (("exact inference", "PyMLNs"), ("MC-SAT", "J-MLNs"))
# tasks = (("MC-SAT", "PyMLNs"), ("MC-SAT", "J-MLNs"))
for method, engine in tasks[:-1]:
    allResults[(method, engine)] = inf.run(
        mlnFiles,
        db,
        method,
        queries,
        engine,
        output_filename,
        saveResults=True,
        maxSteps=100,
    )

for (method, engine), results in allResults.iteritems():
    print("Results obtained using %s and %s" % (engine, method))
    for atom, p in results.iteritems():
        print("  %.6f  %s" % (p, atom))


