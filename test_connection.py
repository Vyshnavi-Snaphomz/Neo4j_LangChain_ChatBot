import os
from neo4j import GraphDatabase
from getpass import getpass

def test_connection():
    """
    Tests the connection to a Neo4j database using user-provided credentials.
    """
    print("--- Neo4j Connection Test ---")
    
    # Check if inside a virtual environment
    if not os.getenv('VIRTUAL_ENV'):
        print("\nWARNING: You don't appear to be in a Python virtual environment.")
        print("Please activate your 'poc' environment before running this script.")
        print("You can do this with: .\poc\Scripts\Activate.ps1\n")

    uri = input("Enter your Neo4j URI (e.g., neo4j+s://xxxx.databases.neo4j.io): ")
    user = input("Enter your Neo4j username (default: neo4j): ")
    if not user:
        user = "neo4j"
    
    # Use getpass to securely ask for the password
    password = getpass("Enter your Neo4j password: ")

    if not all([uri, user, password]):
        print("\nERROR: URI, username, and password are required.")
        return

    driver = None
    try:
        print(f"\nAttempting to connect to '{uri}' with user '{user}'...")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print("\n✅ SUCCESS: Connection to Neo4j database was successful!")
        
        # Optional: Run a simple query
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful' AS message")
            record = result.single()
            print(f"   Query Result: {record['message']}")

    except Exception as e:
        print("\n❌ FAILED: Could not connect to Neo4j database.")
        print("\n--- Error Details ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print("\n--- Troubleshooting ---")
        print("1. Double-check your URI, username, and password.")
        print("2. For Aura, the URI must start with 'neo4j+s://'.")
        print("3. Ensure your database is running and not suspended.")
        print("4. Check if a firewall or antivirus program is blocking the connection to port 7687.")

    finally:
        if driver:
            driver.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    test_connection()
