import csv
import sqlite3
import tkinter as tk

def remake_data():
    """
    a function to drop and remake the database. Takes in no argument
    """

    conn = sqlite3.connect("laptops.db")
    cur = conn.cursor()

    # the sql code for remaking the data is big so wrote it in another file. It shuld be in the same directory as this script
    with open("remakedata.sql", "r") as sqcode:
        cur.executescript(sqcode.read())
        conn.commit() 

    # it remakes the data from a csv file
    with open("Cleaned_Laptop_data.csv", "r") as file:

        laptops = csv.reader(file, delimiter = ",")

        # loops through each row, inserting the data one by one
        for index, laptop in enumerate(laptops):
            # first row is the header
            if index == 0: continue

            # just some string handling so the data inserted is what is to expected
            processor_gnrt= None if laptop[4] == "Missing" else int(laptop[4].replace("th", ""))

            ram = int(laptop[5].replace("GB", ""))

            ssd = int(laptop[7].replace("GB", ""))
            hdd = int(laptop[8].replace("GB", ""))

            os_bit = int(laptop[10].replace("-bit", ""))

            display = None if laptop[13] == "Missing" else float(laptop[13])

            touchscreen = 1 if laptop[15] == "Yes" else 0

            # I used another funtion responsible for inserting data so I could reuse the function later
            insert_data(cur, index, laptop[0], laptop[1], laptop[2], laptop[3], processor_gnrt, ram, laptop[6], ssd, hdd, laptop[9], os_bit, int(laptop[11]), laptop[12], display, touchscreen, int(laptop[17]), float(laptop[20]))

    
    conn.commit()
    conn.close()

def insert_data(cur, id, brand, model, processor_brand, processor_name, processor_generation, ram, ram_type, ssd, hdd, os, os_bit, graphic_card_gb, weight, display_size, touchscreen, price, rating):
    """
    this function takes in everything it needs to know about a laptop and inserts it into the database.
    """      

    # another function is used to give the foreign key or make the foreign key if it doesn't already exist 
    brand_id = get_key(True, "brands", f"name = '{brand}'", f"'{brand}'", "name", cur)
    processor_brand_id = get_key(True, "processor_brand", f"brand = '{processor_brand}'", f"'{processor_brand}'", "brand", cur)
    processor_id = get_key(True, "processor", f"brand_id = '{processor_brand_id}' and model = '{processor_name}'", f"'{processor_brand_id}', '{processor_name}'", "brand_id, model", cur)
    ram_type_id = get_key(True, "ram_type", f"type = '{ram_type}'", f"'{ram_type}'", "type", cur)
    disk_type_id = get_key(True, "disk_type", f"ssd = {ssd} and hdd = {hdd}", f"{ssd}, {hdd}", "ssd, hdd", cur)
    os_id = get_key(True, "os", f"name = '{os}'", f"'{os}'", "name", cur)
    weight_id = get_key(True, "weight", f"type = '{weight}'", f"'{weight}'", "type", cur)

    cur.execute("""
        INSERT INTO laptops (id, brand_id, model, processor_id, processor_generation, ram, ram_type_id, disk_type_id, os_id, os_bit, graphic_card_gb, weight_id, display_size, touchscreen, price, rating) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [id, brand_id, model, processor_id, processor_generation, ram, ram_type_id, disk_type_id, os_id, os_bit, graphic_card_gb, weight_id, display_size, touchscreen, price, rating])

def get_key(create, table, condition, item, values, cur):
    """
    this function will find the foreign key from the foreign table. If it doesn't exist, you can tell it to create it and retrun the key or just return None from the argument "create"
    """
    cur.execute(f"SELECT id FROM {table} WHERE {condition}")
    
    key = cur.fetchone()

    if key == None: 
        # no foreign key... what now?
        if create == False: return None

        # if it got here, it hasn't returned which means create is True and the key should be created
        cur.execute(f"INSERT INTO {table} ({values}) VALUES ({item})")

        cur.execute (f"SELECT id FROM {table} WHERE {condition}")

        return cur.fetchone()[0]
    else:
        # found the key! returning the key id now
        return key[0]
    

# def view_data(brand, model, processor_brand, processor_name, processor_generation, ram, ram_type, ssd, hdd, os, os_bit, graphic_card_gb, weight, display_size, touchscreen, price, rating):

    # brand_id = get_key(False, "brands", f"name = '{brand}'", None, None)
    # processor_id = get_key(False, "processors", f"brand = '{processor_brand}' and name = '{processor_name}'", None, None)
    # ram_type_id = get_key(False, "ram_type", f"type = '{ram_type}'", None, None)
    # disk_type_id = get_key(False, "disk_type", f"ssd < {ssd} and hdd < {hdd}", None, None)
    # os_id = get_key(False, "os", f"name = '{os}'", None, None)
    # weight_id = get_key(False, "weight", f"type = {weight}", None, None)

    # cur.execute(f"SELECT * FROM laptops WHERE brand_id = ? and model = ? and processor_id = ? and processor_generation > ? and ram > ? and ram_type_id = ? and disk_type_id = ? and os_id = ? and os_bit = ? and graphic_card_gb > ? and weight_id = integer and display_size = ? and touchscreen = ? and price < ? and rating > ?", 
    #     [brand_id, model, processor_id, processor_generation, ram, ram_type_id, disk_type_id, os_id, os_bit, graphic_card_gb, weight_id, display_size, touchscreen, price, rating]
    # )
    # print(cur.fetchall())

def all_keys(cur, table, items) -> dict():
    """
    this function gets all the keys from a table. Useful for when you need all the options available from a foreign table
    it returns a dictionary of the items pointing to their key.
    """

    # I used an f string because "items" can include 2 things (for example: ssd, hdd)
    cur.execute(f"SELECT id, {items} FROM {table}")

    result = cur.fetchall()


    # like stated in the last comment, it may have an id and 2 other things instead of just an id and an item. Because I know how I will use the function, I can write it to fit my need
    table = {}
    if len(result[0]) == 3:
        # if it includes an id and 3 other things, I want it to add the two items and point to the id
        for item in result:
            table[f"{item[1]} {item[2]}"] = item[0]
    
    else:
        # if it just has an item and an id, have the item point to the id
        for item in result:
            table[f"{item[1]}"] = item[0]
    
    return table

# averages
def get_average(cur, field, table, average):
    # average will be mean, median, or mode
    # start by getting all data from field
    result = cur.execute(f"SELECT {field} FROM {table} WHERE 1=1")
    numbers = result.fetchall()
   
    if average == "mean":
        # remove all non numbers before calculating the mean
        numbers = [num[0] for num in numbers if isinstance(num[0], int) or isinstance(num[0], float)]
        return f"average of {sum(numbers)/len(numbers)} (mean)"

    if average == "median":
        # remove all non numbers before calculating the median
        numbers = [num[0] for num in numbers if isinstance(num[0], int) or isinstance(num[0], float)]
        numbers.sort()
        return f"usually {numbers[len(numbers)//2]} (median)"

    if average == "mode":
        # this average works for strings
        numbers = [num[0] for num in numbers]
        # https://stackoverflow.com/questions/10797819/finding-the-mode-of-a-list thanks stackoverflow
        return f"commonly {max(set(numbers), key=numbers.count)} (mode)"

remake_data()