import real_ladybug as lb

from sqlalchemy import case
from thefuzz import process

import uuid

from utils import *

int_bounds = {
    "int8": (-128, 127),
    "int16": (-32768, 32767),
    "int32": (-2147483648, 2147483647),
    "int64": (-9223372036854775808, 9223372036854775807),
    "int128": (-170141183460469231731687303715884105728, 170141183460469231731687303715884105727),
    "uint8": (0, 255),
    "uint16": (0, 65535),
    "uint32": (0, 4294967295),
    "uint64": (0, 18446744073709551615)
}

def main():
    while True:
        try:
            choice = int(input("What would you like to do? \n 1) Edit the database \n 2) Add a new node or relationship \n 3) View the database \n 4) Exit \n"))
            
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == 1:
            print("Editing the database...")
            # Code to edit the database goes here

        elif choice == 2:
            print("Adding a new node or relationship...")

            existing_nodes, existing_relations = get_database_info()

            edit_node = select_node(existing_nodes, "Which node table would you like to edit? Type None to go to edit the edges instead. \n")

            schema_info = conn.execute(f"CALL TABLE_INFO('{edit_node}') RETURN *")

            #Create a dictionary to store the column names and their data types
            parameters = {}
            input_parameters = {}

            while schema_info.has_next():
                parameter = schema_info.get_next()
                parameter_name = parameter[1]
                parameter_data_type = parameter[2]

                parameters[parameter_name] = parameter_data_type

                print(f"Parameter Name: {parameter_name}, Parameter Type: {parameter_data_type}")

            print(parameters)

            parameters_iterator = iter(parameters.items())

            # Create a new UUID for the new node and add it to the input parameters with the correct parameter name (the first parameter in the schema, which should always be the ID)
            new_node_id = str(uuid.uuid4())

            id, _ = next(parameters_iterator, None)

            input_parameters[f"{id}"] = new_node_id

            for name, data_type in parameters_iterator:
                new_value = input(f"Enter a new value for {name} (current data type: {data_type}): ")

                # Convert the new value to the correct data type based on the schema information
                converted_type = convert_data_type(data_type).__name__

                print(f"Data Type: {data_type}, Converted Type: {converted_type}")
                    
                match converted_type:
                    case "int":
                        try:
                            new_value = int(new_value)

                            lower_bound = int_bounds[data_type.lower()][0]
                            upper_bound = int_bounds[data_type.lower()][1]

                            if new_value < lower_bound or new_value > upper_bound:
                                print(f"Value out of bounds. Expected a value between {lower_bound} and {upper_bound}. Please try again.")
                                break

                        except ValueError:
                            print(f"Invalid value for {parameter_name}. Expected an integer.")
                            break

                        input_parameters[name] = new_value

                    case "float":
                        new_value = float(new_value)
                        input_parameters[name] = new_value

                    case "str":
                        input_parameters[name] = new_value

            confirm = str(input("Do you want to add this to the database? Type y/n to confirm. \n"))

            if confirm.lower() == "y" or confirm.lower() == "yes":
                print("Adding to the database...")
                create_node(edit_node, input_parameters)

            else:
                print("Aborting. Returning to main menu...")
                continue

        elif choice == 3:
            print("Viewing the database...")

            existing_nodes, _ = get_database_info()

            for node in existing_nodes:
                print(f"\n\n--- Data for {node} ---")
                print_node_data(node)

            print_all_relationships()

        elif choice == 4:
            print("Exiting the program...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()