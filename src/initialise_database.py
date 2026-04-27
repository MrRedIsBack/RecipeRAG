import real_ladybug as lb

#The locations for the node databases (which will include the relationships)
recipe_csv="./data/recipe.csv"
cuisine_csv="./data/cuisine.csv"
main_ingredient_csv="./data/main-ingredient.csv"
diet_tag_csv="./data/diet-tag.csv"

def main():
    # Create an empty on-disk database and connect to it
    db = lb.Database("recipe_database.lbug")
    conn = lb.Connection(db)

    # Create schema
    conn.execute("CREATE NODE TABLE RECIPE(name STRING PRIMARY KEY, description STRING, ingredients STRING, instructions STRING, total_time INT64, cost INT64, rating FLOAT8)")
    conn.execute("CREATE NODE TABLE CUISINE(name STRING PRIMARY KEY, region STRING)")
    conn.execute("CREATE NODE TABLE MAIN_INGREDIENT(name STRING PRIMARY KEY, category STRING, protein_per_100g FLOAT8, carbs_per_100g FLOAT8, fat_per_100g FLOAT8, calories_per_100g FLOAT8)")
    conn.execute("CREATE NODE TABLE DIET_TAG(name STRING PRIMARY KEY)")
    conn.execute("CREATE REL TABLE contains(FROM RECIPE TO MAIN_INGREDIENT)")
    conn.execute("CREATE REL TABLE belongs_to(FROM RECIPE TO CUISINE)")
    conn.execute("CREATE REL TABLE has_tag(FROM RECIPE TO DIET_TAG)")
    conn.execute("CREATE REL TABLE pairs_with(FROM MAIN_INGREDIENT TO MAIN_INGREDIENT)")
    conn.execute("CREATE REL TABLE similar_to(FROM RECIPE TO RECIPE)")

    # Insert data
    #conn.execute(f"COPY RECIPE(name, description, ingredients, instructions, total_time, cost, rating, contains, belongs_to, has_tag, similar_to) FROM '{recipe_csv}' WITH (FORMAT CSV, HEADER TRUE);")
    #conn.execute(f"COPY CUISINE(name, region) FROM '{cuisine_csv}' WITH (FORMAT CSV, HEADER TRUE);")
    #conn.execute(f"COPY MAIN_INGREDIENT(name, category, protein_per_100g, carbs_per_100g, fat_per_100g, calories_per_100g, pairs_with) FROM '{main_ingredient_csv}' WITH (FORMAT CSV, HEADER TRUE);")
    #conn.execute(f"COPY DIET_TAG(name) FROM '{diet_tag_csv}' WITH (FORMAT CSV, HEADER TRUE);")

    conn.execute(f"""
        COPY RECIPE FROM "{recipe_csv}" (HEADER=TRUE);
    """)

    conn.execute(f"""
        Copy CUISINE FROM (
                 LOAD FROM "{cuisine_csv}" (HEADER=TRUE, FORMAT=CSV)
                 Return name, region
                 )
                 """)
    conn.execute(f"""
        Copy MAIN_INGREDIENT FROM (
                 LOAD FROM "{main_ingredient_csv}" (HEADER=TRUE, FORMAT=CSV)
                 Return name, category, protein_per_100g, carbs_per_100g, fat_per_100g, calories_per_100g, pairs_with
                 )
                 """)
    conn.execute(f"""
        Copy DIET_TAG FROM (
                 LOAD FROM "{diet_tag_csv}" (HEADER=TRUE, FORMAT=CSV)
                 Return name
                 )
                 """)

    # Execute Cypher query
    response = conn.execute(
        """
        MATCH (a:RECIPE)-[f:similar_to]->(b:RECIPE)
        RETURN a.name, b.name;
        """
    )
    for row in response:
        print(row)

if __name__ == "__main__":
    main()