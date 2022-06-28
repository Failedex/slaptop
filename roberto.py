import tkinter as tk
from slap import view_data, insert_data, all_keys
import sqlite3

# have the connection and cursor made before anything else
conn = sqlite3.connect("laptops.db")
cur = conn.cursor()

# making the main gui window
root = tk.Tk()
root.title("Roberto")
title = tk.Label(root, text="Laptops", font=("Sans", 15))
title.pack()

# this function will make sure that only one child window is on at any point
window_on = False

def noinjection(statement, statement_type):
    """
    this function pprevents sql injection. It takes in an entered field and what type it is meant to be before checking them accordingly
    """

    if statement_type == "string":
        # check for the suspicious strings
        if any(x in statement for x in ["\"", "\'", ";", "--", "%", "/", "!"]):
            return False
        
    if statement_type == "int":
        # just make sure everything is a number
        if not statement.isdigit(): 
            return False
    
    if statement_type == "float":
        # very clever solution https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
        if not statement.replace(".", "", 1).isdigit():
            return False
    
    return True

def filter_window():
    """
    this function spawns a window with filtering gui
    """
    global window_on

    # is there is already a window open return
    if window_on: return
    # no window is open, continue and set it to true.
    window_on = True

    # just some window configuration
    t = tk.Toplevel(root)
    t.wm_title("laptop filters")

    # a subfunction that is activated when pressing "comfirm filter"
    # note that this function will confuse you if you haven't read the rest of the function
    def exit_filter():
        global window_on

        # it will write the sql statement as it goes through what the user has input
        condition = ""
        for column, info in dropdowns.items():

            # hdd and ssd will be checked together as they belong together in one foreign table
            if column == "hdd": continue
            if column == "ssd":

                if dropdowns["hdd"]["choice"].get() == "" and info["choice"].get() == "":
                    # if nothing is put for them both, it just takes all the id available
                    disk_filter = "select id from disk_type;"
                else:
                    # if something is placed for at least one of them, it will write a sql statement to filter the ones that fit the case 
                    disk_filter = "select id from disk_type where "
                    if not noinjection(dropdowns["hdd"]["choice"].get(), "int") or not noinjection(info["choice"].get(), "int"):
                        # if either one of the fails the anti sql injection test, everything will be displayed and the window will close
                        display_data(False, "numbers field only take in numbers")
                        t.destroy()
                        t.update()
                        window_on = False
                        return

                    # if the following field isn't empty, add to the sql statement
                    if dropdowns["hdd"]["choice"].get() != "":
                        disk_filter += f"hdd {dropdowns['hdd']['operator'].get()} {dropdowns['hdd']['choice'].get()} and "
                    
                    if info["choice"].get() != "":
                        disk_filter += f"ssd {info['operator'].get()} {info['choice'].get()} and "
                    
                    # take out the last "and" and add a semicolon
                    disk_filter = disk_filter[:-4] + ";"

                # execute the sql statement and get all the available disk type ids
                cur.execute(disk_filter)

                disk_type_filter = "("

                for valid_id in cur.fetchall():
                    disk_type_filter += f"laptops.disk_type_id = {valid_id[0]} or "
                
                # take out the last "or" and add a closing bracket before continuing
                condition += disk_type_filter[:-3] + ") and "
                continue


            if info["foreign"]: 

                # get the id from its saved dictionary
                choice = info["choice"].get()
                dictionary = info["dictionary"]
                
                # if there is nothing selected, don't add on to the statement
                if choice == "None": continue

                # added the "_id" because all my foreign key column name strategicly end with _id
                condition += f"laptops.{column}_id = {dictionary[choice]} and "
                
                continue
            
            if info["option"] == "search":
                entry = info["choice"].get()

                # if the user didn't put anything for this field, skip it
                if entry == "": continue

                if not noinjection(entry, "string"):
                    # if the entered string does not pass the anti sql injection test, it displays everything and destroys the window
                    display_data(False, "suspicious string detected")
                    t.destroy()
                    t.update()
                    window_on = False
                    return

                # if it made it here, the prompt will be added onto the statement
                condition += f"laptops.{column} like '%{entry}%' and "
                
                continue
            
            if info["option"] == "searchint" or info["option"] == "searchfloat":
                entry = info["choice"].get()

                # if the user didn't put anything for this field, skip it
                if entry == "": continue

                if not noinjection(entry, "float"): 
                    # if the entered string does not pass the anti sql injection test, it displays everything and destroys the window
                    display_data(False, "number field only takes in numbers")
                    t.destroy()
                    t.update()
                    window_on = False
                    return

                # bigger than, smaller than, or equal to
                operator = info["operator"].get()

                # if it made it here, the prompt will be added onto the statement
                condition += f"laptops.{column} {operator} {entry} and "
                
                continue
                    
            if info["option"] == "boolean":
                boo = info["choice"].get()


                # if this field isn't selected, don't add it to the statement
                if boo == 0: continue

                # if it made it here, the prompt will be added onto the statement
                condition += f"laptops.{column} = {boo} and "

                continue
        
        # remove the last "and" from the sql filter statement
        condition = condition[:-4]
        print(condition)

        # this will display the filtered data on the main gui
        display_data(condition)

        # destroys the window before setting window_on back to False, allowing another window to be open
        t.destroy()
        t.update()
        window_on = False
        

    # read below before reading the exit_filter function

    # a visible title for the window
    tk.Label(t, text="Filters", font = ("Sans, 15")).grid(row = 0, column = 0, columnspan=2)

    # a save filter function for when the user is done setting their filter
    save = tk.Button(t, text="comfirm filter", command=exit_filter).grid(row = 0, column= 2)
    
    # since I want to do this recursively, I made a function that will contain everything that will be needed for the field such as foreign, option type, dictionary to convert from foreign item back to foreign key, and the user iuput
    dropdowns = dict(
        brand= {"foreign": True, "table": "brands", "items": "name", "option": "dropdown"}, 
        model= {"foreign": False, "option":"search"},
        processor= {"foreign": True, "special": True},
        processor_generation= {"foreign": False, "option": "searchint"},
        ram= {"foreign": False, "option": "searchint"},
        ram_type= {"foreign": True, "table": "ram_type", "items": "type", "option": "dropdown"},
        ssd= {"foreign": False, "option": "searchint"},
        hdd= {"foreign": False, "option": "searchint"},
        os= {"foreign": True, "table": "os", "items": "name", "option": "dropdown"},
        os_bit= {"foreign": False, "option": "searchint"},
        graphic_card_gb= {"foreign": False, "option": "searchint"},
        weight= {"foreign": True, "table": "weight", "items": "type", "option": "dropdown"},
        display_size= {"foreign": False, "option": "searchfloat"},
        touchscreen= {"foreign": False, "option": "boolean"},
        price= {"foreign": False, "option": "searchint"},
        rating= {"foreign": False, "option": "searchfloat"},
    )

    # loops through the dictionary and makes the gui
    for i , (column, info) in enumerate(dropdowns.items()):

        # this displays the field name
        tk.Label(t, text=column).grid(row = i+1, column = 0)
        
        if info["foreign"] == True:

            # processor is special. So is disk_type
            if column == "processor":
                touched_grass = False
                
                # selects all processors with their id, brand, and model
                cur.execute(f"""
                    select processor.id, processor_brand.brand, processor.model from processor 
                    left join processor_brand
                    on processor.brand_id = processor_brand.id;
                """)

                # making the dictionary that can convert from item to key
                options = {}

                for cpu in cur.fetchall():
                    options[f"{cpu[1]} {cpu[2]}"] = cpu[0]
                
                # after this, continue like the rest of the foreign fields
            else:
                # this is a common foreign field, just make the item to key dictionary and continue with the code
                options = all_keys(cur, info["table"], info["items"])

            # make the dropdown ui
            choice = tk.StringVar(t)
            choice.set("None")

            choice_select = tk.OptionMenu(t, choice, *options)
            choice_select.grid(row = i+1, column = 2)

            # save the choice the user will enter and the dictionary to convert from item back to id
            dropdowns[column]["choice"] = choice
            dropdowns[column]["dictionary"] = options

            continue

        if info["option"] == "search":
            # simply make a text field
            entry = tk.Entry(t)
            entry.grid(row = i+1, column=2)

            # save the entry
            dropdowns[column]["choice"] = entry
        
        if info["option"] == "searchint" or info["option"] == "searchfloat":
            # make a dropdown of operators bigger than, smaller than, and equal to
            
            options = [">=", "<=", "="]
            choice = tk.StringVar(t)
            choice.set("=")
            choice_select = tk.OptionMenu(t, choice, *options)
            choice_select.grid(row = i+1, column = 1)

            # add an entry field
            entry = tk.Entry(t)
            entry.grid(row = i+1, column = 2)

            # remember the entry and the operator 
            dropdowns[column]["choice"] = entry
            dropdowns[column]["operator"] = choice
        
        if info["option"] == "boolean": 
            # make a checkbox
            boo = tk.IntVar()
            checkbox = tk.Checkbutton(t, variable=boo).grid(row = i+1, column = 2)

            # remember check box entry
            dropdowns[column]["choice"] = boo


def add_window():
    """
    this function spawns a window with the add gui
    """
    global window_on

    # similar code to before. Prevents multiple top window from being spawned
    if window_on: return
    window_on = True

    t = tk.Toplevel(root)
    t.wm_title("laptop add")

    # function that runs when the "add laptop" button is pressed. similar to the filter gui function, read the rest of the code in this function before reading this one or you will be confused
    def add_laptop():
        global window_on
        
        # loops through laptop_info dictionary
        for key, info in laptop_info.items():
            if info["type"] == "foreign":
                # if nothing is entered, display everything and close window
                if info["entry"].get() == "None": 
                    display_data(False, "field not entered")
                    t.destroy()
                    t.update()
                    window_on = False
                    return

                
                info["entry"] = info["entry"].get()
                continue
            
            
            if info["entry"].get() == "":

                # if nothing is entered but it is optional, set the entry to the default value. otherwise, display all data and close window
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
                # if entry fails the anti sql injection test, display everything and close window
                display_data(False, "suspicious characters detected")
                t.destroy()
                t.update()
                window_on = False
                return

            if info["type"] == "string":
                # if entry type is meant to be a string, set the first character to upper case and everything else to lower
                entry = info["entry"].get()
                laptop_info[key]["entry"] = entry[0].upper() + entry[1:].lower()
                
            if info["type"] == "int":
                info["entry"] = int(info["entry"].get())

            if info["type"] == "float":
                info["entry"] = float(info["entry"].get())

            if info["type"] == "bool":
                info["entry"] = info["entry"].get()
 

        # get the id of the new laptop by taking the amount of laptops in the database +1
        id = len(view_data(cur, "1 = 1"))+1

        print(id, laptop_info["brand"]["entry"], laptop_info["model"]["entry"], laptop_info["processor_brand"]["entry"], laptop_info["processor_name"]["entry"], laptop_info["processor_generation"]["entry"], laptop_info["ram"]["entry"], laptop_info["ram_type"]["entry"], laptop_info["ssd"]["entry"], laptop_info["hdd"]["entry"], laptop_info["os"]["entry"], laptop_info["os_bit"]["entry"], laptop_info["graphic_card_gb"]["entry"], laptop_info["weight"]["entry"], laptop_info["display_size"]["entry"], laptop_info["touchscreen"]["entry"], laptop_info["price"]["entry"], laptop_info["rating"]["entry"])

        # use the insert function from the other python file to easily insert the new data
        insert_data(cur, id, laptop_info["brand"]["entry"], laptop_info["model"]["entry"], laptop_info["processor_brand"]["entry"], laptop_info["processor_name"]["entry"], laptop_info["processor_generation"]["entry"], laptop_info["ram"]["entry"], laptop_info["ram_type"]["entry"], laptop_info["ssd"]["entry"], laptop_info["hdd"]["entry"], laptop_info["os"]["entry"], laptop_info["os_bit"]["entry"], laptop_info["graphic_card_gb"]["entry"], laptop_info["weight"]["entry"], laptop_info["display_size"]["entry"], laptop_info["touchscreen"]["entry"], laptop_info["price"]["entry"], laptop_info["rating"]["entry"])
        
        # commit because the function doesn't do that
        conn.commit()

        # close window, display everything with the appropriate message
        t.destroy()
        t.update()
        window_on = False
        display_data(False, "laptop has been added")
        return
        

    # title 
    tk.Label(t, text="Add Laptop", font = ("Sans, 15")).grid(row = 0, column = 0, columnspan=2)

    # "add" button
    add = tk.Button(t, text="add laptop", command = add_laptop).grid(row = 0, column= 2)

    # dictionary with all the field info including what the user enters for each field
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
        display_size = {"type": "float", "unit": "inches"},
        touchscreen = {"type": "bool"},
        price = {"type": "int", "optional": True, "default": None, "unit": "$"},
        rating = {"type": "float", "optional": True, "default": 0, "unit": "stars"},
    )

    # loops through the dictionary to make the ui
    for i, (key, info) in enumerate(laptop_info.items()):

        # makes a header for each one
        heading = tk.Label(t, text = key).grid(row = i+1, column = 0)

        if info["type"] == "foreign":
            # makes a dropdown menu
            options = all_keys(cur, info["table"], info["items"])
            choice = tk.StringVar(t)
            choice.set("None")

            choice_select = tk.OptionMenu(t, choice, *options)
            choice_select.grid(row = i+1, column = 2)

            # saves the user option
            laptop_info[key]["entry"] = choice
            continue

        if info["type"] == "bool":
            # makes a checkbox
            boo = tk.IntVar()
            checkbox = tk.Checkbutton(t, variable=boo).grid(row = i+1, column = 2)
            # saves user option
            laptop_info[key]["entry"] = boo
            continue

        if info["type"] == "int" or info["type"] == "float":
            # if its a integer or float we are expecting, we will add the unit behind the entry box
            tk.Label(t, text = info["unit"]).grid(row=i+1, column=3)

        # an entry box for int and string fields
        entry = tk.Entry(t)
        entry.grid(row=i+1, column=2)
        # saves user option
        laptop_info[key]["entry"] = entry


# a filter and add button
filter_button = tk.Button(root, text="filters", command=filter_window, font = ("Sans, 10"))
filter_button.pack(side = "top", anchor="ne")

add_button = tk.Button(root, text = "add", command=add_window, font = ("Sans, 10"))
add_button.pack(side = "top", anchor="ne")

# create main frame
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
    """
    this function displays more data on the laptop clicked by user on the main gui
    """

    # gets more information from the laptop id
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

    # fetch the laptop
    laptop = cur.fetchone()

    # get the right button with the button id and the second_frame widget
    btn = second_frame.winfo_children()[btn_id]

    # set text
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


def display_data(condition = False, error = ""):
    """
    this function displays all the laptop on the main gui for the user, it also prints out the "error" message
    """

    # destroys everything in the scrolling widget
    for widget in second_frame.winfo_children():
        widget.destroy()
    
    # display error message
    tk.Label(second_frame, text = error, fg="red", font=("15")).pack(fill = "x")

    # if no conditions are given, display everything, otherwise, display with condition
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
    
    # pack each laptop as a button that expands when the user clicks on it
    for index, laptop in enumerate(cur.fetchall()):
        item = tk.Button(second_frame, text=f"{laptop[1]} {laptop[2]}", command=lambda id=laptop[0], widget_id = index+1: detail(id, widget_id))
        item.pack(fill="x")

# display everything before runnint tkinter mainloop
display_data()
root.mainloop()