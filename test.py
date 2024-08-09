import tkinter as tk

def create_grid(data):
    """Creates a grid of text boxes based on the provided data.

    Args:
        data: A list of lists containing initial values for the text boxes.
    """

    root = tk.Tk()
    root.geometry("400x300")  # Adjust window size as needed

    textboxes = []
    for row, values in enumerate(data):
        row_boxes = []
        for col, value in enumerate(values):
            entry = tk.Entry(root)
            entry.insert(0, value)  # Pre-fill the text box
            entry.grid(row=row, column=col, padx=5, pady=5)
            row_boxes.append(entry)
        textboxes.append(row_boxes)

    def save_data():
        saved_data = []
        for row in textboxes:
            row_values = [box.get() for box in row]
            saved_data.append(row_values)
        print(saved_data)  # Replace with your desired saving logic

    save_button = tk.Button(root, text="Save Data", command=save_data)
    save_button.grid(row=len(data), column=0, columnspan=len(data[0]), pady=10)

    root.mainloop()

# Example usage:
data = [
    ["value1", "value2", "value3"],
    ["value4", "value5", "value6"],
    ["value7", "value8", "value9"]
]

create_grid(data)
