import tkinter as tk
from backend import insert_data, all_keys, get_average
import sqlite3

class program():

    def __init__(self):

        # have the connection and cursor made before anything else. I also want this to be global
        self.conn = sqlite3.connect("laptops.db")
        self.cur = self.conn.cursor()

        # making the main gui window
        self.root = tk.Tk()
        self.root.title("Laptops")
        title = tk.Label(self.root, text="Laptops", font=("Sans", 15))
        title.pack()

        # canvas to contain everything
        button_ui = tk.Canvas(self.root)
        button_ui.pack()

        # a filter and add button
        filter_button = tk.Button(button_ui, text="filters", command=self.filter_window, font = ("Sans, 10"))
        filter_button.grid(row = 0, column = 1)

        add_button = tk.Button(button_ui, text = "add", command=self.add_window, font = ("Sans, 10"))
        add_button.grid(row = 0, column = 2)

        # sort by
        tk.Label(button_ui, text="sort by: ").grid(row = 1, column = 0)
        sort_by = tk.StringVar(button_ui)
        sort_by.set("model")
        sort_by_options = tk.OptionMenu(button_ui, sort_by, *["model", "ram", "graphic_card_gb", "price", "rating"])
        sort_by_options.grid(row = 1, column = 1)
        direction = tk.StringVar(button_ui)
        direction.set("ascending")
        direction_options = tk.OptionMenu(button_ui, direction, *["ascending", "descending"])
        direction_options.grid(row = 1, column = 2)

        # refresh main gui
        refresh_button = tk.Button(button_ui, text="refresh", command=lambda: self.display_data(sort_by=sort_by.get(), direction=direction.get()))
        refresh_button.grid(row = 1, column = 4)

        # create main frame
        main_frame = tk.Frame(self.root, height = 100, width = 100)
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

        # supporting mouse scrolling
        def _on_mousewheel(event):
            my_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

        my_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # below is for linux
        # my_canvas.bind_all("<Button-4>", _on_mousewheel)
        # my_canvas.bind_all("<Button-5>", _on_mousewheel) 

        # create another frame inside canvas
        self.second_frame = tk.Frame(my_canvas)

        # add new frame to window in canvas
        my_canvas.create_window((0,0), window=self.second_frame, anchor="nw")

        # display everything before runnint tkinter mainloop
        self.display_data()
        self.root.mainloop()

    def noinjection(self, statement, statement_type):
        """
        this function prevents sql injection. It takes in an entered field and what type it is meant to be before checking them accordingly
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

    def check_stupid(self, column, lowerbound, upperbound):
        """
        this function checks if the input by the user is stupid 
        """

        # convert both to integer
        lowerbound = int(lowerbound)
        upperbound = int(upperbound)

        # if check the value accordingly to the column
        if column == "price" or column == "ssd" or column == "hdd":

            if lowerbound < 0:
                return "stupid input detected"

        elif column == "rating":
            if lowerbound < 0 or upperbound > 5:
                return "rating is between 0 to 5"
        else:
            if upperbound > 100 or lowerbound < 0 or lowerbound > upperbound:
                return "stupid input detected"
        
        return True

    def filter_window(self):
        """
        this function spawns a window with filtering gui
        """

        # just some window configuration
        t = tk.Toplevel(self.root)
        t.wm_title("Filters")

        # a subfunction that is activated when pressing "comfirm filter"
        # note that this function will confuse you if you haven't read the rest of the function. It is very important to read the rest of the function first.
        def exit_filter():

            # it will write the sql statement as it goes through what the user has input
            condition = ""
            for column, info in dropdowns.items():

                # hdd and ssd will must be checked together as they belong together in one foreign table
                if column == "hdd": continue
                if column == "ssd":

                    if dropdowns["hdd"]["choice"].get() == "" and info["choice"].get() == "":
                        # if nothing is put for them both, it just takes all the id available
                        disk_filter = "SELECT id FROM disk_type;"
                    else:
                        # if something is placed for at least one of them, it will write a sql statement to filter the ones that fit the case 

                        hddentry = dropdowns["hdd"]["choice"].get()
                        hddentry2 = dropdowns["hdd"]["choice2"].get()
                        ssdentry = info["choice"].get()
                        ssdentry2 = info["choice2"].get()

                        if hddentry == "": hddentry = "0"
                        if hddentry2 == "": hddentry2 = "10000000"
                        if ssdentry == "": ssdentry = "0"
                        if ssdentry2 == "": ssdentry2 = "10000000"
                        
                        if not self.noinjection(hddentry, "int") or not self.noinjection(hddentry2, "int") or not self.noinjection(ssdentry, "int") or not self.noinjection(ssdentry2, "int"):
                            # if either one of the fails the anti sql injection test, everything will be displayed and the window will close
                            self.display_data(False, "numbers field only take in numbers")
                            t.destroy()
                            t.update()
                            return

                        disk_filter = f"SELECT id FROM disk_type WHERE (hdd between {hddentry} and {hddentry2}) and (ssd between {ssdentry} and {ssdentry2})" 
                        

                    # execute the sql statement and get all the available disk type ids
                    self.cur.execute(disk_filter)

                    disk_type_filter = "("

                    for valid_id in self.cur.fetchall():
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

                    if not self.noinjection(entry, "string"):
                        # if the entered string does not pass the anti sql injection test, it displays everything and destroys the window
                        self.display_data(False, "suspicious string detected")
                        t.destroy()
                        t.update()
                        return

                    # if it made it here, the prompt will be added onto the statement
                    condition += f"laptops.{column} like '%{entry}%' and "
                    
                    continue
                
                if info["option"] == "searchint" or info["option"] == "searchfloat":
                    # there is a below than option and an above than option
                    entry = info["choice"].get()
                    entry2 = info["choice2"].get()

                    # if the user didn't put anything for both field, skip it
                    if entry == "" and entry2 == "": continue

                    # if only one field is empty, fill it out for them
                    if entry == "": entry = "0"
                    if entry2 == "": entry2 = "10000000" if column == "price" else "5" if column == "rating" else "100"

                    if not self.noinjection(entry, "float") or not self.noinjection(entry2, "float"): 
                        # if the entered string does not pass the anti sql injection test, it displays everything and destroys the window
                        self.display_data(False, "number field only takes in numbers")
                        t.destroy()
                        t.update()
                        return

                    # checking for dumb inputs
                    check = self.check_stupid(column, entry, entry2)
                    if check is not True:
                        self.display_data(False, check)
                        t.destroy()
                        t.update()
                        return

                    # if it made it here, the prompt will be added onto the statement
                    condition += f"(laptops.{column} between {entry} and {entry2}) and"
                    
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

            # prints the finished condition to the console. Was for debugging but was kept for demonstration purposes
            print(condition)

            # this will display the filtered data on the main gui
            self.display_data(condition, sort_by=sort_by.get(), direction=direction.get())

            # destroys the window
            t.destroy()
            t.update()
            

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
            processor_generation= {"foreign": False, "option": "searchint", "average": "median"},
            ram= {"foreign": False, "option": "searchint", "average": "mode"},
            ram_type= {"foreign": True, "table": "ram_type", "items": "type", "option": "dropdown", "average": "mode"},
            ssd= {"foreign": False, "option": "searchint", "average": "median"},
            hdd= {"foreign": False, "option": "searchint", "average": "median"},
            os= {"foreign": True, "table": "os", "items": "name", "option": "dropdown", "average": "mode"},
            os_bit= {"foreign": False, "option": "searchint", "average": "median"},
            graphic_card_gb= {"foreign": False, "option": "searchint", "option": "median"},
            weight= {"foreign": True, "table": "weight", "items": "type", "option": "dropdown"},
            display_size= {"foreign": False, "option": "searchfloat", "average": "mean"},
            touchscreen= {"foreign": False, "option": "boolean"},
            price= {"foreign": False, "option": "searchint", "average": "mean"},
            rating= {"foreign": False, "option": "searchfloat", "average": "mean"},
        )

        # loops through the dictionary and makes the gui

        # index, (field, field_information)
        for i , (column, info) in enumerate(dropdowns.items()):

            # this displays the field name
            tk.Label(t, text=column).grid(row = i+1, column = 0)
            
            if info["foreign"] == True:

                # processor is special
                if column == "processor":
                    
                    # selects all processors with their id, brand, and model
                    self.cur.execute(f"""
                        SELECT processor.id, processor_brand.brand, processor.model FROM processor 
                        LEFT JOIN processor_brand
                        ON processor.brand_id = processor_brand.id;
                    """)

                    # making the dictionary that can convert from item to key
                    options = {}

                    for cpu in self.cur.fetchall():
                        options[f"{cpu[1]} {cpu[2]}"] = cpu[0]
                    
                    # after this, continue like the rest of the foreign fields
                else:
                    # this is a common foreign field, just make the item to key dictionary and continue with the code
                    options = all_keys(self.cur, info["table"], info["items"])

                # make the dropdown ui
                choice = tk.StringVar(t)
                choice.set("None")

                choice_select = tk.OptionMenu(t, choice, *options)
                choice_select.grid(row = i+1, column = 2)
                
                if "average" in info:
                    average = get_average(self.cur, info["items"], info["table"], info["average"])
                    tk.Label(t, text=average).grid(row=i+1, column =5)

                # save the choice the user will enter and the dictionary to convert from item back to id
                info["choice"] = choice
                info["dictionary"] = options

                continue

            if info["option"] == "search":
                # simply make a text field
                entry = tk.Entry(t)
                entry.grid(row = i+1, column=2)

                # save the entry
                info["choice"] = entry
            
            if info["option"] == "searchint" or info["option"] == "searchfloat":
                # add two entry field, one for < one for >
                entry = tk.Entry(t)
                entry.grid(row = i+1, column = 0)

                # overides the original label
                tk.Label(t, text = column).grid(row = i+1, column=2)
                tk.Label(t, text = "<=").grid(row = i+1, column=3)
                tk.Label(t, text = "<=").grid(row = i+1, column=1)

                entry2 = tk.Entry(t)
                entry2.grid(row = i+1, column = 4)

                # if an average is set
                if "average" in info: 

                    if column == "ssd" or column == "hdd":
                        average = get_average(self.cur, column, "disk_type", info["average"])
                    else:
                        average = get_average(self.cur, column, "laptops", info["average"])
                    
                    # put info on column 5
                    tk.Label(t, text = average).grid(row = i+1, column=5)

                # remember the entry and the operator 
                info["choice"] = entry
                info["choice2"] = entry2
            
            if info["option"] == "boolean": 
                # make a checkbox
                boo = tk.IntVar()
                checkbox = tk.Checkbutton(t, variable=boo).grid(row = i+1, column = 2)

                # remember check box entry
                info["choice"] = boo
        

        # sort by
        tk.Label(t, text="sort by: ").grid(row = 17, column = 0)
        sort_by = tk.StringVar(t)
        sort_by.set("model")
        sort_by_options = tk.OptionMenu(t, sort_by, *["model", "ram", "graphic_card_gb", "price", "rating"])
        sort_by_options.grid(row = 17, column = 1)
        direction = tk.StringVar(t)
        direction.set("ascending")
        direction_options = tk.OptionMenu(t, direction, *["ascending", "descending"])
        direction_options.grid(row = 17, column = 2)


    def add_window(self):
        """
        this function spawns a window with the add gui
        """
        t = tk.Toplevel(self.root)
        t.wm_title("Add")

        # function that runs when the "add laptop" button is pressed. similar to the filter gui function, read the rest of the code in this function before reading this one or you will be confused
        def add_laptop():
            
            # loops through laptop_info dictionary
            for key, info in laptop_info.items():
                if info["type"] == "foreign":
                    # if nothing is entered, display everything and close window
                    if info["entry"].get() == "None": 
                        self.display_data(False, "field not entered")
                        t.destroy()
                        t.update()
                        return

                    
                    info["entry"] = info["entry"].get()
                    continue
                
                
                if info["entry"].get() == "":

                    # if nothing is entered but it is optional, set the entry to the default value. otherwise, display all data and close window
                    if "optional" in info.keys():
                        info["entry"] = info["default"]
                        continue
                    else:
                        self.display_data(False, "field not entered")
                        t.destroy()
                        t.update()
                        return

                if not self.noinjection(info["entry"].get(), info["type"]): 
                    # if entry fails the anti sql injection test, display everything and close window
                    self.display_data(False, "suspicious characters detected")
                    t.destroy()
                    t.update()
                    return

                if info["type"] == "string":
                    # if entry type is meant to be a string, set the first character to upper case and everything else to lower
                    entry = info["entry"].get()
                    info["entry"] = entry[0].upper() + entry[1:].lower()
                    
                if info["type"] == "int":
                    # check if input is stupid
                    check = self.check_stupid(key, info["entry"].get(), info["entry"].get())
                    if check is not True:
                        self.display_data(False, check)
                        t.destroy()
                        t.update()
                        return
                        
                    info["entry"] = int(info["entry"].get())

                if info["type"] == "float":
                    info["entry"] = float(info["entry"].get())

                if info["type"] == "bool":
                    info["entry"] = info["entry"].get()
    

            # get the id of the new laptop by taking the amount of laptops in the database +1
            self.cur.execute("SELECT * FROM laptops where 1 = 1")
            id = len(self.cur.fetchall())+1

            # just prints to the console. Was for debugging purposes but I decided to keep it for demonstration purposes
            print(id, laptop_info["brand"]["entry"], laptop_info["model"]["entry"], laptop_info["processor_brand"]["entry"], laptop_info["processor_name"]["entry"], laptop_info["processor_generation"]["entry"], laptop_info["ram"]["entry"], laptop_info["ram_type"]["entry"], laptop_info["ssd"]["entry"], laptop_info["hdd"]["entry"], laptop_info["os"]["entry"], laptop_info["os_bit"]["entry"], laptop_info["graphic_card_gb"]["entry"], laptop_info["weight"]["entry"], laptop_info["display_size"]["entry"], laptop_info["touchscreen"]["entry"], laptop_info["price"]["entry"], laptop_info["rating"]["entry"])

            # use the insert function from the other python file to easily insert the new data
            insert_data(self.cur, laptop_info["brand"]["entry"], laptop_info["model"]["entry"], laptop_info["processor_brand"]["entry"], laptop_info["processor_name"]["entry"], laptop_info["processor_generation"]["entry"], laptop_info["ram"]["entry"], laptop_info["ram_type"]["entry"], laptop_info["ssd"]["entry"], laptop_info["hdd"]["entry"], laptop_info["os"]["entry"], laptop_info["os_bit"]["entry"], laptop_info["graphic_card_gb"]["entry"], laptop_info["weight"]["entry"], laptop_info["display_size"]["entry"], laptop_info["touchscreen"]["entry"], laptop_info["price"]["entry"], laptop_info["rating"]["entry"])
            
            # commit because the function doesn't do that
            self.conn.commit()

            # close window, display everything with the appropriate message
            t.destroy()
            t.update()
            self.display_data(False, "laptop has been added")
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
                options = all_keys(self.cur, info["table"], info["items"])
                choice = tk.StringVar(t)
                choice.set("None")

                choice_select = tk.OptionMenu(t, choice, *options)
                choice_select.grid(row = i+1, column = 2)

                # saves the user option
                info["entry"] = choice
                continue

            if info["type"] == "bool":
                # makes a checkbox
                boo = tk.IntVar()
                checkbox = tk.Checkbutton(t, variable=boo).grid(row = i+1, column = 2)
                # saves user option
                info["entry"] = boo
                continue

            if info["type"] == "int" or info["type"] == "float":
                # if its a integer or float we are expecting, we will add the unit behind the entry box
                tk.Label(t, text = info["unit"]).grid(row=i+1, column=3)

            if "optional" not in info: 
                tk.Label(t, text = "*required").grid(row=i+1, column=4)

            # an entry box for int and string fields
            entry = tk.Entry(t)
            entry.grid(row=i+1, column=2)
            # saves user option
            info["entry"] = entry

    # add items into second frame
    def detail(self, id):
        """
        this function displays more data on the laptop clicked by user on the main gui
        """

        # gets more information from the laptop id
        self.cur.execute(f"""
        SELECT brands.name, laptops.model, laptops.processor_generation, processor.model, ram_type.type, laptops.ram, disk_type.ssd, disk_type.hdd, os.name, laptops.os_bit, laptops.graphic_card_gb, weight.type, laptops.display_size, laptops.touchscreen, laptops.price, laptops.rating
        FROM laptops LEFT JOIN brands ON laptops.brand_id = brands.id
        LEFT JOIN processor ON laptops.processor_id = processor.id
        LEFT JOIN ram_type ON laptops.ram_type_id = ram_type.id
        LEFT JOIN disk_type ON laptops.disk_type_id = disk_type.id
        LEFT JOIN os ON laptops.os_id = os.id
        LEFT JOIN weight ON laptops.weight_id = weight.id
        WHERE laptops.id = {id}
        """)

        # fetch the laptop
        laptop = self.cur.fetchone()

        t = tk.Toplevel(self.root)
        t.wm_title(f"{laptop[0]} {laptop[1]}")

        # set text
        tk.Label(t, text = f"""{laptop[0]} {laptop[1]} 
        ssd: {laptop[6]}GB hdd: {laptop[7]}GB
        ram: {laptop[5]}GB {laptop[4]} 
        cpu: {laptop[3]} {str(laptop[2]) + "th gen" if laptop[2] else ""}
        os: {laptop[8]} bit: {laptop[9]}
        graphics card: {laptop[10]}GB
        weight: {laptop[11]}
        display size: {laptop[12] if laptop[12] else "undefined"}
        touchsceen: {"true" if laptop[13] == 1 else "false"}
        price: {laptop[14] if laptop[14] else "undefined"} 
        rating: {laptop[15] if laptop[15] else "undefined"}
        id: {id}
        """, font=("15"), justify="left").pack(anchor="nw")

    def display_data(self, condition = False, error = None, sort_by = "model", direction = "ascending"):
        """
        this function displays all the laptop on the main gui for the user, it also prints out the "error" message
        """

        # destroys everything in the scrolling widget
        for widget in self.second_frame.winfo_children():
            widget.destroy()
    
        # if no conditions are given, display everything, otherwise, display with condition
        if not condition:
            self.cur.execute(f"""
                SELECT laptops.id, brands.name, laptops.model, laptops.processor_generation, processor.model, ram_type.type, laptops.ram, disk_type.ssd, disk_type.hdd, os.name, laptops.os_bit, laptops.graphic_card_gb, weight.type, laptops.display_size, laptops.touchscreen, laptops.price, laptops.rating
                FROM laptops 
                LEFT JOIN brands ON laptops.brand_id = brands.id
                LEFT JOIN processor ON laptops.processor_id = processor.id
                LEFT JOIN ram_type ON laptops.ram_type_id = ram_type.id
                LEFT JOIN disk_type ON laptops.disk_type_id = disk_type.id
                LEFT JOIN os ON laptops.os_id = os.id
                LEFT JOIN weight ON laptops.weight_id = weight.id
                ORDER BY laptops.{sort_by} {"ASC" if direction == "ascending" else "DESC"}
            """)
        else:
            self.cur.execute(f"""
            SELECT laptops.id, brands.name, laptops.model, laptops.processor_generation, processor.model, ram_type.type, laptops.ram, disk_type.ssd, disk_type.hdd, os.name, laptops.os_bit, laptops.graphic_card_gb, weight.type, laptops.display_size, laptops.touchscreen, laptops.price, laptops.rating
            FROM laptops 
            LEFT JOIN brands ON laptops.brand_id = brands.id
            LEFT JOIN processor ON laptops.processor_id = processor.id
            LEFT JOIN ram_type ON laptops.ram_type_id = ram_type.id
            LEFT JOIN disk_type ON laptops.disk_type_id = disk_type.id
            LEFT JOIN os ON laptops.os_id = os.id
            LEFT JOIN weight ON laptops.weight_id = weight.id
            WHERE {condition}
            ORDER BY laptops.{sort_by} {"ASC" if direction == "ascending" else "DESC"}
            """)
        
        result = self.cur.fetchall()
        
        if not error:
            # if there are no issue with the prompt, display amoung of results
            tk.Label(self.second_frame, text = f"showing {len(result)} results (click on a model for more info)").pack(fill = "x")
        else:
            # display error message
            tk.Label(self.second_frame, text = error, fg="red", font=("15")).pack(fill = "x")


        # pack each laptop as a button that expands when the user clicks on it
        for index, laptop in enumerate(result):
            # item = tk.Button(second_frame, text=f"{laptop[1]} {laptop[2]}", command=lambda id=laptop[0], widget_id = index+1: detail(id, widget_id))
            item = tk.Button(self.second_frame, text=f"{laptop[1]} {laptop[2]}", command=lambda id=laptop[0]: self.detail(id))
            item.pack(fill="x")


if __name__ == "__main__":
    program()
    # the classic dunder statement with the twist. It is important that these variables below are global for the sake of clean code, therefore I did not restrict them to the scope of a main function
    pass