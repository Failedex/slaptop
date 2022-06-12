import tkinter as tk
from slap import view_data, insert_data, all_keys
import sqlite3

conn = sqlite3.connect("laptops.db")
cur = conn.cursor()

root = tk.Tk()
root.title("Roberto")

title = tk.Label(root, text="Laptops", font=("Sans", 15))
title.pack()

window_on = False

def filter_window():
    global window_on

    if window_on: return
    window_on = True

    t = tk.Toplevel(root)
    t.wm_title("laptop filters")

    def exit_filter():
        global window_on

        condition = ""
        for column, info in dropdowns.items():
            if info["foreign"]: 

                if column == "hdd": continue
                if column == "ssd":

                    cur.execute(f"""select id from disk_type where 
                        hdd {dropdowns['hdd']['operator'].get()} {dropdowns['hdd']['choice'].get()}
                        and sdd {info['operator'].get()} {info['choice'].get()};
                    """)

                    for valid_id in cur.fetchall():
                        pass

                choice = info["choice"].get()
                dictionary = info["dictionary"]
                
                if choice == "None": continue

                condition += f"{column}_id = {dictionary[choice]} and"
                
                continue
            
            if info["option"] == "search":
                entry = info["choice"].get()

                if entry == "": continue

                condition += f"{column} like '%{entry}%' and "
                
                continue
            
            if info["option"] == "searchint" or info["type"] == "searchfloat":
                entry = info["choice"].get()
                operator = info["operator"].get()

                condition += f"{column} {operator} {entry} and "
                
                continue
                    
            if info["option"] == "boolean":
                boo = info["choice"].get()

                if boo == 0: continue

                condition += f"{column} = {boo} and "

                continue
        
        condition = condition[:-3]
        print(condition)

        t.destroy()
        t.update()
        window_on = False
        


    ttitle = tk.Label(t, text="Filters", font = ("Sans, 15")).grid(row = 0, column = 0, columnspan=2)

    save = tk.Button(t, text="comfirm filter", command=exit_filter).grid(row = 0, column= 2)
    
    dropdowns = {
        "brand": {"foreign": True, "table": "brands", "items": "name", "option": "dropdown"}, 
        "model": {"foreign": False, "option":"search"},
        "processor": {"foreign": True, "special": True},
        "processor_generation": {"foreign": False, "option": "searchint"},
        "ram": {"foreign": False, "option": "searchint"},
        "ram_type": {"foreign": True, "table": "ram_type", "items": "type", "option": "dropdown"},
        "ssd": {"foreign": True, "special": True},
        "hdd": {"foreign": True, "special": True},
        "os": {"foreign": True, "table": "os", "items": "name", "option": "dropdown"},
        "os_bit": {"foreign": False, "option": "searchint"},
        "graphic_card_gb": {"foreign": False, "option": "searchint"},
        "weight": {"foreign": True, "table": "weight", "items": "type", "option": "dropdown"},
        "display_size": {"foreign": False, "option": "searchint"},
        "touchscreen": {"foreign": False, "option": "boolean"},
        "price": {"foreign": False, "option": "searchint"},
        "rating": {"foreign": False, "option": "searchfloat"},
    }

    for i , (column, info) in enumerate(dropdowns.items()):

        label = tk.Label(t, text=column).grid(row = i+1, column = 0)
        
        if info["foreign"] == True:

            # processor is a special kid. So is disk_type
            if column == "processor":
                bitches = False
                
                cur.execute(f"""
                    select processor.id, processor_brand.brand, processor.model from processor 
                    left join processor_brand
                    on processor.brand_id = processor_brand.id;
                """)

                options = {}

                for cpu in cur.fetchall():
                    options[f"{cpu[1]} {cpu[2]}"] = cpu[0]
            
            elif column == "ssd" or column == "hdd":
                
                options = [">", "<", "="]
                choice = tk.StringVar(t)
                choice.set("=")
                choice_select = tk.OptionMenu(t, choice, *options)
                choice_select.grid(row = i+1, column = 1)
                entry = tk.Entry(t).grid(row = i+1, column = 2)
                dropdowns[column][hardtype] = entry
                dropdowns[column]["operator"] = choice
                
                continue

            else:
            
                options = all_keys(cur, info["table"], info["items"])

            choice = tk.StringVar(t)
            choice.set("None")

            choice_select = tk.OptionMenu(t, choice, *options)
            choice_select.grid(row = i+1, column = 2)

            dropdowns[column]["choice"] = choice
            dropdowns[column]["dictionary"] = options

            continue

        if info["option"] == "search":
            entry = tk.Entry(t).grid(row = i+1, column=2)
            dropdowns[column]["choice"] = entry
        
        if info["option"] == "searchint" or info["option"] == "searchfloat":
            options = [">", "<", "="]
            choice = tk.StringVar(t)
            choice.set("=")
            choice_select = tk.OptionMenu(t, choice, *options)
            choice_select.grid(row = i+1, column = 1)
            entry = tk.Entry(t).grid(row = i+1, column = 2)

            dropdowns[column]["choice"] = entry
            dropdowns[column]["operator"] = choice
        
        if info["option"] == "boolean": 
            boo = tk.IntVar()
            checkbox = tk.Checkbutton(t, variable=boo).grid(row = i+1, column = 2)
            dropdowns[column]["choice"] = boo

        

    
filter_button = tk.Button(root, text="filters", command=filter_window, font = ("Sans, 10"))
filter_button.pack(side = "top", anchor="ne")

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


shits = view_data(cur, "rating > 3")
for shit in shits:
    item = tk.Label(second_frame, text=f"{shit[0]}")
    item.pack()

root.mainloop()