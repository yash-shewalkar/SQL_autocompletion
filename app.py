from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain_groq import ChatGroq
from services.config import GROQ_API_KEY

app = Flask(__name__)
CORS(app)

cached_schema = ""
def calculate_max_tokens(user_query):
    """Determine max tokens dynamically based on input length."""
    base_tokens = 50  # Minimum response length
    input_length = len(user_query.split())
    
    # Dynamic allocation based on user query length
    max_tokens = base_tokens + (input_length * 2)  # Adjust factor if needed

    return min(max_tokens, 200)  # Prevent exceeding model limits

def get_llm(max_tokens):
    """Dynamically set max_tokens based on input size."""
    return ChatGroq(
        model="qwen-2.5-coder-32b",
        temperature=0.1,
        max_tokens=max_tokens,  # Dynamically allocated tokens
        top_p=0.9,
        timeout=10,
        max_retries=3,
        groq_api_key=GROQ_API_KEY
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/suggest", methods=["POST"])
def suggest():
    global cached_schema
    data = request.json
    user_query = data.get("query", "").strip()
    schema = data.get("schema", "").strip()

    if schema and schema != cached_schema:
        cached_schema = schema  # Cache the schema to optimize processing

    if len(user_query.split()) > 3:
        max_tokens = calculate_max_tokens(user_query)  # Adjust dynamically
        prompt = f"""
        You are a SQL autocompletion assistant. Your task is to suggest a SQL query based on the provided schema and user input.
        You will be given a SQL schema and a user query. Your response should be a valid SQL query that completes the user input.
        assume that user is typing and you are its copilot and you are helping him to complete the query.
        You should not answer anything else. Do not add any extra text or explanation. Just give the SQL query.
        Given the SQL schema:
        {cached_schema}

        Complete the SQL query:
        {user_query}
        """
        llm = get_llm(max_tokens)
        response = llm.invoke(prompt)
        
        suggestion = response.content.strip() if response and response.content else ""

        return jsonify({"suggestion": suggestion})



    return jsonify({"suggestion": ""})

if __name__ == "__main__":
    app.run(debug=True)
