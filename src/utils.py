import real_ladybug as lb

db = lb.Database("recipe_database.lbug")
conn = lb.Connection(db)

# Take the Ladybug data types and convert them to Python data types
# These should cover all the data types that should ever be used, but LadybugDB does support more
def convert_data_type(data_type: str):
    data_type = data_type.lower()

    match data_type:

        case ("int8", "int16", "int32", "int64", "int128"):
            return int
        
        case ("uint8", "uint16", "uint32", "uint64"):
            return int
        
        case ("float", "double", "decimal"):
            return float
        
        case "boolean":
            return bool
        
        case "string":
            return str
        
        case "interval":
            return str
        
        case _:
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
