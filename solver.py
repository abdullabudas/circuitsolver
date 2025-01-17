from loopanalysis import Loop
from loopanalysis import Resistor
from loopanalysis import VoltageSource
from loopanalysis import CurrentSource

explored_superloops = set()
def write_equations_with_no_superloops(loops_arrays, loops_arrays1):
    equations = []
    for loop in loops_arrays:
        equation = ""
        for comp in loop.components:
            if isinstance(comp, VoltageSource):
                if comp.dependency == "Independent":
                    if comp.polarity[1] == "+":
                        if str(loop.number) == comp.polarity[0]:
                            equation += " + " + comp.name
                        else:
                            equation += " - " + comp.name
                    else:
                        if str(loop.number) == comp.polarity[0]:
                            equation += " - " + comp.name
                        else:
                            equation += " + " + comp.name
                else:  # Dependent Voltage Source
                    my_dependency = component_lookup(comp.dependency[1], loops_arrays1)
                    if len(my_dependency) == 1:
                        if comp.dependency.startswith(
                                    "V"):
                            if comp.polarity[1] == "+":
                                if str(loop.number) == comp.polarity[0]:
                                    equation += "+" + str(comp.value) + " * i" + str(
                                            my_dependency) + " * " + comp.dependency
                                else:
                                    equation += "-" + str(comp.value) + " * i" + str(
                                            my_dependency[0][0]) + " * " + my_dependency[0][1].name
                            else:
                                if str(loop.number) == comp.polarity[0]:
                                    equation += "-" + str(comp.value) + " * i" + str(
                                            my_dependency) + " * " + comp.dependency
                                else:
                                    equation += "+" + str(comp.value) + " * i" + str(
                                            my_dependency) + " * " + comp.dependency
                        else:
                            if str(loop.number) == comp.polarity[0]:
                                equation += "-" + str(comp.value) + " * i" + str(my_dependency)
                            else:
                                equation += "+" + str(comp.value) + " * i" + str(my_dependency)
                    else:
                        loop1, loop2 = my_dependency
                        if comp.dependency.startswith(
                                    "V"):
                            # Voltage Source that depends on the voltage drop across a resistor
                            if comp.polarity[1] == "+":
                                if str(loop.number) == comp.polarity[0]:
                                        equation += "+" + str(comp.value) + " * (i" + str(
                                            loop1[0]) + "-i" + str(loop2[0]) + ") * " + loop1[1].name
                                else:
                                        equation += "-" + str(comp.value) + " * (i" + str(
                                            loop1[0]) + "-i" + str(loop2[0]) + ") * " + loop1[1].name
                            else:
                                if str(loop.number) == comp.polarity[0]:
                                        equation += "-" + str(comp.value) + " * (i" + str(
                                            loop1[0]) + "-i" + str(loop2[0]) + ") * " + loop1[1].name
                                else:
                                        equation += "+" + str(comp.value) + " * (i" + str(
                                            loop1[0]) + "-i" + str(loop2[0]) + ") * " + loop1[1].name
                        else:
                            if str(loop.number) == comp.polarity[0]:
                                equation += " - " + comp.value + " * "  + my_dependency[0][1].name + "*(i" + str(
                                    my_dependency[1][0]) + "-" + "i" + str(
                                    my_dependency[0][0]) + ")"
                            else:
                                equation += " + " + comp.value + " * " + my_dependency[0][1].name + "*(i" + str(my_dependency[1][0]) + "-" + "i" + str(
                                    my_dependency[0][0]) + ")"

            if isinstance(comp, Resistor):

                my_set = neighboring_components(comp, loop, loops_arrays1)
                if len(my_set) == 0:  # Resistor is not present in any other loop
                        equation += " + i" + str(loop.number) + "*" + str(comp.name)
                else:
                    for my in my_set:  # Resistor is present in other loops
                        equation += " + (i" + str(loop.number) + "-i" + str(my[0]) + ")" + "*" + str(my[1].name)
        equations.append(equation)
    return equations
def write_equations_with_superloops(loops_arrays, loops_arrays1):

    equation = ""
    equation2 = ""
    equations = []
    for loop in loops_arrays:
        if loop in explored_superloops:
            break
        for comp in loop.components:
            if isinstance(comp, CurrentSource) and comp.dependency == "Independent":
                shared_current_sources = neighboring_currents(comp, loop, loops_arrays1)

                if len(shared_current_sources) == 0:  #Current Source is not shared
                    if comp.polarity[1] == "+":
                        if str(loop.number) == comp.polarity[0]:
                            equation += "i" + str(loop.number) + " + " + str(comp.value)
                        else:
                            equation += "i" + str(loop.number) + " - " + str(comp.value)
                    else:
                        if str(loop.number) == comp.polarity[0]:
                            equation += "i" + str(loop.number) + " - " + str(comp.value)
                        else:
                            equation += "i" + str(loop.number) + " + " + str(comp.value)

                elif len(shared_current_sources) == 1:

                    count = sum(1 for current_source in shared_current_sources[0].components if
                                isinstance(current_source, CurrentSource))

                    if count == 1:
                        kcl = shared_current_sources[0]
                        loop_combination = [loop, kcl]
                        write_kvl = write_equations_with_no_superloops(loop_combination, loops_arrays1)


                        explored_superloops.add(loop)
                        explored_superloops.add(kcl)
                        equations.append(write_kvl)

                        if comp.polarity[1] == "+":
                            if str(loop.number) == comp.polarity[0]:
                                equation +=  str(comp.value) + " = ""i" + str(kcl.number) + " - " "i" + str(loop.number)
                            else:
                                equation +=  str(comp.value) + " = ""i" + str(loop.number) + " - " "i" + str(kcl.number)
                        else:
                            if str(loop.number) == comp.polarity[0]:

                                equation += str(comp.value) + " = ""i" + str(loop.number) + " - " "i" + str(kcl.number)
                            else:
                                equation +=  str(comp.value) + " = ""i" + str(kcl.number) + " - " "i" + str(kcl.number)
                    else:
                        kcl = shared_current_sources[0]
                        X_list = [comp for comp in kcl.components if isinstance(comp, CurrentSource)]
                        filtered_X_list = [X for X in X_list if X != comp]
                        X_length = neighboring_currents(filtered_X_list[0], kcl, loops_arrays1)[0]

                        if len(X_list) == 0:

                            if comp.polarity[1] == "+":
                                if str(loop.number) == comp.polarity[0]:
                                    equation += str(comp.value) + " = ""i" + str(kcl.number) + " - " "i" + str(
                                        loop.number)
                                else:
                                    equation += str(comp.value) + " = ""i" + str(loop.number) + " - " "i" + str(
                                        kcl.number)
                            else:
                                if str(loop.number) == comp.polarity[0]:
                                    equation += str(comp.value) + " = ""i" + str(loop.number) + " - " "i" + str(
                                       kcl.number)
                                else:
                                    equation += str(comp.value) + " = ""i" + str(kcl.number) + " - " "i" + str(
                                        kcl.number)

                        else:
                            loops = [loop, kcl, X_length]
                            write_kvl = write_equations_with_no_superloops(loops, loops_arrays1)

                            cohesive_string = ''.join(write_kvl)

                            equations.append(cohesive_string)

                            for l in loops:
                                explored_superloops.add(l)

                            # Current Balances
                            # Equation 1
                            if comp.polarity[1] == "+":
                                if str(loop.number) == comp.polarity[0]:  ## On the left side of the loop
                                    equation += str(comp.value) + " = ""i" + str(kcl.number) + " - " "i" + str(
                                        loop.number)
                                else:
                                    equation += str(comp.value) + " = ""i" + str(loop.number) + " - " "i" + str(
                                        kcl.number)
                            else:
                                if str(loop.number) == comp.polarity[0]:
                                    equation += str(comp.value) + " = ""i" + str(loop.number) + " - " "i" + str(
                                       kcl.number)
                                else:
                                    equation += str(comp.value) + " = ""i" + str(kcl.number) + " - " "i" + str(
                                        kcl.number)

                            # Equation 2
                            if comp.polarity[1] == "+":
                                if str(loop.number) == comp.polarity[0]:
                                    equation2 += str(filtered_X_list[0].value) + " = ""i" + str(kcl.number) + " - " "i" + str(
                                        X_length.number)
                                else:
                                    equation2 += str(filtered_X_list[0].value) + " = ""i" + str(kcl.number) + " + " "i" + str(
                                        X_length.number)
                            else:
                                if str(loop.number) == comp.polarity[0]:
                                    equation2 += str(filtered_X_list[0].value) + " = ""i" + str(kcl.number) + " + " "i" + str(
                                        X_length.number)
                                else:
                                    equation2+= str(filtered_X_list[0].value) + " = ""i" + str(kcl.number) + " - " "i" + str(
                                        X_length.number)
                            equations.append(equation2)

        equations.append(equation)
        flat_list = [item for sublist in equations for item in (sublist if isinstance(sublist, list) else [sublist])]
        if len(equations) == 0:
            pass
        else:
            return flat_list


def neighboring_components(target_component, current_loop,
                           all_loops):  # Takes a target component, and returns (loop number, object), where loop number is where the target component is found in
    shared = set()
    for loop in all_loops:
        if loop != current_loop:
            if target_component in loop.components:
                shared.add((loop.number, target_component))
    return shared


def neighboring_currents(target_component, current_loop,
                         all_loops):  # Takes a target component, and returns [loop object, component], where loop object is where the target component is found in
    shared = []
    for loop in all_loops:
        if loop != current_loop:
            if target_component in loop.components:
                shared.append(loop)
    return shared


def component_lookup(target_component,
                     all_loops): # Takes a target component, and returns the list of loops it is found in
    shared = []
    for loop in all_loops:
        for components in loop.components:
            if isinstance(components, Resistor):
                if str(target_component) == components.name[1]:
                    shared.append((loop.number, components))
    return shared
def convert_dependent_current_sources(comp, loops_arrays): ## Takes a current source as an input, and the total loops in the circuit
    my_dependency = component_lookup(comp.dependency[1], loops_arrays)


    if len(my_dependency) == 1:

        x = (my_dependency)[0]
        if comp.dependency.startswith("V"):
            dependency = "i" + str(x[0]) + "*" + str(x[1].name)

        else:

            dependency = "i" + str(x[0])
    else:
        loop1, loop2 = my_dependency

        if comp.dependency.startswith("V"):  # Voltage Source that depends on the voltage drop across a resistor

            dependency = "(i" + str(loop1[0]) + "-i" + str(loop2[0]) + ")" + "*" + str(loop1[1].value)

        else:
            dependency = "i(" + str(loop1[0]) + " - " + str(loop2[1]) + ")"
    comp.value = str(dependency) + " * " + str(comp.value)
    comp.dependency = "Independent"



def process_circuit_data(loops_arrays):
    for loop in loops_arrays:
        for comp in loop.components:
            if isinstance(comp, CurrentSource) and comp.dependency != "Independent":
                convert_dependent_current_sources(comp, loops_arrays)
    superloop = []
    non_superloop = []

    # Separate loops into superloops and non-superloops
    for loop in loops_arrays:
        if all(not isinstance(comp, CurrentSource) for comp in loop.components):
            non_superloop.append(loop)
        else:
            superloop.append(loop)

    equations = []

    # Write equations for non-superloops and superloops
    equations.extend((write_equations_with_no_superloops(non_superloop, loops_arrays)))
    for loop in superloop:
        equation = write_equations_with_superloops([loop], loops_arrays)
        if equation is not None:
            equations.extend(equation)

    return equations
