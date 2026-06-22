from database import engine

try:
    connection = engine.connect()
    print("Connected successfully to the database!")
    connection.close()
except Exception as e:
    print(f"Connection failed: {e}")
