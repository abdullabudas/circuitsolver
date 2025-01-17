from loopanalysis import Loop
from loopanalysis import Resistor
from loopanalysis import VoltageSource
from loopanalysis import CurrentSource
from copypython import process_circuit_data
import sympy as sp

def read_text(file_path):
    voltage_sources = []
    resistors = []
    loops = []
    current_sources = []

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()

            if line.startswith("Voltage Source:"):
                voltage_sourceinfo, voltage, polarity, dependency = line.split(", ")
                name = voltage_sourceinfo.split(": ")[1]
                voltage_source = VoltageSource(name=name, value=voltage, polarity=polarity, dependency=dependency)
                voltage_sources.append(voltage_source)

            elif line.startswith("Resistor:"):
                resistor_info, resistance, = line.split(", ")
                name = resistor_info.split(": ")[1]
                value = float(resistance)
                resistor = Resistor(name=name, value=value)
                resistors.append(resistor)

            elif line.startswith("Current Source:"):
                voltage_sourceinfo, voltage, polarity, dependency = line.split(", ")
                name = voltage_sourceinfo.split(": ")[1]
                current_source = CurrentSource(name=name, value=voltage, polarity=polarity, dependency=dependency)
                current_sources.append(current_source)

            elif line.startswith("Loop:"):
                loop_info, components = line.split(", ", 1)
                loop_number = int(loop_info.split(": ")[1])
                component_names = components.split(" ")
                component_array = set()
                component_array.update(resistor for resistor in resistors if resistor.name in component_names)
                component_array.update(
                    voltage_source for voltage_source in voltage_sources if voltage_source.name in component_names)
                component_array.update(
                    current_source for current_source in current_sources if current_source.name in component_names)
                loop = Loop(loop_number, component_array)
                loops.append(loop)

    return [loops, voltage_sources, resistors]


def main():
    file_path = "circuit.txt"
    x = read_text(file_path)
    equations_list = process_circuit_data(x[0])
    y = parse_equations(equations_list, x[0], x[1], x[2])
    print("System of Equations: ")
    print(y)
    print("Solutions: ")
    solutions = solve_equations(y)



def parse_equations(equation_list, loops, resistors, voltage_sources):
    currents = [sp.symbols(f'i{i}') for i in range(1, len(loops) + 1)]
    resistances = {resistor.name: resistor.value for resistor in resistors}
    voltages = {voltage_source.name: voltage_source.value for voltage_source in voltage_sources}
    sympy_equations = []
    for equation in equation_list:
        equation = equation.lstrip('+').replace(' ', '')
        for voltage in voltage_sources:
            equation = equation.replace(voltage.name, str(voltage.value))
        for resistor in resistances:
            equation = equation.replace(resistor, str(resistances[resistor]))
        if '=' not in equation:
            equation += '=0'
        lhs, rhs = equation.split('=')
        try:
            lhs_expr = sp.sympify(lhs, locals={**resistances, **voltages, **dict(zip([f'i{i}' for i in range(1, len(loops) + 1)], currents))})
            rhs_expr = sp.sympify(rhs, locals={**resistances, **voltages, **dict(zip([f'i{i}' for i in range(1, len(loops) + 1)], currents))})
            sympy_equation = sp.Eq(lhs_expr, rhs_expr)
            sympy_equations.append(sympy_equation)
        except Exception as e:
            print(f"Error parsing equation: {equation}")
            print(f"Error details: {e}")
            continue
    return sympy_equations

def solve_equations(sympy_equations):
    solutions = sp.solve(sympy_equations)
    if len(solutions) == 0:
        print("No solutions")
        return None
    units = "mA"
    i = 1
    for variable, value in solutions.items():
        print(f"i{i} = {round(value, 3)} {units}")
        i += 1


if __name__ == "__main__":
    main()
