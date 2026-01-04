from objects import VoltageSource, Resistor, Loop, CurrentSource

def write_equations_with_no_superloops(target_loops, all_loops):
    equations = []

    for loop in target_loops:

        equation = ""
        for comp in loop.components:

            # --- Handling Voltage Sources ---
            if isinstance(comp, VoltageSource):

                sign_val = get_polarity_sign(comp, loop.number)
                sign_str = " + " if sign_val > 0 else " - "

                if comp.dependency == "Independent":

                    # Simple independent source (e.g., 10V)
                    equation += f"{sign_str}{comp.name}"

                else:
                    # Dependent Source: Use helper function to get the algebraic expression

                    # This checks and handles whether it's voltage or current controlled and the (i1 - i2) math
                    dep_expression = convert_dependent_sources(comp, all_loops)


                    if dep_expression:
                        # We use the polarity sign to decide if we add or subtract the whole expression
                        equation += f"{sign_str}({dep_expression})"

            # --- Handling Resistors ---
            elif isinstance(comp, Resistor):
                # Standard mesh term: Ri_1 or R(i_1 - i_2)
                equation += " + " + resistor_term(loop, comp, all_loops)

        # Cleanup: Remove leading " + " and add " = 0"
        equation = equation.strip().lstrip("+").strip()
        equations.append(f"{equation} = 0")

    return equations


def write_equations_with_superloops(target_loops, all_loops, explored_superloops):
    equations = []

    for loop in target_loops:
        if loop in explored_superloops:
            continue

        for comp in loop.components:
            if isinstance(comp, CurrentSource):
                # 1. Handle Dependency (Turn VC/CC into mesh current expression)
                source_val = comp.value
                if comp.dependency != "Independent":
                    source_val = convert_dependent_sources(comp, all_loops)

                # 2. Check if this Current Source is shared with another loop
                # We exclude the current loop from the search to find the neighbor
                shared_info = find_shared_loops(comp.name, all_loops, current_loop=loop)

                if not shared_info:  # Case: Current source is NOT shared (Outer boundary)
                    # Use polarity to see if i_loop matches source direction
                    # If get_polarity_sign is -1, loop enters '+', so it's opposite the source arrow
                    sign = "" if get_polarity_sign(comp, loop.number) > 0 else "-"
                    equations.append(f"i{loop.number} = {sign}" + source_val)
                    explored_superloops.add(loop)

                else:  # Case: Current source shared between two loops
                    neighbor_loop = shared_info[0][0]  # Extract the Loop object

                    # A. Constraint Equation (KCL)
                    # If loop enters negative terminal, mesh current aligns with source arrow
                    if get_polarity_sign(comp, loop.number) > 0:
                        # i_this - i_neighbor = source_val
                        constraint = f"i{loop.number} - i{neighbor_loop.number} = {source_val}"
                    else:
                        # i_neighbor - i_this = source_val
                        constraint = f"i{neighbor_loop.number} - i{loop.number} = {source_val}"

                    equations.append(constraint)

                    # B. Supermesh KVL Equation
                    # We combine the two loops into one KVL equation
                    # We pass the pair to the no_superloops function to get their KVL terms
                    kvl_parts = write_equations_with_no_superloops([loop, neighbor_loop], all_loops)

                    # Clean up: join the two loop equations and remove the middle '= 0'
                    combined_kvl = " + ".join([eq.split('=')[0].strip() for eq in kvl_parts])
                    equations.append(f"{combined_kvl} = 0")

                    # Mark both loops as processed
                    explored_superloops.add(loop)
                    explored_superloops.add(neighbor_loop)

    return [e for e in equations if e]



def find_shared_loops(component_name, all_loops, current_loop=None):
    """
    Returns a list of (loop, component) tuples where the component is found.
    """
    shared = []
    for loop in all_loops:
        if loop == current_loop:
            continue
        for comp in loop.components:
            if hasattr(comp, "name") and comp.name == component_name:
                shared.append((loop, comp))
    return shared


#Convert dependent current sources ===
def convert_dependent_sources(component, all_loops):
    """
    Converts dependent sources (Voltage or Current controlled) into
    independent algebraic forms based on mesh currents.
    """

    if component.dependency == "Independent":
        return None

    # 1. Identify the control type and the target resistor
    # component.dependency might be "Vu" or "Iu"
    control_type = component.dependency[0] # 'V' or 'I'
    dependency_name = "R" + component.dependency[1:] # e.g., "Vu" -> "Ru"

    # 2. Find all loops containing the controlling resistor
    shared_loops = find_shared_loops(dependency_name, all_loops)


    # 3. Build the current expression (i_a - i_b)
    current_expr = "("
    for idx, (loop, _) in enumerate(shared_loops):
        current_expr += f"i{loop.number}" if idx == 0 else f"-i{loop.number}"
    current_expr += ")"

    # 4. Is it Voltage-Controlled or Current-Controlled?
    if control_type == "V":
        # Voltage = Current * Resistance (Ohm's Law)
        resistor_value = shared_loops[0][1].value
        dependency_expr = f"{current_expr} * {resistor_value}"
    else:
        # Current = Just the current expression
        dependency_expr = current_expr

    # 5. Apply Gain (the multiplier, e.g., the "0.75" from "Voltage Source: V, 0.75, 0+4, Vu")
    final_value = f"({dependency_expr}) * {component.value}"

    # 6. Finalize component state
    component.value = final_value
    component.dependency = "Independent"

    return final_value

def get_polarity_sign(comp, loop_number):
    """
    Returns 1 if the component's polarity aligns with the loop direction,
    and -1 if it is opposite.
    """
    if comp.polarity[1] == "+":
        if str(loop_number) == comp.polarity[0]:
            return -1
        else:
            return 1
    else:
        if str(loop_number) == comp.polarity[0]:
            return 1
        else:
            return -1

def resistor_term(loop, resistor, all_loops):
    """
    Build the contribution of a resistor to a loop equation.

    Parameters:
        loop_number   : int, the loop number
        resistor      : Resistor object
        all_loops : list of all loop objects from the circuit

    Returns:
        str: equation fragment for this resistor
    """
    shared_loops = find_shared_loops(resistor.name, all_loops, loop)
    if not shared_loops:
        # Resistor only in this loop
        return f"i{loop.number} * {resistor.name}"

    # Resistor shared with other loops
    terms = [f"i{loop.number}"]
    for shared_loop, _ in shared_loops:
        # Subtract current in neighboring loops
        terms.append(f"- i{shared_loop.number}")

    # Multiply by resistor value
    return "(" + " ".join(terms) + f") * {resistor.name}"

def process_circuit_data(all_loops):
    equations = []
    explored_superloops = set()

    for loop in all_loops:
        if loop in explored_superloops:
            continue

        has_current_source = any(isinstance(comp, CurrentSource) for comp in loop.components)

        if not has_current_source:
            # Pass single loop as target_loops
            eqs = write_equations_with_no_superloops([loop], all_loops)
            equations.extend(eqs)
        else:
            # Pass single loop as target_loops
            eqs = write_equations_with_superloops([loop], all_loops, explored_superloops)
            if eqs:
                equations.extend(eqs)

    return equations
