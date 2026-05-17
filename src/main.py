import real_ladybug as lb

from sqlalchemy import case
from thefuzz import process

import uuid

nodes_path = "./data/node/"
relations_path = "./data/relation/"

db = lb.Database("recipe_database.lbug")
conn = lb.Connection(db)

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

# Take the Ladybug data types and convert them to Python data types
# These should cover all the data types that should ever be used, but LadybugDB does support more
def convert_data_type(data_type: str):
    data_type = data_type.lower()

    if data_type in ["int8", "int16", "int32", "int64", "int128"]:
        return int
    
    elif data_type in ["uint8", "uint16", "uint32", "uint64"]:
        return int
    
    elif data_type in ["float", "double", "decimal"]:
        return float
    
    elif data_type == "boolean":
        return bool
    
    elif data_type == "string":
        return str
    
    elif data_type == "interval":
        return str
    
    else:
        return "Unknown data type"

# This function will take your input parameters and create a new node in the database with those parameters
def create_node(node_name: str, parameters: dict):
    # 1. Create a string of key-parameter pairs: "id: $id, name: $name"
    props_cypher = ", ".join([f"{key}: ${key}" for key in parameters.keys()])
    
    # 2. Inject it into the CREATE statement
    query = f"CREATE (n:{node_name} {{{props_cypher}}})"

    print(f"Generated query: {query}")
    print(f"With parameters: {parameters}")
    
    # 3. Execute the query, passing the original dictionary as the parameters
    try:
        conn.execute(query, parameters=parameters)
        print(f"Node '{node_name}' created with parameters: {parameters}")

    except Exception as e:
        print(f"An error occurred while creating the node: {e}")
    
# A function that gets all the nodes and relationships stored in the LadybugDB
def get_database_info() -> tuple[list[str], list[str]]:

    current_tables = conn.execute("CALL show_tables() RETURN *")

    existing_nodes = []
    existing_relations = []

    # Loop through the current tables in the database and categorise them as nodes or relations
    while current_tables.has_next():
        table_row = current_tables.get_next()
        table_name = table_row[1]
        table_type = table_row[2]

        if table_type == "NODE":
            existing_nodes.append(table_name)
        elif table_type == "REL":
            existing_relations.append(table_name)

    print("Existing Nodes:")
    print(existing_nodes)
    print("Existing Relations:")
    print(existing_relations)

    return existing_nodes, existing_relations

# Lets you select a node by typing a name and using the fuzz to find the most similar existing node
def select_node(existing_nodes, custom_message: str) -> str | None:

    # First, print the available node tables and ask the user which one they want to edit
    print("The following node tables are available: ")
    for node in existing_nodes:
        print(f" - {node}")

    edit_node = str(input(custom_message))

    if edit_node.lower() == "none":
        return None

    # Use the fuzz library to find the most similar existing node table to the user's input and suggest it to them
    most_similar_node = process.extract(edit_node, existing_nodes, limit=1)[0][0] #process.extract returns a list of tuples, where each tuple contains the matched string and its similarity score. We take the first tuple (the most similar match) and then take the first element of that tuple (the matched string) to get the most similar node table name
    similarity_score = process.extract(edit_node, existing_nodes, limit=1)[0][1]

    if similarity_score == 100:
        return most_similar_node

    correct_node = str(input(f"Did you mean {most_similar_node}? Type y/n to confirm. \n"))

    if correct_node.lower() == "y" or correct_node.lower() == "yes":
        edit_node = most_similar_node
        return edit_node
    
    else:
        print("Please type the name of the node again: ")
        return select_node(existing_nodes, custom_message)

# Given a node name, print all the values stored in that node table
def print_node_data(node: str) -> None:
    # 1. MATCH all nodes with the given label (no filters)
    query = f"MATCH (n:{node}) RETURN n"
    
    # 2. Execute the query
    results = conn.execute(query)
    
    # 3. Check if the table is empty
    if not results.has_next():
        print(f"No nodes found in the {node} table.")
        return

    node_count = 1
    
    # 4. Loop through every node returned
    while results.has_next():
        row = results.get_next()
        node = row[0] 
        
        print(f"\n--- Node {node_count} ---")
        for key, value in node.items():
            # Filter out internal keys like _ID and _LABEL
            if not key.startswith("_"):
                print(f"{key}: {value}")
                
        node_count += 1


def print_all_relationships() -> None:
    # Use label(r) to pull the actual relationship name right from the query
    query = "MATCH (src)-[r]->(dst) RETURN src, label(r) AS rel_type, dst"
    results = conn.execute(query)
    
    if not results.has_next():
        print("No relationships found.")
        return

    while results.has_next():
        row = results.get_next()
        src_node = row[0]
        rel_type = row[1]  # This is now just a clean string (e.g., 'WORKS_FOR')
        dst_node = row[2]
        
        src_name = src_node.get("name", f"Node({src_node.get('_id')})")
        dst_name = dst_node.get("name", f"Node({dst_node.get('_id')})")
        
        print(f"({src_name}) ------> [{rel_type}] ------> ({dst_name})")

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