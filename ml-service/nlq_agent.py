import os
import pandas as pd
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

# Initialize Global Agent
AGENT = None

def get_agent():
    global AGENT
    if AGENT:
        return AGENT
    
    # Database Connection Confirmation
    # Default to local SQLite mock DB, but ready for Oracle via Env Var
    # For Oracle: export DATABASE_URL="oracle+oracledb://user:password@host:port/service_name"
    db_uri = os.environ.get("DATABASE_URL", "sqlite:///mock_data.db")
    
    # Check if using default SQLite and file exists
    if db_uri.startswith("sqlite"):
        db_path = db_uri.replace("sqlite:///", "")
        if not os.path.exists(db_path):
             print(f"⚠️  Database file not found at {db_path}")
             return None

    try:
        # Connect to Database (Supports SQLite, Oracle, PostgreSQL, etc.)
        db = SQLDatabase.from_uri(db_uri)
        
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        # Create SQL Agent
        AGENT = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="openai-tools",
            verbose=True,
            agent_executor_kwargs={"return_intermediate_steps": True}
        )
        print("✅ NLQ SQL Agent initialized")
        return AGENT
    except Exception as e:
        print(f"⚠️ Failed to init NLQ SQL Agent: {e}")
        return None

def query_csv_agent(question: str):
    """
    Executes the agent and extracts SQL + Logs from intermediate steps.
    """
    agent = get_agent()
    if not agent:
        return {"error": "Agent not initialized"}
    
    try:
        # Invoke agent
        result = agent.invoke({"input": question})
        
        # Extract Output
        answer = result.get("output", "")
        steps = result.get("intermediate_steps", [])
        
        # Parse logic for SQL and Logs
        generated_sql = ""
        logs = []
        
        for idx, (action, observation) in enumerate(steps):
            # Action: Tool usage
            log_entry = {
                "step": f"step_{idx+1}",
                "tool": action.tool,
                "tool_input": str(action.tool_input),
                "log": action.log
            }
            logs.append(log_entry)
            
            # Capture SQL if the tool is sql_db_query
            if action.tool == "sql_db_query":
                # tool_input might be a string query or a dict depending on agent version
                if isinstance(action.tool_input, dict):
                     generated_sql = action.tool_input.get("query", str(action.tool_input))
                else:
                     generated_sql = str(action.tool_input)

        # Output Structured Data (Columns/Rows) if SQL was generated
        columns = []
        rows = []
        if generated_sql:
            try:
                # Clean SQL (remove markdown backticks if present)
                clean_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
                
                # Execute against DB to get raw data
                with sqlite3.connect("mock_data.db") as conn:
                    df = pd.read_sql(clean_sql, conn)
                    columns = df.columns.tolist()
                    rows = df.to_dict(orient="records")
            except Exception as e:
                print(f"⚠️ Failed to execute generated SQL for data preview: {e}")

        return {
            "answer": answer,
            "sql": generated_sql, 
            "logs": logs,
            "columns": columns,
            "rows": rows
        }
    except Exception as e:
        return {"error": str(e)}
