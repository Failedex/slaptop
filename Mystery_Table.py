import enum
import sqlite3 as sql
import csv

# connecting sql 
conn = sql.connect("Mystery.csv")
cur = conn.cursor()

def createtable():

    #make table
    cur.executescript("""
        DROP TABLE mystery;
        DROP TABLE gender;
        DROP TABLE color;
        DROP TABLE height;
        DROP TABLE build;
    
        CREATE TABLE mystery (
            id int,
            name varchar(20),
            gender_id int,
            hair_color_id int,
            eye_color_id int,
            height_id int, 
            build_id int,
            glasses bit
        );

        CREATE TABLE color (
            id int,
            color_name varchar(10)
        );

        CREATE TABLE height (
            id int,
            height_size varchar(10)
        );

        CREATE TABLE build (
            id int,
            build_type varchar(10)            
        );

        CREATE TABLE gender (
            id int, 
            gender_name varchar(10)
        );
    """)

    gender = {
        "Male": 1,
        "Female": 2
    }

    for gend, id in gender.items():
        cur.execute(f"INSERT INTO gender VALUES ({id}, '{gend}')")
    
    color = {
        "Black": 1,
        "Blonde": 2,
        "Red": 3,
        "Brown": 4,
        "Blue": 5,
        "Green": 6
    }

    for colo, id in color.items():
        cur.execute(f"INSERT INTO color VALUES ({id}, '{colo}')")

    height = {
        "Short": 1, 
        "Average": 2,
        "Tall": 3
    }

    for heigh, id in height.items():
        cur.execute(f"INSERT INTO height VALUES ({id}, '{heigh}')")

    build = {
        "Small": 1, 
        "Medium": 2,
        "Large": 3
    }

    for buil, id in build.items():
        cur.execute(f"INSERT INTO build VALUES ({id}, '{buil}')")

    # read csv and put in sql db AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

    with open("Mystery_Table_data.csv", "r") as f:
        people = csv.reader(f, delimiter = ",")
        for person in people:
            cur.execute(f'''
                INSERT INTO mystery VALUES ({person[0]}, "{person[1]}", {gender[person[2]]}, {color[person[3]]}, {color[person[4]]}, {height[person[5]]}, {build[person[6]]}, {person[7]})
            ''')

    conn.commit()

def viewtable():
    cur.execute("SELECT * FROM mystery")
    print(cur.fetchall())

# literally main code
def main():
    createtable()

    hair = input("hair: ").title()
    height = input("height: ").title()
    gender = input("gender: ").title()
    eye = input("eye color: ").title()
    build = input("build: ").title()

    iddata = [] 
    cur.execute("select id from color where color_name = 'Brown'", (hair, ))
    iddata.append(cur.fetchone())
    cur.execute("select id from height where height_size = 'Short'", (height, ))
    iddata.append(cur.fetchone())
    cur.execute("select id from gender where gender_name = 'Female'", (gender, ))
    iddata.append(cur.fetchone())
    cur.execute("select id from color where color_name = 'Green'", (eye, ))
    iddata.append(cur.fetchone())
    cur.execute("select id from build where build_type = ?", (build,))
    iddata.append(cur.fetchone())
    print(iddata)

    cur.execute("SELECT * FROM mystery WHERE glasses = 1 and hair_color_id = ? and height_id = ? and gender_id = ? and eye_color_id = ? and build_id", (iddata[0][0], iddata[1][0], iddata[2][0], iddata[3][0], iddata[4][0]))
    print(cur.fetchall())

    # input stuff ig
    # sin(5^3125)
    
    

if __name__ == "__main__":
    main()