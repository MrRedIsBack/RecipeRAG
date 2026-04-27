def main():
    while True:
        try:
            choice = int(input("What would you like to do? \n 1) Edit the database \n 2) View the database \n 3) Exit \n"))
            
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == 1:
            print("Editing the database...")
            # Code to edit the database goes here

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