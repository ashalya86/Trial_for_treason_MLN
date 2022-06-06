import functional_terms8 as funct_term
def converting_fol(formula):
    """
    >>> converting_fol("traitor(x) => group_goal(Jury, time(x), punish(z, y)) ^ hai(time, iron(k, l))")
    'traitor(x) => group_goal(Jury, time_prop, punish_prop) ^ hai(time, iron_prop) ^  group_goal_proposition(Jury, x, time_prop, z, y, punish_prop)  ^  hai_proposition(time, k, l, iron_prop).'
    >>> converting_fol("commonknowledge(Citizen, group_goal(Secure_city))")
    'commonknowledge(Citizen, group_goal_prop) ^ commonknowledge_proposition(Citizen, Secure_city, group_goal_prop).'
    >>> converting_fol("commonknowledge(citizen, group_goal(Secure_city)) => groupGoal(Citizens, SecureCity).")
    'commonknowledge(citizen, group_goal_prop) => groupGoal(Citizens, SecureCity) ^ commonknowledge_proposition(citizen, Secure_city, group_goal_prop).'
    >>> converting_fol("citizen(coperate(Secure_city), t).")
    'citizen(coperate_prop, t) ^ citizen_proposition(Secure_city, coperate_prop, t).'
    """
    # print("original formula ", formula)
    if formula[-1] == ".":
            formula = formula.replace(".","")
    arguments_inside_functional_terms = funct_term.finding_functional_terms(formula)
    # print(arguments_inside_functional_terms)
    list_func_term = funct_term.get_functional_terms(arguments_inside_functional_terms)
    # print("list_func_term ", list_func_term)
    formula, prop_list = funct_term.change_funct_into_prop(formula, list_func_term)
    # print("changed formula ", formula, "prop_list ", prop_list)
    list_funct_propostions = funct_term.change_funct_into_proposition(formula, prop_list, arguments_inside_functional_terms)
    # print("list_funct_propostions ", list_funct_propostions)
    formula = funct_term.final_converted_formula(formula, list_funct_propostions)
    # print("Changed formula ", formula)
    return formula

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose = True)
