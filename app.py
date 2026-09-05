import os
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)


@app.route("/")
def home():
    return "Music Recommendation System Backend is Running!"


@app.route("/test-users")
def test_users():
    response = supabase.table("users").select("*").execute()
    return str(response.data)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            session["user_id"] = response.user.id
            session["email"] = response.user.email

            return "Login successful!"

        except Exception as e:
            return f"Login failed: {str(e)}"

    return render_template("login.html")


@app.route("/logout")
def logout():
    supabase.auth.sign_out()
    session.clear()
    return "Logged out successfully!"


if __name__ == "__main__":
    app.run(debug=True)