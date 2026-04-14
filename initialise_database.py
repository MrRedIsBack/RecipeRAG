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
    conn.execute("CREATE NODE TABLE RECIPE(name STRING PRIMARY KEY, description STRING, ingredients_text STRING, instructions_text STRING, total_time INT64, cost INT64, rating FLOAT64)")
    conn.execute("CREATE NODE TABLE CUISINE(name STRING PRIMARY KEY, region STRING)")
    conn.execute("CREATE NODE TABLE MAIN_INGREDIENT(name STRING PRIMARY KEY, category STRING, protein_per_100g FLOAT64, carbs_per_100g FLOAT64, fat_per_100g FLOAT64, carbs_per_100g FLOAT64, fat_per_100g FLOAT64, calories_per_100g FLOAT64)")
    conn.execute("CREATE NODE TABLE DIET_TAG(name STRING PRIMARY KEY)")
    conn.execute("CREATE REL TABLE contains(FROM RECIPE TO MAIN_INGREDIENT)")
    conn.execute("CREATE REL TABLE belongs_to(FROM RECIPE TO CUISINE)")
    conn.execute("CREATE REL TABLE has_tag(FROM RECIPE TO DIET_TAG)")
    conn.execute("CREATE REL TABLE pairs_with(FROM MAIN_INGREDIENT TO MAIN_INGREDIENT)")
    conn.execute("CREATE REL TABLE similar_to(FROM RECIPE TO RECIPE)")

    # Insert data
    conn.execute(f"COPY RECIPE FROM {recipe_csv}")
    conn.execute(f"COPY CUISINE FROM {cuisine_csv}")
    conn.execute(f"COPY MAIN_INGREDIENT FROM {main_ingredient_csv}")
    conn.execute(f"COPY DIET_TAG FROM {diet_tag_csv}")

    # Execute Cypher query
    response = conn.execute(
        """
        MATCH (a:User)-[f:Follows]->(b:User)
        RETURN a.name, b.name, f.since;
        """
    )
    for row in response:
        print(row)

if __name__ == "__main__":
    main()