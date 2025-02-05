import psycopg2
import os
from dotenv import load_dotenv



db_url = "postgresql://postgres:password@localhost:5432/trustwise_db"

try:
    print("Connecting to database...")

    conn = psycopg2.connect(db_url)
    print(conn)
    print("Connected to database successfully!")
    cur = conn.cursor()

    create_vectara_results_table_query = """
        CREATE TABLE vectara_results (
            prediction_id VARCHAR(36) PRIMARY KEY, 
            input_1 TEXT,
            input_2 TEXT,
            output_score FLOAT,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
            processing_time_ms INTEGER,
            status VARCHAR(20)
        );
    """

    create_gibberish_results_table_query = """
        CREATE TABLE gibberish_results (
            prediction_id VARCHAR(36) PRIMARY KEY, 
            input_text TEXT ,
            predicted_label VARCHAR(50),
            prob_clean FLOAT,
            prob_mild_gibberish FLOAT,
            prob_noise FLOAT,
            prob_word_salad FLOAT,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
            processing_time_ms INTEGER,
            status VARCHAR(20)
        );
    """
    cur.execute("DROP TABLE IF EXISTS vectara_results")
    cur.execute("DROP TABLE IF EXISTS gibberish_results")
    # Execute the queries to create the tables
    cur.execute(create_vectara_results_table_query)
    cur.execute(create_gibberish_results_table_query)
    
    #generate 5 synthetic entries for both tables
    # for i in range(5):
    #     input_1 = f"Input {i+1}"
    #     input_2 = f"Input {i+2}"
    #     output_score = random.uniform(0, 1)
    #     processing_time_ms = random.randint(100, 1000)
    #     status = "success"

    # Commit the changes to the database
    conn.commit()
    cur.close()
    conn.close()
    print("Tables 'vectara_results' and 'gibberish_results' created successfully!")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL or creating tables:", error)
