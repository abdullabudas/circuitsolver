# circuitsolver
circuitsolver is a Python-based tool designed to solve DC circuits using the loop analysis method. It can handle both dependent and independent sources in a circuit.

Circuit Conventions:
Positive loop current: Clockwise  
Resistance: In kilo ohms (kΩ)  
Current: In milliampere (mA)  
Conductance: In millisiemens (mS)  
Voltage: In volts (V)  
Sample Usage:

Circuit

<img width="843" alt="Screen Shot 2025-01-18 at 10 51 09 PM" src="https://github.com/user-attachments/assets/8dd1b624-91b0-4006-90ec-70785f0c991b" />

"circuit.txt" file:  


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




