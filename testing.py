import csv
import sqlite3 as sql

# I wrote this program to print out every 10 info from the original csv file and the sql database. I did this so I can compare the 2 and make sure the info was inserted correctly.

conn = sql.connect("laptops.db")
cur = conn.cursor()

with open("Cleaned_Laptop_data.csv", "r") as f:
    laptops = csv.reader(f, delimiter = ",")

    # loop through each csv row
    for index, laptop in enumerate(laptops):

        # ignore header and every row that's not a multiple of 10
        if index == 0 or index % 10 != 0: continue

        # get the same laptop from the row number of the laptop in the csv file because it is the same as the id in the database 
        cur.execute(f"""
            SELECT brands.name, laptops.model, processor.model, laptops.processor_generation, ram_type.type, laptops.ram, disk_type.ssd, disk_type.hdd, os.name, laptops.os_bit, laptops.graphic_card_gb, weight.type, laptops.display_size, laptops.touchscreen, laptops.price, laptops.rating
            FROM laptops 
            LEFT JOIN brands ON laptops.brand_id = brands.id
            LEFT JOIN processor ON laptops.processor_id = processor.id
            LEFT JOIN ram_type ON laptops.ram_type_id = ram_type.id
            LEFT JOIN disk_type ON laptops.disk_type_id = disk_type.id
            LEFT JOIN os ON laptops.os_id = os.id
            LEFT JOIN weight ON laptops.weight_id = weight.id
            WHERE laptops.id = {index};
        """)
        res = cur.fetchone()

        # print out both versions of the laptop
        print(f"""
        
        {laptop}
        {res}

        """)
    
    # :)
    print("done (:")
