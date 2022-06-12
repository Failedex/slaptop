import csv
import sqlite3
import tkinter as tk

def remake_data():
    conn = sqlite3.connect("laptops.db")
    cur = conn.cursor()

    with open("remakedata.sql", "r") as sqcode:
        cur.executescript(sqcode.read())
        conn.commit() 

    with open("Cleaned_Laptop_data.csv", "r") as file:

        laptops = csv.reader(file, delimiter = ",")
        for index, laptop in enumerate(laptops):
            if index == 0: continue

            processor_gnrt= None if laptop[4] == "Missing" else int(laptop[4].replace("th", ""))

            ram = int(laptop[5].replace("GB", ""))

            ssd = int(laptop[7].replace("GB", ""))
            hdd = int(laptop[8].replace("GB", ""))

            os_bit = int(laptop[10].replace("-bit", ""))

            display = None if laptop[13] == "Missing" else float(laptop[13])

            touchscreen = 1 if laptop[15] == "Yes" else 0

            insert_data(cur, index, laptop[0], laptop[1], laptop[2], laptop[3], processor_gnrt, ram, laptop[6], ssd, hdd, laptop[9], os_bit, int(laptop[11]), laptop[12], display, touchscreen, int(laptop[17]), float(laptop[20]))

        conn.commit()
    conn.close()
        
def insert_data(cur, id, brand, model, processor_brand, processor_name, processor_generation, ram, ram_type, ssd, hdd, os, os_bit, graphic_card_gb, weight, display_size, touchscreen, price, rating):

    brand_id = get_key(True, "brands", f"name = '{brand}'", f"'{brand}'", "name", cur)
    processor_brand_id = get_key(True, "processor_brand", f"brand = '{processor_brand}'", f"'{processor_brand}'", "brand", cur)
    processor_id = get_key(True, "processor", f"brand_id = '{processor_brand_id}' and model = '{processor_name}'", f"'{processor_brand_id}', '{processor_name}'", "brand_id, model", cur)
    ram_type_id = get_key(True, "ram_type", f"type = '{ram_type}'", f"'{ram_type}'", "type", cur)
    disk_type_id = get_key(True, "disk_type", f"ssd = {ssd} and hdd = {hdd}", f"{ssd}, {hdd}", "ssd, hdd", cur)
    os_id = get_key(True, "os", f"name = '{os}'", f"'{os}'", "name", cur)
    weight_id = get_key(True, "weight", f"type = '{weight}'", f"'{weight}'", "type", cur)

    cur.execute("insert into laptops (id, brand_id, model, processor_id, processor_generation, ram, ram_type_id, disk_type_id, os_id, os_bit, graphic_card_gb, weight_id, display_size, touchscreen, price, rating) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [id, brand_id, model, processor_id, processor_generation, ram, ram_type_id, disk_type_id, os_id, os_bit, graphic_card_gb, weight_id, display_size, touchscreen, price, rating])

def get_key(create, table, condition, item, values, cur) -> int|None:

    cur.execute(
        f"""
        select id from {table} where {condition}
        """
    )
    
    response = cur.fetchone()

    if response == None: 
        
        if create == False: return None
        cur.execute(f"insert into {table} ({values}) values ({item})")

        cur.execute (f"select id from {table} where {condition}")

        return cur.fetchone()[0]
    else:
        return response[0]
    

# def view_data(brand, model, processor_brand, processor_name, processor_generation, ram, ram_type, ssd, hdd, os, os_bit, graphic_card_gb, weight, display_size, touchscreen, price, rating):

    # brand_id = get_key(False, "brands", f"name = '{brand}'", None, None)
    # processor_id = get_key(False, "processors", f"brand = '{processor_brand}' and name = '{processor_name}'", None, None)
    # ram_type_id = get_key(False, "ram_type", f"type = '{ram_type}'", None, None)
    # disk_type_id = get_key(False, "disk_type", f"ssd < {ssd} and hdd < {hdd}", None, None)
    # os_id = get_key(False, "os", f"name = '{os}'", None, None)
    # weight_id = get_key(False, "weight", f"type = {weight}", None, None)

    # cur.execute(f"select * from laptops where brand_id = ? and model = ? and processor_id = ? and processor_generation > ? and ram > ? and ram_type_id = ? and disk_type_id = ? and os_id = ? and os_bit = ? and graphic_card_gb > ? and weight_id = integer and display_size = ? and touchscreen = ? and price < ? and rating > ?", 
    #     [brand_id, model, processor_id, processor_generation, ram, ram_type_id, disk_type_id, os_id, os_bit, graphic_card_gb, weight_id, display_size, touchscreen, price, rating]
    # )
    # print(cur.fetchall())

def view_data(cur, condition):

    cur.execute(f"select * from laptops where {condition}")
    return cur.fetchall()


def all_keys(cur, table, items):

    cur.execute(f"select id, {items} from {table}")

    res = cur.fetchall()

    dic = {}
    if len(res[0]) == 3:
        for item in res:
            dic[f"{item[1]} {item[2]}"] = item[0]
    
    else:
        for item in res:
            dic[f"{item[1]}"] = item[0]
    
    return dic
