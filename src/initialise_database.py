import real_ladybug as lb

#The locations for the node databases
recipe_csv="./data/node/recipe.csv"
cuisine_csv="./data/node/cuisine.csv"
main_ingredient_csv="./data/node/main_ingredient.csv"
diet_tag_csv="./data/node/diet_tag.csv"

#The locations for the relationship databases
contains_csv="./data/relation/contains.csv"
belongs_to_csv="./data/relation/belongs_to.csv"
has_tag_csv="./data/relation/has_tag.csv"
similar_to_csv="./data/relation/similar_to.csv"
pairs_with_csv="./data/relation/pairs_with.csv"

def main():
    # Create an empty on-disk database and connect to it
    db=lb.Database("recipe_database.lbug")
    conn=lb.Connection(db)

    #Create the Node tables
    conn.execute("""
        CREATE NODE TABLE Recipe (
            recipe_id INT32 PRIMARY KEY,
            name STRING,
            description STRING,
            ingredients STRING,
            instructions STRING,
            total_time INTERVAL,
            cost DOUBLE,
            rating INT8,
            date_added TIMESTAMP
        )""")
    conn.execute("""
        CREATE NODE TABLE Cuisine (
            cuisine_id INT16 PRIMARY KEY,
            name STRING,
            region STRING
        )""")
    conn.execute("""
        CREATE NODE TABLE Main_Ingredient (
            ingredient_id INT16 PRIMARY KEY,
            name STRING,
            category STRING,
            protein_per_100g DOUBLE,
            carbs_per_100g DOUBLE,
            fat_per_100g DOUBLE,
            calories_per_100g DOUBLE
        )""")
    conn.execute("""
        CREATE NODE TABLE Diet_Tag (
            diet_id INT16 PRIMARY KEY,
            name STRING
        )""")

    #Create the Relationship tables
    conn.execute("""
        CREATE REL TABLE CONTAINS (
            FROM Recipe TO Main_Ingredient
        )""")
    conn.execute("""
        CREATE REL TABLE BELONGS_TO (
            FROM Recipe TO Cuisine
        )""")
    conn.execute("""
        CREATE REL TABLE HAS_TAG (
            FROM Recipe TO Diet_Tag
        )""")
    conn.execute("""
        CREATE REL TABLE SIMILAR_TO (
            FROM Recipe TO Recipe
        )""")
    conn.execute("""
        CREATE REL TABLE PAIRS_WITH (
            FROM Main_Ingredient TO Main_Ingredient
        )""")
    
    #Copy the data from the CSV files into the respective tables
    conn.execute(f"COPY Recipe FROM '{recipe_csv}'")
    conn.execute(f"COPY Cuisine FROM '{cuisine_csv}'")
    conn.execute(f"COPY Main_Ingredient FROM '{main_ingredient_csv}'")
    conn.execute(f"COPY Diet_Tag FROM '{diet_tag_csv}'")
    conn.execute(f"COPY CONTAINS FROM '{contains_csv}'")
    conn.execute(f"COPY BELONGS_TO FROM '{belongs_to_csv}'")
    conn.execute(f"COPY HAS_TAG FROM '{has_tag_csv}'")
    conn.execute(f"COPY SIMILAR_TO FROM '{similar_to_csv}'")
    conn.execute(f"COPY PAIRS_WITH FROM '{pairs_with_csv}'")

if __name__ == "__main__":
    main()