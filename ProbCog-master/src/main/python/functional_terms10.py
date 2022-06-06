# from asyncio.windows_events import NULL
from collections import defaultdict
from pickletools import string1
from re import L
from itertools import combinations, count
d = defaultdict(list)
import re


def get_functional_terms(dict_func_term):
    # print("dict_func_term ", dict_func_term)
    list_func_term =[]
    for key, value in dict_func_term.items():        
        if len(value) > 1:
            func_term = key + "("
            for i in range (len(value)):
                if i == len(value) - 1:
                    func_term += dict_func_term[key][i] +")"
                else:
                    func_term += dict_func_term[key][i] + ", " 
                
            list_func_term.append(func_term)
        else:
            list_func_term.append(key + "(" + dict_func_term[key][0] + ")")
    # print("list_func_term", list_func_term)
    return list_func_term

def removing_additional_brackets(formula):
    for i, x in enumerate(formula): 
        if x == ">":
            if formula [i+2] == "(":
               formula = formula[:i+1] + " " + formula[(i+3):]
    return formula            
            

def finding_functional_terms(formula):
    string =""
    count = 0 
    no_of_func_term = 0
    arg_no = 0
    arguments_inside_functional_terms = defaultdict(list)
    for i, x in enumerate(formula): 
        # print(i, x) 
        if x == "(":
            count +=1;
        elif x == ")":
            count -=1;
        if count == 2 :
            if x == "(":
                # print("formula[i] ", formula[i])
                # print("formula[i-1]..", formula[i-1])
                if formula[i-1] != " ":
                    no_of_func_term +=1
                    # print("no_of_func_term ", no_of_func_term)
                    #.....................finding predicate name where the functional term in.....
                    arg_no = 0
                    for j in range(i-1, -1, -1):
                    # print("formula[j] ",formula[j])
                        if formula[j] == ",":
                            arg_no = j
                            break
                        if formula[j] == "(":
                            arg_no = j-1
                            break
                # print("arg_no ", arg_no)
                #..................finding arguments ......
                    string = ""
                    for j in range(i+1, len(formula)):
                        if formula[j] == ")":
                            break
                        elif arg_no > 0:
                            if formula[j] == ",":
                                arguments_inside_functional_terms[formula[arg_no+2:i]].append(string)
                                string = ""
                                string += formula[j+1].rstrip().lstrip()
                            else:
                                string += formula[j].rstrip().lstrip()
                    arguments_inside_functional_terms[formula[arg_no+2:i]].append(string)                     
            # print("string ", string)
                # print("functional_predicate ", formula[arg_no+2:i] )
    # print("There is a functional term", arguments_inside_functional_terms)
        # print("count ", count)
        # print("............................")
    return arguments_inside_functional_terms
    
def change_funct_into_prop(formula, list_func_term):
    replaced_formula = formula.replace ("=>", "+").replace("^", "+").replace("v","+")
    splitted_formula = replaced_formula.split("+")
    prop_list = []
    # print("splitted_formula ", splitted_formula)
    # print("list_func_term ", list_func_term)
    # print(".........................")
    for z in splitted_formula:
        count = 0
        # print(z)
        for i, y in enumerate (z):
            if y == "(":
                count += 1;
            elif y == ")":
                count -=1;
            if count == 2 :
                # print("......", formula[i-1])
                if formula[i-1] != " ":
                    for x in list_func_term:
                        term = z.replace(x, x[:x.index("(")]+"_prop")
                        formula = formula.replace(z, term)
                        prop_list.append(x[:x.index("(")]+"_prop")
                break
    # print(prop_list)
    # print(formula)
    return formula, prop_list
    
def change_funct_into_proposition(formula, prop_list, arguments_inside_functional_terms):
    # print("............................................")
    All_list_funct_propostions = []
    list_funct_propostions = []
    formula = formula.replace ("=>", "+").replace("^", "+").replace("v","+")
    splitted_formula = formula.split("+")
    # print("arguments_inside_functional_terms ", arguments_inside_functional_terms)
    # print("..............................................")
    # print("prob_list ", prop_list)
    # print("..............................................")
    # print("splitted_formula ", splitted_formula)
    # print("..............................................")
    for key, value in arguments_inside_functional_terms.items():
        s1 = ""
        s1 = key + "_proposition("
        for i in range (len(value)):
            if i >0:
                s1 +=  ", "+ value[i]
            else:
                s1 += value[i]  
            # print("s1 ", s1)      
        for x in splitted_formula:
            str = key +"_prop"
            if str in x:
                if "(" in x:
                    arguments = x[x.find("(")+1:x.find(")")]
                    arguments = arguments.split(",")
                    for y in arguments:
                        if y not in s1:
                            s1 += ", " + y
                # s2 = ""
                # count = x.index("(")
                # for i in range(count+1, len(x)):
                #     # print(x[i])
                #     if x[i] == ")":
                #             break
                #     else: 
                #         s2 += x[i]
        All_list_funct_propostions.append(s1 + ")")
        # print("..............................................")
        # print("All_list_funct_propostions", All_list_funct_propostions)
        #...elemenate same name variables inside propositions
        # for item in combinations(All_list_funct_propostions, 2):
        #     if any(i in item[1] for i in item[0]):
        #         list_funct_propostions = item
    #     print(list_funct_propostions)
    # print("..............................................")
    # if len(list_funct_propostions) <= 0:
    #     return All_list_funct_propostions
    # else:
    #     return(list_funct_propostions)
    return All_list_funct_propostions

def final_converted_formula(formula, list_funct_propostions):
    if len(list_funct_propostions) > 0:
        if formula[-1] == ".":
            formula = formula.replace(".","")    
            for x in list_funct_propostions:
                formula += " ^ " + x
            formula += "."
        else:
            for x in list_funct_propostions:
                formula += " ^ " + x        
    return formula

def checkingBraces(formula):
    count = 0
    for i, x in enumerate(formula): 
        if x == "(":
            count +=1;
        elif x == ")":
            count -=1;
    if count > 0:
        for i in range (count):
            formula += ")"
    formula = formula.rstrip().lstrip()
    return formula
    
    
    
formula1 = "ck(group, group_goal(group, goal)) => group_goal(group, goal)."
formula2 = "commonknowledge(Citizen, group_goal(Citizen, Secure_city))."
formula3 = "commonknowledge(citizen, group_goal(Secure_city)) => groupGoal(Citizens, SecureCity)."
formula4 = "traitor(x) => (group_goal(Jury, punish(x)))"
formula5 = "traitor(x) ^ cooperate(x, group_goal(Secure_city)) => group_goal(Jury, punish(x))"
formula6 = "citizen(coperate(Secure_city), t)."
def converting_fol(formula): 
    # print("original formula ", formula)
    # print(".....................................")
    # if formula[-1] == ".":
    #         formula = formula.replace(".","")
    formula2 = removing_additional_brackets(formula)
    arguments_inside_functional_terms = finding_functional_terms(formula2)
    #print arguments inside the functional terms
    # print("arguments_inside_functional_terms ", arguments_inside_functional_terms)
    list_func_term = get_functional_terms(arguments_inside_functional_terms)
    #print the list of functional terms
    # print("list_func_term ", list_func_term)
    formula, prop_list = change_funct_into_prop(formula, list_func_term)
    # print("prop_list ", prop_list)
    list_funct_propostions = change_funct_into_proposition(formula, prop_list, arguments_inside_functional_terms)
    # print("list_funct_propostions ", list_funct_propostions)
    formula1 = final_converted_formula(formula, list_funct_propostions)
    # print("Changed formula ", formula)
    formula3 = checkingBraces(formula1)
    # print("Changed formula ", formula3)
    return formula3, arguments_inside_functional_terms

def print_formula(formula):
    print(formula)
       
# converting_fol("ck(Citizens, group_goal(x, y)) ^ goal(x, yo(z))")
# print_formula(formula1)
# print (removing_additional_brackets(formula4))