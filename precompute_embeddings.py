import openai ,os
import MySQLdb
from sqlalchemy import create_engine ,text
import json

# Ensure openai.api_key is set
openai.api_key = os.getenv("OPENAI_API_KEY")

password = os.getenv("PA")
# Connect to the databas
engine = create_engine("mysql+mysqlconnector://root:W7301%40jqir%23@127.0.0.1:3306/library_management_system")

def generate_embeddings(text_input):
    if not isinstance(text_input, str):
        raise ValueError("Expected a string for text_input, got a non-string type.")

    response = openai.Embedding.create(input=text_input, model="text-embedding-ada-002")
    return response['data'][0]['embedding']


# Connect to the database and process books
with engine.connect() as connection:
    # Start a transaction
    with connection.begin() as transaction:
        # Fetch books from the database using text()
        results = connection.execute(text("SELECT id, title, author FROM add_book")).fetchall()

        # Generate and store embeddings
        for book in results:
            book_id = book[0]  # Access by index if results are tuples
            title = book[1]
            author = book[2]
            text_input = f"{title} {author}"
            embedding = generate_embeddings(text_input)

            # Convert the embedding list to JSON (an array in JSON format)
            embedding_json = json.dumps(embedding)

            # Store embedding in the database as JSON using a parameterized query
            connection.execute(
                text("UPDATE add_book SET embedding = :embedding WHERE id = :id"),
                {"embedding": embedding_json, "id": book_id}
            )

        # Commit the transaction to save changes
        transaction.commit()

print("Embeddings generated and stored successfully.")
