import chainlit as cl
import uuid
from utils import *

# --- Main Application Loop ---
@cl.on_chat_start
async def main():
    while True:
        res = await cl.AskUserMessage(
            content="What would you like to do? \n 1) Edit the database \n 2) Add a new node or relationship \n 3) View the database \n 4) Exit"
        ).send()
        
        print(res)

        if not res: 
            break
            
        try:
            choice = int(res["output"])
        except ValueError:
            await cl.Message("Invalid input. Please enter a number.").send()
            continue

        if choice == 1:
            await cl.Message("Editing the database...").send()
            # Code to edit the database goes here

        elif choice == 2:
            await cl.Message("Adding a new node or relationship...").send()

            existing_nodes, existing_relations = await get_database_info()

            edit_node = await select_node(existing_nodes, "Which node table would you like to edit? Type None to go to edit the edges instead.")
            if not edit_node:
                continue

            # Need to use the conn object from utils
            schema_info = conn.execute(f"CALL TABLE_INFO('{edit_node}') RETURN *")

            parameters = {}
            input_parameters = {}
            param_outputs = []

            while schema_info.has_next():
                parameter = schema_info.get_next()
                parameter_name = parameter[1]
                parameter_data_type = parameter[2]

                parameters[parameter_name] = parameter_data_type
                param_outputs.append(f"Parameter Name: {parameter_name}, Parameter Type: {parameter_data_type}")

            await cl.Message("\n".join(param_outputs)).send()
            await cl.Message(f"{parameters}").send()

            parameters_iterator = iter(parameters.items())
            new_node_id = str(uuid.uuid4())
            id_key, _ = next(parameters_iterator, (None, None))
            
            if id_key:
                input_parameters[id_key] = new_node_id

            for name, data_type in parameters_iterator:
                res = await cl.AskUserMessage(content=f"Enter a new value for {name} (current data type: {data_type}):").send()
                if not res: continue
                new_value = res["output"]

                converted_type = convert_data_type(data_type).__name__ if hasattr(convert_data_type(data_type), '__name__') else "str"
                await cl.Message(f"Data Type: {data_type}, Converted Type: {converted_type}").send()
                    
                match converted_type:
                    case "int":
                        try:
                            new_value = int(new_value)
                            lower_bound = int_bounds[data_type.lower()][0]
                            upper_bound = int_bounds[data_type.lower()][1]

                            if new_value < lower_bound or new_value > upper_bound:
                                await cl.Message(f"Value out of bounds. Expected a value between {lower_bound} and {upper_bound}. Please try again.").send()
                                break
                        except ValueError:
                            await cl.Message(f"Invalid value for {name}. Expected an integer.").send()
                            break

                        input_parameters[name] = new_value

                    case "float":
                        try:
                            new_value = float(new_value)
                            input_parameters[name] = new_value
                        except ValueError:
                            await cl.Message(f"Invalid value for {name}. Expected a float.").send()
                            break

                    case "str":
                        input_parameters[name] = new_value

            confirm_res = await cl.AskUserMessage(content="Do you want to add this to the database? Type y/n to confirm.").send()
            if not confirm_res: continue
            confirm = confirm_res["output"]

            if confirm.lower() in ["y", "yes"]:
                await cl.Message("Adding to the database...").send()
                await create_node(edit_node, input_parameters)
            else:
                await cl.Message("Aborting. Returning to main menu...").send()
                continue

        elif choice == 3:
            await cl.Message("Viewing the database...").send()

            existing_nodes, _ = await get_database_info()

            for node in existing_nodes:
                await cl.Message(f"**--- Data for {node} ---**").send()
                await print_node_data(node)

            await print_all_relationships()

        elif choice == 4:
            await cl.Message("Exiting the program... (Session Ended)").send()
            break

        else:
            await cl.Message("Invalid choice. Please try again.").send()