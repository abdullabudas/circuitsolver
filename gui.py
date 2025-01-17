import tkinter as tk
from tkinter import messagebox


class CircuitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Circuit Parameters")

        # Input fields for components
        self.data = {}
        self.create_input_section("Voltage Source", ["Name", "Value", "Polarity", "Type"], 0)
        self.create_input_section("Resistor", ["Name", "Value"], 1)
        self.create_input_section("Current Source", ["Name", "Value", "Polarity", "Type"], 2)
        self.create_input_section("Loop", ["Loop Number", "Components"], 3)

        # Save button
        save_button = tk.Button(root, text="Save to File", command=self.save_to_file)
        save_button.grid(row=4, column=0, pady=10)

        # Generate Circuit button
        generate_button = tk.Button(root, text="Generate Circuit")
        generate_button.grid(row=4, column=1, pady=10)

    def create_input_section(self, title, fields, row):
        frame = tk.LabelFrame(self.root, text=title)
        frame.grid(row=row, column=0, columnspan=4, pady=5, sticky="w")

        self.data[title] = {"fields": fields, "entries": []}

        # Create header labels
        for col, field in enumerate(fields):
            tk.Label(frame, text=field).grid(row=0, column=col, padx=5)

        # Add button to add rows dynamically
        add_button = tk.Button(frame, text="Add", command=lambda: self.add_entry(frame, title))
        add_button.grid(row=0, column=len(fields), padx=5)

        # Add initial entry row
        self.add_entry(frame, title)

    def add_entry(self, frame, title):
        row = len(self.data[title]["entries"]) + 1
        entries = []

        for col in range(len(self.data[title]["fields"])):
            entry = tk.Entry(frame)
            entry.grid(row=row, column=col, padx=5)
            entries.append(entry)

        self.data[title]["entries"].append(entries)

    def save_to_file(self):
        filename = "circuit.txt"

        try:
            with open(filename, "w") as file:
                for section, content in self.data.items():
                    for entries in content["entries"]:
                        values = [entry.get().strip() for entry in entries]
                        if any(values):
                            if section == "Loop":
                                # For loops, format as: Loop: 1, Ra, Rb, Rc
                                file.write(f"{section}: {values[0]}, {', '.join(values[1:])}\n")
                            else:
                                # For other components (Voltage Source, Resistor, Current Source)
                                file.write(f"{section}: {', '.join(values)}\n")

            messagebox.showinfo("Success", f"Data saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CircuitApp(root)
    root.mainloop()
