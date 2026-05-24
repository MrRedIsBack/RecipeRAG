import chainlit as cl
import real_ladybug as lb
from thefuzz import process

# --- Database Setup ---
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

# --- Utility Functions (Adapted for Chainlit) ---
def convert_data_type(data_type: str):
    data_type = data_type.lower()
    match data_type:
        case ("int8", "int16", "int32", "int64", "int128", "uint8", "uint16", "uint32", "uint64"):
            return int
        case ("float", "double", "decimal"):
            return float
        case "boolean":
            return bool
        case ("string", "interval"):
            return str
        case _:
            return str

async def get_database_info() -> tuple[list[str], list[str]]:
    current_tables = conn.execute("CALL show_tables() RETURN *")
    existing_nodes = []
    existing_relations = []
    
    while current_tables.has_next():
        table_row = current_tables.get_next()
        table_name = table_row[1]
        table_type = table_row[2]

        if table_type == "NODE":
            existing_nodes.append(table_name)
        elif table_type == "REL":
            existing_relations.append(table_name)

    await cl.Message(f"Existing Nodes:\n{existing_nodes}\nExisting Relations:\n{existing_relations}").send()
    return existing_nodes, existing_relations

async def select_node(existing_nodes, custom_message: str) -> str | None:
    nodes_list = "\n".join([f" - {node}" for node in existing_nodes])
    prompt = f"The following node tables are available:\n{nodes_list}\n\n{custom_message}"
    
    res = await cl.AskUserMessage(content=prompt).send()
    if not res: return None
    edit_node = res["output"]

    if edit_node.lower() == "none":
        return None

    match = process.extract(edit_node, existing_nodes, limit=1)
    if not match: return None
    most_similar_node, similarity_score = match[0][0], match[0][1]

    if similarity_score == 100:
        return most_similar_node

    res = await cl.AskUserMessage(content=f"Did you mean {most_similar_node}? Type y/n to confirm.").send()
    if not res: return None
    correct_node = res["output"]

    if correct_node.lower() in ["y", "yes"]:
        return most_similar_node
    else:
        await cl.Message("Please type the name of the node again:").send()
        return await select_node(existing_nodes, custom_message)

async def create_node(node_name: str, parameters: dict):
    props_cypher = ", ".join([f"{key}: ${key}" for key in parameters.keys()])
    query = f"CREATE (n:{node_name} {{{props_cypher}}})"
    
    await cl.Message(f"Generated query: {query}\nWith parameters: {parameters}").send()
    
    try:
        conn.execute(query, parameters=parameters)
        await cl.Message(f"Node '{node_name}' created successfully!").send()
    except Exception as e:
        await cl.Message(f"An error occurred while creating the node: {e}").send()

async def print_node_data(node: str):
    query = f"MATCH (n:{node}) RETURN n"
    results = conn.execute(query)
    
    if not results.has_next():
        await cl.Message(f"No nodes found in the {node} table.").send()
        return

    node_count = 1
    output = []
    
    while results.has_next():
        row = results.get_next()
        n = row[0] 
        output.append(f"\n**--- Node {node_count} ---**")
        for key, value in n.items():
            if not key.startswith("_"):
                output.append(f"{key}: {value}")
        node_count += 1
        
    await cl.Message("\n".join(output)).send()

async def print_all_relationships():
    query = "MATCH (src)-[r]->(dst) RETURN src, label(r) AS rel_type, dst"
    results = conn.execute(query)
    
    if not results.has_next():
        await cl.Message("No relationships found.").send()
        return

    output = []
    while results.has_next():
        row = results.get_next()
        src_node = row[0]
        rel_type = row[1] 
        dst_node = row[2]
        
        src_name = src_node.get("name", f"Node({src_node.get('_id')})")
        dst_name = dst_node.get("name", f"Node({dst_node.get('_id')})")
        
        output.append(f"({src_name}) ------> [{rel_type}] ------> ({dst_name})")
        
    if output:
        await cl.Message("\n".join(output)).send()