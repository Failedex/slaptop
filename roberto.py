import tkinter as tk
from slap import view_data, insert_data

root = tk.Tk()
root.title("Roberto")

title = tk.Label(root, text="Laptops", font=("Sans", 15))
title.pack()



# Create main frame
main_frame = tk.Frame(root)
main_frame.pack(fill = "both", expand=1)  

# create canvas
my_canvas = tk.Canvas(main_frame)
my_canvas.pack(side = "left", fill="both", expand=1)

# add scrollbar to canvas
my_scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=my_canvas.yview)
my_scrollbar.pack(side="right", fill="y")

# configure canvas
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# create another frame inside canvas
second_frame = tk.Frame(my_canvas)

# add new frame to window in canvas
my_canvas.create_window((0,0), window=second_frame, anchor="nw")

# add items into second frame


shits = view_data("rating > 3")
for shit in shits:
    item = tk.Label(second_frame, text=f"{shit[0]}")
    item.pack()

root.mainloop()