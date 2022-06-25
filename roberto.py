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

def noinjection(statement, statement_type):
            if statement_type == "string":
                if any(x in statement for x in ["\"", "\'", ";", "--"]):
                    return False
                
            if statement_type == "int":
                if not statement.isdigit(): 
                    return False
            
            if statement_type == "float":
                # very clever solution https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
                if not statement.replace(".", "", 1).isdigit():
                    return False
            
            return True

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


                    if dropdowns["hdd"]["choice"].get() == "" and info["choice"].get() == "":
                        disk_filter = "select id from disk_type;"
                    else:
                        disk_filter = "select id from disk_type where "
                        if not noinjection(dropdowns["hdd"]["choice"].get(), "int") or not noinjection(info["choice"].get(), "int"):
                            display_data(False, "numbers field only take in numbers")
                            t.destroy()
                            t.update()
                            window_on = False
                            return

                        if dropdowns["hdd"]["choice"].get() != "":
                            disk_filter += f"hdd {dropdowns['hdd']['operator'].get()} {dropdowns['hdd']['choice'].get()} and "
                        
                        if info["choice"].get() != "":
                            disk_filter += f"ssd {info['operator'].get()} {info['choice'].get()} and "
                        
                        disk_filter = disk_filter[:-4] + ";"

                    cur.execute(disk_filter)

                    disk_type_filter = "("

                    for valid_id in cur.fetchall():
                        disk_type_filter += f"laptops.disk_type_id = {valid_id[0]} or "
                    
                    condition += disk_type_filter[:-3] + ") and "
                    continue

                choice = info["choice"].get()
                dictionary = info["dictionary"]
                
                if choice == "None": continue

                condition += f"laptops.{column}_id = {dictionary[choice]} and "
                
                continue
            
            if info["option"] == "search":
                entry = info["choice"].get()
                if entry == "": continue
                if not noinjection(entry, "string"):
                    display_data(False, "suspicious string detected")
                    t.destroy()
                    t.update()
                    window_on = False
                    return

                condition += f"laptops.{column} like '%{entry}%' and "
                
                continue
            
            if info["option"] == "searchint" or info["option"] == "searchfloat":
                entry = info["choice"].get()

                if entry == "": continue
                if not noinjection(entry, "float"): 
                    display_data(False, "number field only takes in numbers")
                    t.destroy()
                    t.update()
                    window_on = False
                    return

                operator = info["operator"].get()

                condition += f"laptops.{column} {operator} {entry} and "
                
                continue
                    
            if info["option"] == "boolean":
                boo = info["choice"].get()

                if boo == 0: continue

                condition += f"laptops.{column} = {boo} and "

                continue
        
        condition = condition[:-4]
        print(condition)

        display_data(condition)

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
                
                options = [">=", "<=", "="]
                choice = tk.StringVar(t)
                choice.set("=")
                choice_select = tk.OptionMenu(t, choice, *options)
                choice_select.grid(row = i+1, column = 1)
                entry = tk.Entry(t)
                entry.grid(row = i+1, column = 2)
                dropdowns[column]["choice"] = entry
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
            entry = tk.Entry(t)
            entry.grid(row = i+1, column=2)
            dropdowns[column]["choice"] = entry
        
        if info["option"] == "searchint" or info["option"] == "searchfloat":
            options = [">=", "<=", "="]
            choice = tk.StringVar(t)
            choice.set("=")
            choice_select = tk.OptionMenu(t, choice, *options)
            choice_select.grid(row = i+1, column = 1)
            entry = tk.Entry(t)
            entry.grid(row = i+1, column = 2)

            dropdowns[column]["choice"] = entry
            dropdowns[column]["operator"] = choice
        
        if info["option"] == "boolean": 
            boo = tk.IntVar()
            checkbox = tk.Checkbutton(t, variable=boo).grid(row = i+1, column = 2)
            dropdowns[column]["choice"] = boo

def add_window():
    global window_on

    if window_on: return
    window_on = True

    t = tk.Toplevel(root)
    t.wm_title("laptop add")

    def add_laptop():
        global window_on

        for key, info in laptop_info.items():
            if info["type"] == "foreign":
                if info["entry"].get() == "None": 
                    display_data(False, "field not entered")
                    t.destroy()
                    t.update()
                    window_on = False
                    return

                info["entry"] = info["entry"].get()
                continue
            
            
            if info["entry"].get() == "":
                if "optional" in info.keys():
                    laptop_info[key]["entry"] = info["default"]
                    continue
                else:
                    display_data(False, "field not entered")
                    t.destroy()
                    t.update()
                    window_on = False
                    return

            if not noinjection(info["entry"].get(), info["type"]): 
                display_data(False, "suspicious characters detected")
                t.destroy()
                t.update()
                window_on = False
                return

            if info["type"] == "string":
                entry = info["entry"].get()
                laptop_info[key]["entry"] = entry[0].upper() + entry[1:]
                
            if info["type"] == "int":
                info["entry"] = int(info["entry"].get())

            if info["type"] == "float":
                info["entry"] = float(info["entry"].get())

            if info["type"] == "bool":
                info["entry"] = info["entry"].get()
 

        id = len(view_data(cur, "1 = 1"))+1

        print(id, laptop_info["brand"]["entry"], laptop_info["model"]["entry"], laptop_info["processor_brand"]["entry"], laptop_info["processor_name"]["entry"], laptop_info["processor_generation"]["entry"], laptop_info["ram"]["entry"], laptop_info["ram_type"]["entry"], laptop_info["ssd"]["entry"], laptop_info["hdd"]["entry"], laptop_info["os"]["entry"], laptop_info["os_bit"]["entry"], laptop_info["graphic_card_gb"]["entry"], laptop_info["weight"]["entry"], laptop_info["display_size"]["entry"], laptop_info["touchscreen"]["entry"], laptop_info["price"]["entry"], laptop_info["rating"]["entry"])

        insert_data(cur, id, laptop_info["brand"]["entry"], laptop_info["model"]["entry"], laptop_info["processor_brand"]["entry"], laptop_info["processor_name"]["entry"], laptop_info["processor_generation"]["entry"], laptop_info["ram"]["entry"], laptop_info["ram_type"]["entry"], laptop_info["ssd"]["entry"], laptop_info["hdd"]["entry"], laptop_info["os"]["entry"], laptop_info["os_bit"]["entry"], laptop_info["graphic_card_gb"]["entry"], laptop_info["weight"]["entry"], laptop_info["display_size"]["entry"], laptop_info["touchscreen"]["entry"], laptop_info["price"]["entry"], laptop_info["rating"]["entry"])
        conn.commit()
        t.destroy()
        t.update()
        window_on = False
        display_data(False, "laptop has been added")
        return
        

    tk.Label(t, text="Filters", font = ("Sans, 15")).grid(row = 0, column = 0, columnspan=2)

    add = tk.Button(t, text="add laptop", command = add_laptop).grid(row = 0, column= 2)

    laptop_info = dict(
        brand = {"type": "string"},
        model = {"type": "string"},
        processor_brand = {"type": "string"},
        processor_name = {"type": "string"},
        processor_generation = {"type": "int", "optional": True, "default": None, "unit": "th"},
        ram = {"type": "int", "unit": "GB"},
        ram_type = {"type": "foreign", "table": "ram_type", "items": "type"},
        ssd = {"type": "int", "optional": True, "default": 0, "unit": "GB"},
        hdd = {"type": "int", "optional": True, "default": 0, "unit": "GB"},
        os = {"type": "foreign", "table": "os", "items": "name"},
        os_bit = {"type": "int", "optional": True, "default": None, "unit": "bits"},
        graphic_card_gb = {"type": "int", "optional": True, "default": 0, "unit": "GB"},
        weight = {"type": "foreign", "table": "weight", "items": "type"},
        display_size = {"type": "int", "unit": "inches"},
        touchscreen = {"type": "bool"},
        price = {"type": "int", "optional": True, "default": None, "unit": "$"},
        rating = {"type": "float", "optional": True, "default": 0},
    )

    for i, (key, info) in enumerate(laptop_info.items()):
        heading = tk.Label(t, text = key).grid(row = i+1, column = 0)

        if info["type"] == "foreign":
            options = all_keys(cur, info["table"], info["items"])
            choice = tk.StringVar(t)
            choice.set("None")

            choice_select = tk.OptionMenu(t, choice, *options)
            choice_select.grid(row = i+1, column = 2)

            laptop_info[key]["entry"] = choice
            continue

        if info["type"] == "bool":
            boo = tk.IntVar()
            checkbox = tk.Checkbutton(t, variable=boo).grid(row = i+1, column = 2)
            laptop_info[key]["entry"] = boo
            continue

        if info["type"] == "int":
            tk.Label(t, text = info["unit"]).grid(row=i+1, column=3)

        entry = tk.Entry(t)
        entry.grid(row=i+1, column=2)
        laptop_info[key]["entry"] = entry


    
filter_button = tk.Button(root, text="filters", command=filter_window, font = ("Sans, 10"))
filter_button.pack(side = "top", anchor="ne")

add_button = tk.Button(root, text = "add", command=add_window, font = ("Sans, 10"))
add_button.pack(side = "top", anchor="ne")

# Create main frame
main_frame = tk.Frame(root, height = 100, width = 100)
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

def detail(id, btn_id):
    cur.execute(f"""
    select brands.name, laptops.model, laptops.processor_generation, processor.model, ram_type.type, laptops.ram, disk_type.ssd, disk_type.hdd, os.name, laptops.os_bit, laptops.graphic_card_gb, weight.type, laptops.display_size, laptops.touchscreen, laptops.price, laptops.rating
    from laptops left join brands on laptops.brand_id = brands.id
    left join processor on laptops.processor_id = processor.id
    left join ram_type on laptops.ram_type_id = ram_type.id
    left join disk_type on laptops.disk_type_id = disk_type.id
    left join os on laptops.os_id = os.id
    left join weight on laptops.weight_id = weight.id
    where laptops.id = {id}
    """)
    laptop = cur.fetchone()
    btn = second_frame.winfo_children()[btn_id]
    btn["text"] = f"""{laptop[0]} {laptop[1]} 
    ssd: {laptop[6]} hdd: {laptop[7]}
    ram: {laptop[5]}GB {laptop[4]} 
    {laptop[3]} {laptop[2]}th gen
    os: {laptop[8]} bit: {laptop[9]}
    graphics card: {laptop[10]}GB
    weight: {laptop[11]}
    display size: {laptop[12]}
    touchsceen: {"true" if laptop[13] == 1 else "false"}
    price: {laptop[14]} rating: {laptop[15]}"""

    my_canvas.update()


def display_data(condition = False, error = None):

    for widget in second_frame.winfo_children():
        widget.destroy()
    
    if error:
        tk.Label(second_frame, text = error, fg="red", font=("15")).pack(fill = "x")
    else:
        tk.Label(second_frame, text = "", fg="red", font=("15")).pack(fill = "x")


    if not condition:
        cur.execute(f"""
            select laptops.id, brands.name, laptops.model, laptops.processor_generation, processor.model, ram_type.type, laptops.ram, disk_type.ssd, disk_type.hdd, os.name, laptops.os_bit, laptops.graphic_card_gb, weight.type, laptops.display_size, laptops.touchscreen, laptops.price, laptops.rating
            from laptops 
            left join brands on laptops.brand_id = brands.id
            left join processor on laptops.processor_id = processor.id
            left join ram_type on laptops.ram_type_id = ram_type.id
            left join disk_type on laptops.disk_type_id = disk_type.id
            left join os on laptops.os_id = os.id
            left join weight on laptops.weight_id = weight.id
        """)
    else:
        cur.execute(f"""
        select laptops.id, brands.name, laptops.model, laptops.processor_generation, processor.model, ram_type.type, laptops.ram, disk_type.ssd, disk_type.hdd, os.name, laptops.os_bit, laptops.graphic_card_gb, weight.type, laptops.display_size, laptops.touchscreen, laptops.price, laptops.rating
        from laptops 
        left join brands on laptops.brand_id = brands.id
        left join processor on laptops.processor_id = processor.id
        left join ram_type on laptops.ram_type_id = ram_type.id
        left join disk_type on laptops.disk_type_id = disk_type.id
        left join os on laptops.os_id = os.id
        left join weight on laptops.weight_id = weight.id
        where {condition}
        """)
    

    for index, laptop in enumerate(cur.fetchall()):
        item = tk.Button(second_frame, text=f"{laptop[1]} {laptop[2]}", command=lambda id=laptop[0], widget_id = index+1: detail(id, widget_id))
        item.pack(fill="x")

display_data()
root.mainloop()