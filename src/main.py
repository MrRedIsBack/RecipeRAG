import real_ladybug as lb

import os

import csv

nodes_path = "./data/node/"
relations_path = "./data/relation/"

def main():
    while True:
        try:
            choice = int(input("What would you like to do? \n 1) Edit the database \n 2) View the database \n 3) Exit \n"))
            
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == 1:
            print("Editing the database...")

            #Grab all the files in the node path
            files_list = os.listdir(nodes_path)
            nodes_list = []

            #Only add files that end with csv, although no other files should be in there
            for file in files_list:
                if file.endswith(".csv"):
                    nodes_list.append(file[:-4:])

            #First, print the available node tables and ask the user which one they want to edit
            print("The following node tables are available: ")
            for node in nodes_list:
                print(f" - {node}")
            edit_node = str(input("Which node table would you like to edit? Type None to go to edit the edges instead. \n"))

            if edit_node.lower() == "none":
                pass

            ### This currently goes back to the main menu, but I want it to instead go back to the edit_node = str(input())
            elif edit_node.lower() not in nodes_list:
                print("Invalid node table selected.")
                continue

            else:
                print(f"Editing the {edit_node} node table...")
                file = os.path.join(nodes_path,edit_node+".csv")
                
                # We are going to get the last id to make sure we have unique ids
                # We are also getting the header names so we can loop through them and ask the user for the relevant information
                with open(file, mode='r') as csv_file:

                    headers = csv_file.readline().strip().split(",")
                    #headers = headers[] # Skip the first column as that is the primary key and should not be edited

                    print(headers)

                    try:
                        last_id = int(csv_file.readlines()[-1].strip().split(",")[0])

                    except ValueError:
                        print("Something went wrong with reading the last id. Please check the csv file and make sure it is formatted correctly.")
                        print("Setting last_id to 1 in case the csv is just empty.")
                        last_id = 1

                ### Massive issue with data types
                print("Please enter the following information: ")
                new_entry = [str(int(last_id)+1)]
                print(headers)
                for header in headers[1:]:
                    value = input(f"{header}: ")
                    new_entry.append(value)

                print(f"New entry: {new_entry}")

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