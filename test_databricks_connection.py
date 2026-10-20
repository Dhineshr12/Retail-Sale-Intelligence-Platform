
import os
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
TOKEN = os.getenv("DATABRICKS_TOKEN")


def test_connection():
    if not all([SERVER_HOSTNAME, HTTP_PATH, TOKEN]):
        print("Missing Databricks settings in .env")
        return

    try:
        print("Connecting to Databricks using token authentication...")

        with sql.connect(
            server_hostname=SERVER_HOSTNAME,
            http_path=HTTP_PATH,
            access_token=TOKEN,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                print("Connection successful:", cursor.fetchone())

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM sales.salesschema.silver_superstore
                """)
                print("Silver table row count:", cursor.fetchone()[0])

    except Exception as error:
        print("Connection failed:", error)


if __name__ == "__main__":
    test_connection()



import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("DATABRICKS_TOKEN")

print("Token found:", bool(token))
print("Token length:", len(token) if token else 0)
print("Looks like traditional PAT:", token.startswith("dapi") if token else False)
