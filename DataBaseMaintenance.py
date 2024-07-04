import sqlite3
import math


# creation of the DroneData Database
def create_database():
    # Connect to SQLite database (it will create the database file if it doesn't exist)
    connection = sqlite3.connect('DroneData.db')

    # Create a cursor object using the cursor() method
    cursor = connection.cursor()

    # Create a table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Drones (
        id TEXT NOT NULL,
        Make TEXT NOT NULL,
        Model TEXT NOT NULL,
        Type INTEGER,
        cd FLOAT,
        Mtom FLOAT,
        MaxSpeed FLOAT,
        AscentSpeed FLOAT,
        DescentSpeed FLOAT,
        Length FLOAT,
        Width FLOAT,
        Height FLOAT,
        Ekin FLOAT
    )
    ''')

    # Commit your changes in the database
    connection.commit()

    # Close the connection
    connection.close()


# collect information and create a list for the drone that can be put into the database
def drone_list():
    # collect all relevant data for the SORA process on the drone from the user
    identifier = drone_identifier()
    make = input("Manufacturer: ")
    model = input("Model: ")
    typ = options("Type of drone: Rotarywing - 1 / Multicopter - 2 / Fixedwing - 3 / Hybrid - 4: ", 4)
    cd = get_float("Characteristic Dimension [m]: ")
    maxspeed = get_float("Maximum speed (in sport mode, if available) [m/s]: ")
    mtom = get_float("Maximum take-off mass [kg]: ")
    ascentspeed = get_float("Ascent speed [m/s]: ")
    descentspeed = get_float("Descent speed [m/s]: ")
    length = get_float("Length [m]: ")
    width = get_float("Width [m]: ")
    height = get_float("Height [m]: ")
    ekin = calculate_ekin(typ, cd, mtom, maxspeed)
    # create a list with all relevant data to pass on to the next functions
    drone_data = [identifier, make, model, typ, cd, mtom, maxspeed, ascentspeed, descentspeed, length, width, height,
                  ekin]
    return drone_data


# define a unique identifier with the length of 4 characters for the drone
def drone_identifier():
    while True:
        identifier = input("Identifier (4 characters): ")
        # check the length of the identifier
        if len(identifier) == 4:
            break
        else:
            print("invalid identifiert. The identifier must be exaclty 4 characters long")
    # check whether the identifier already exists in the database
    check_identifier(identifier)
    return identifier


# query to the database to see whether the same identifier was used before.
def check_identifier(identifier):
    # connecting to the database and definition of the cursor
    conn = sqlite3.connect("DroneData.db")
    cursor = conn.cursor()
    # check whether the same ID already exists
    cursor.execute("SELECT * FROM Drones WHERE id = ?", (identifier,))
    existing_id = cursor.fetchone()
    if existing_id is None:
        return identifier
    else:
        print("This ID is already taken, please select another one")
        drone_identifier()


# function to present the user with a certain amount of choices and validating the result of the choice
def options(question, choices):
    while True:
        category = input(question)  # asking the user to choose from an array of options
        try:
            category_int = int(category)  # validate whether the option chosen is a valid one
            if 1 <= category_int <= choices:
                break
            else:
                print("Invalid Input")
        except ValueError:
            print("Invalid Input")
    return category_int


# function to collect a float from the user and round it two a maximum of two decimals.
def get_float(aspect):
    while True:
        var = input(aspect)
        try:
            var_float = round(float(var), 2)
            break
        except ValueError:
            print("Invalid input. Use a decimal number.")
    return var_float


# calculate the Kinetic Energy of the drone based on the FOCA formulas
def calculate_ekin(typ, cd, mtom, maxspeed):
    a = (cd * 0.5) ** 2 * math.pi * 0.3  # definition of the multicopter area
    drag = 0.8  # Dragcoefficient for Multicopter
    g = 9.81  # m/s2
    roh = 1.225  # kg/m3 Density of the air at sealevel
    # terminal velocity for multicopter or rotary wing aircraft
    if typ == 1 or 2:
        vterminal = math.sqrt((2 * mtom * g) / (drag * a * roh))
    # terminal velocity for fixed wing aircraft
    elif typ == 3:
        vterminal = maxspeed
    else:
        print("This type of aircraft is not yet available")

    ekin = round((0.5 * mtom * vterminal ** 2) / 1000, 2)  # calculates the kinetic energy in kJ
    return ekin


# updating the DroneData Database
def update_db(drone_data):

    # Connect to SQLite database
    connection = sqlite3.connect('DroneData.db')

    # Create a cursor object
    cursor = connection.cursor()

    # Insert a single row of data
    cursor.execute('''
    INSERT INTO Drones (id, Make, Model, Type, Cd, Mtom, MaxSpeed, AscentSpeed, DescentSpeed, Length, Width, Height, 
    Ekin)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', drone_data)

    # Commit your changes
    connection.commit()

    # Close the connection
    connection.close()


# show the table "Drones" of the database to check what the content is so far.
def show_table():
    # connect to the DB
    connection = sqlite3.connect('DroneData.db')
    cursor = connection.cursor()

    # Execute SQL query to fetch data from the table
    cursor.execute("SELECT * FROM Drones;")
    rows = cursor.fetchall()

    # Print the table into the console
    for row in rows:
        print(row)


def main():
    drone_data = drone_list()
    update_db(drone_data)


create_database()
main()
show_table()
