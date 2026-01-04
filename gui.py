import tkinter as tk
from tkinter import messagebox
import io
import sys



class CircuitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mesh Analysis Solver")

        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        self.input_frame = tk.Frame(root)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.preview_frame = tk.Frame(root)
        self.preview_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(self.preview_frame, text="System Terminal (Live File & Results):", font=("Arial", 11, "bold")).pack(
            pady=(0, 5))

        self.preview_box = tk.Text(
            self.preview_frame, width=75, height=42, state='disabled',
            bg="#121212", fg="#32CD32", font=("Consolas", 11),
            padx=15, pady=15, borderwidth=0
        )
        self.preview_box.pack(fill="both", expand=True)

        self.data = {}
        self.create_input_section("Voltage Source", ["Name", "Value", "Polarity", "Dependency"], 0)
        self.create_input_section("Resistor", ["Name", "Value"], 1)
        self.create_input_section("Current Source", ["Name", "Value", "Polarity", "Dependency"], 2)
        self.create_input_section("Loop", ["Number", "Components (Space Separated)"], 3)

        btn_frame = tk.Frame(self.input_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=30)

        self.solve_button = tk.Button(btn_frame, text="Solve Circuit", command=self.run_solver, width=20, padx=10,
                                      pady=10)
        self.solve_button.pack(side="left", padx=10)

    def create_input_section(self, title, fields, row):
        frame = tk.LabelFrame(self.input_frame, text=title, font=("Arial", 9, "bold"))
        frame.grid(row=row, column=0, columnspan=4, pady=8, padx=5, sticky="w")

        # Keep track of the frame so we can add/remove widgets from it
        self.data[title] = {"fields": fields, "entries": [], "frame": frame}

        for col, field in enumerate(fields):
            tk.Label(frame, text=field).grid(row=0, column=col, padx=5)

        tk.Button(frame, text="+", command=lambda: self.add_entry(title), width=3, fg="green").grid(row=0,
                                                                                                    column=len(fields),
                                                                                                    padx=5)
        self.add_entry(title)

    def add_entry(self, title):
        """Generates a new row for component attributes with a delete button."""
        section = self.data[title]
        frame = section["frame"]

        grid_row = len(section["entries"]) + 1

        row_entries = []
        for col in range(len(section["fields"])):
            entry = tk.Entry(frame, width=12)
            entry.grid(row=grid_row, column=col, padx=5, pady=2)
            entry.bind("<KeyRelease>", lambda event: self.update_preview())
            row_entries.append(entry)

        # Add Delete Button for this row
        del_btn = tk.Button(frame, text="-", width=3, fg="red",
                            command=lambda: self.remove_entry(title, row_data))
        del_btn.grid(row=grid_row, column=len(section["fields"]), padx=5)

        # Store entries and the button as a dictionary so we can delete them easily
        row_data = {"widgets": row_entries, "button": del_btn}
        section["entries"].append(row_data)

        self.update_preview()

    def remove_entry(self, title, row_data):
        """Removes the widgets from the UI and the data list."""
        if len(self.data[title]["entries"]) <= 1:
            messagebox.showwarning("Warning", "At least one row is required.")
            return

        # 1. Destroy the Entry widgets and the Button widget
        for widget in row_data["widgets"]:
            widget.destroy()
        row_data["button"].destroy()

        # 2. Remove the row dictionary from the list
        self.data[title]["entries"].remove(row_data)

        # 3. Refresh preview
        self.update_preview()

    def generate_text_content(self):
        lines = []
        for section_name, content in self.data.items():
            section_added = False
            for row_data in content["entries"]:
                # Access the 'widgets' list inside our row dictionary
                values = [entry.get().strip() for entry in row_data["widgets"]]
                if values and values[0]:
                    if section_name in ["Loop", "Resistor"]:
                        lines.append(f"{section_name}: {values[0]}, {values[1]}")
                    else:
                        lines.append(f"{section_name}: {', '.join(values)}")
                    section_added = True
            if section_added: lines.append("")
        return "\n".join(lines).strip()


    def update_preview(self, additional_text=""):
        self.preview_box.config(state='normal')
        self.preview_box.delete(1.0, tk.END)
        self.preview_box.insert(tk.END, "--- CURRENT CIRCUIT FILE ---\n")
        self.preview_box.insert(tk.END, self.generate_text_content())

        if additional_text:
            self.preview_box.insert(tk.END, "\n\n" + "=" * 60 + "\n")
            self.preview_box.insert(tk.END, "SOLVER COMPUTATION RESULTS:\n")
            self.preview_box.insert(tk.END, "=" * 60 + "\n")
            self.preview_box.insert(tk.END, additional_text)
            self.preview_box.see(tk.END)

        self.preview_box.config(state='disabled')

    def save_to_file(self):
        content = self.generate_text_content()
        try:
            with open("circuit.txt", "w") as file:
                file.write(content)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"File save failed: {e}")
            return False

    def run_solver(self):
        if self.save_to_file():
            output_capture = io.StringIO()
            sys.stdout = output_capture
            try:
                import main
                main.run_process()
                sys.stdout = sys.__stdout__
                results = output_capture.getvalue()
                if not results.strip():
                    results = "Computation complete. No text results returned."
                self.update_preview(results)
            except Exception as e:
                sys.stdout = sys.__stdout__
                messagebox.showerror("Solver Error", f"The engine encountered an error: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CircuitApp(root)
    root.mainloop()
