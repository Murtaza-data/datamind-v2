import os
import psycopg2
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()                                 


def get_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )      

mcp = FastMCP("datamind")



@mcp.tool()
def get_schema() -> str:
    """Return all tables and their columns in the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    schema = {}
    for table, col in rows:
        schema.setdefault(table, []).append(col)
    return "".join(f"Table {t}: {', '.join(c)}\n" for t, c in schema.items())

@mcp.tool()
def run_sql(query: str) -> str:
    """Run a read-only SQL query on the database and return the result."""
    q = query.strip().lower()
    if not q.startswith("select"):
        return "BLOCKED: Only SELECT (read-only) queries are allowed."
    if any(word in q for word in ["users", "password", "query_history"]):
        return "BLOCKED: Access to sensitive tables is not allowed."
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return str(rows)
    except Exception as e:
        conn.rollback(); cur.close(); conn.close()
        return f"ERROR: {e}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")