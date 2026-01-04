# CircuitSolver

CircuitSolver is a Python-based tool designed to solve DC circuits using the loop analysis method. This application was built to efficiently verify complex circuit configurations with unique parameters, supporting both independent and dependent sources.

---

## How to Use

1. **Clone the Repository**: Download the project files to your local machine.
2. **Launch the Interface**: Run the `gui.py` file using Python.
3. **Input Data**: Use the GUI to fill out circuit components following the rules and conventions defined below.
4. **Solve**: The application processes the input and displays the results in the system terminal preview.

---

## Circuit Conventions

To ensure accurate computation, the solver adheres to the following units and directional standards:

* **Loop Current**: All loops are assumed to flow in a Clockwise direction.
* **Resistance**: Measured in kilo-ohms (kΩ).
* **Current**: Measured in milliamperes (mA).
* **Conductance**: Measured in millisiemens (mS).
* **Voltage**: Measured in volts (V).

---

## Component Parameter Guide

When entering data into the GUI, the Value and Dependency fields are interpreted as follows:

* **Resistors**: Enter the resistance in kΩ.
* **Independent Sources**: Enter the constant magnitude. The dependency field must be set to Independent.
* **Dependent Sources**: Enter the **Gain** coefficient (e.g., if $V = 0.75 V_u$, enter `0.75`). 
* **Dependency Logic**: The dependency field must match the name of the controlling component exactly (e.g., the name of the specific Resistor it depends on).
---

## Polarity and Connection Rules

The solver uses a coordinate system based on a **Left-to-Right** and **Up-to-Down** priority. Components are defined by their placement between loops using the syntax `LoopA[Sign]LoopB`.

### Directional Polarity Logic

The sign (+ or -) is determined by how the **primary loop** (the loop to the left of a vertical branch or the loop above a horizontal branch) interacts with the component:

* **Current Sources**: 
    * **Plus (+)**: Assigned if the clockwise motion of the primary loop flows against the direction of the current source arrow.
* **Voltage Sources**: 
    * **Plus (+)**: Assigned if the clockwise motion of the primary loop enters the negative terminal (moving from - to +).
* **Boundary Components**: Performed against loop 0 (e.g., `0+4`). A `+` is used if the loop current enters a negative terminal or opposes a source arrow.

### Sample Mapping Examples Based on Example Circuit

The following examples demonstrate how these rules are applied to the specific circuit diagram shown in the next section:

* **VA, 2, 2-5**: Source VA is shared between Loop 2 and Loop 5. Since the clockwise current of Loop 2 (above) flows in the same direction as Loop 5 (below) through that branch, they are coupled with a `-`.
* **IB, 8, 2+3**: Source IB is between Loop 2 and Loop 3. The clockwise current of Loop 2 (left) flows downward, opposing the upward arrow of the source, resulting in a `+`.

---

## Sample Usage

### Circuit Diagram
<img width="843" alt="Screen Shot 2025-01-18 at 10 51 09 PM" src="https://github.com/user-attachments/assets/8dd1b624-91b0-4006-90ec-70785f0c991b" />

### circuit.txt Configuration
```text
Voltage Source: VA, 2, 2-5, Independent  
Voltage Source: VC, 7, 1+2, Independent  
Voltage Source: V, 0.75, 0+4, Vu  

Resistor: Rz, 3.6  
Resistor: Rv, 1.2  
Resistor: Rx, 3  
Resistor: Ry, 1.8  
Resistor: Ru, 1.5  
Resistor: Rw, 4.7     

Current Source: IB, 8, 2+3, Independent  
Current Source: IC, 2, 4+5, Vw    

Loop: 1, Rz VC  
Loop: 2, VC Ry VA IB  
Loop: 3, IB Rx Rv  
Loop: 4, V IC Rz  
Loop: 5, IC Rw VA  
Loop: 6, Rw Rv Ru

```
## Application Interface and Results
The image below demonstrates the GUI after processing the example circuit, showcasing the Live Terminal output and the calculated loop currents.
<img width="1456" height="913" alt="Screen Shot 2026-01-04 at 11 23 52 PM" src="https://github.com/user-attachments/assets/dc7728f8-ca1b-4c1c-b127-66381a4ff77c" />


## Limitations and Constraints
* Current Source Topology:
Any branch containing a current source must be a shared boundary between exactly two loops.

* Shared Branch Failures:
The solver cannot currently resolve configurations where two or more current sources are shared between three or more loops.
