class Loop:
    def __init__(self, number: int, components: set):
        self.number = number
        self.components = components

    def __repr__(self):
        return f"Loop({self.number}, {self.components})"

    def add_component(self, component):
        """Adds a component to the loop's components list."""
        self.components.add(component)

    def get_components(self):
        """Returns the list of components in the loop."""
        return self.components



class Resistor:
    def __init__(self, name: str, value: float):
        self.name = name
        self.value = value


    def __repr__(self):
        return f"Resistor('{self.name}', {self.value}Ω,"

    def get_info(self):
        """Returns a dictionary with resistor information."""
        return {
            "name": self.name,
            "value": self.value,

        }

class VoltageSource:
    def __init__(self, name: str, value: str, polarity: str, dependency: str):
        self.name = name
        self.value = value
        self.polarity = polarity
        self.dependency = dependency

    def __repr__(self):
        return f"VoltageSource('{self.name}', {self.value}V, '{self.polarity}', '{self.dependency}')"

    def get_info(self):
        """Returns a dictionary with voltage source information."""
        return {
            "name": self.name,
            "value": self.value,
            "polarity": self.polarity,
            "dependency": self.dependency
        }

class CurrentSource:
    def __init__(self, name: str, value: str, polarity: str, dependency: str):
        self.name = name
        self.value = value
        self.polarity = polarity
        self.dependency = dependency

    def __repr__(self):
        return f"CurrentSource('{self.name}', {self.value}A, '{self.dependency}')"

    def get_info(self):
        """Returns a dictionary with current source information."""
        return {
            "name": self.name,
            "value": self.value,
            "dependency": self.dependency
        }
