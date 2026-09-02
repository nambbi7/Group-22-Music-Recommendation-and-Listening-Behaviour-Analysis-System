import os
from flask import Flask
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

app = Flask(__name__)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)


@app.route("/")
def home():
    return "Music Recommendation System Backend is Running!"


if __name__ == "__main__":
    app.run(debug=True)
