import real_ladybug as lb

from thefuzz import process


nodes_path = "./data/node/"
relations_path = "./data/relation/"

db = lb.Database("recipe_database.lbug")
conn = lb.Connection(db)

def main():
    while True:
        try:
            choice = int(input("What would you like to do? \n 1) Edit the database \n 2) View the database \n 3) Exit \n"))
            
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == 1:
            print("Editing the database...")

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

            # First, print the available node tables and ask the user which one they want to edit
            print("The following node tables are available: ")
            for node in existing_nodes:
                print(f" - {node}")
            edit_node = str(input("Which node table would you like to edit? Type None to go to edit the edges instead. \n"))

            if edit_node.lower() == "none":
                pass

            # Use the fuzz library to find the most similar existing node table to the user's input and suggest it to them
            most_similar_node = process.extract(edit_node, existing_nodes, limit=1)[0][0] #process.extract returns a list of tuples, where each tuple contains the matched string and its similarity score. We take the first tuple (the most similar match) and then take the first element of that tuple (the matched string) to get the most similar node table name

            correct_node = str(input(f"Did you mean {most_similar_node}? Type y/n to confirm. \n"))

            if correct_node.lower() == "y" or correct_node.lower() == "yes":
                edit_node = most_similar_node

                schema_info = conn.execute(f"CALL TABLE_INFO('{edit_node}') RETURN *")

                #Create a dictionary to store the column names and their data types
                columns = {}

                while schema_info.has_next():
                    column_row = schema_info.get_next()
                    column_name = column_row[1]
                    column_data_type = column_row[2]

                    columns[column_name] = column_data_type

                    print(f"Column Name: {column_name}, Column Type: {column_data_type}")

                print(columns)

            else:
                print("No similar node table found. Please try again.")
                continue

        elif choice == 2:
            print("Viewing the database...")
            # Code to view the database goes here

        elif choice == 3:
            print("Exiting the program...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()