import csv
import sqlite3

conn = sqlite3.connect("laptops.db")
cur = conn.cursor()

def remake_data():
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

            insert_data(index, laptop[0], laptop[1], laptop[2], laptop[3], processor_gnrt, ram, laptop[6], ssd, hdd, laptop[9], os_bit, int(laptop[11]), laptop[12], display, touchscreen, int(laptop[17]), float(laptop[20]))

        conn.commit()
        
def insert_data(id, brand, model, processor_brand, processor_name, processor_generation, ram, ram_type, ssd, hdd, os, os_bit, graphic_card_gb, weight, display_size, touchscreen, price, rating):
    brand_id = get_key("brands", f"name = '{brand}'", f"'{brand}'", "name")
    processor_id = get_key("processor", f"brand = '{processor_brand}' and name = '{processor_name}'", f"'{processor_brand}', '{processor_name}'", "brand, name")
    ram_type_id = get_key("ram_type", f"type = '{ram_type}'", f"'{ram_type}'", "type")
    disk_type_id = get_key("disk_type", f"ssd = {ssd} and hdd = {hdd}", f"{ssd}, {hdd}", "ssd, hdd")
    os_id = get_key("os", f"name = '{os}'", f"'{os}'", "name")
    weight_id = get_key("weight", f"type = '{weight}'", f"'{weight}'", "type")

    cur.execute("insert into laptops (id, brand_id, model, processor_id, processor_generation, ram, ram_type_id, disk_type_id, os_id, os_bit, graphic_card_gb, weight_id, display_size, touchscreen, price, rating) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [id, brand_id, model, processor_id, processor_generation, ram, ram_type_id, disk_type_id, os_id, os_bit, graphic_card_gb, weight_id, display_size, touchscreen, price, rating])

def get_key(table, condition, item, values) -> int:
    cur.execute(
        f"""
        select id from {table} where {condition}
        """
    )
    
    response = cur.fetchone()

    if response == None:

        cur.execute(f"insert into {table} ({values}) values ({item})")

        cur.execute (f"select id from {table} where {condition}")

        return cur.fetchone()[0]
    else:
        return response[0]

def viewdata(condition):
    cur.execute(f"select * from laptops where {condition}")
    print(cur.fetchall())


viewdata()
conn.close()