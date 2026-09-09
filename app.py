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

            return redirect(url_for("dashboard"))
        
        except Exception as e:
            return f"Login failed: {str(e)}"

    return render_template("login.html")


@app.route("/logout")
def logout():
    supabase.auth.sign_out()
    session.clear()
    return "Logged out successfully!"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            if response.session:
                supabase.auth.set_session(
                    response.session.access_token,
                    response.session.refresh_token
                )

            supabase.table("users").insert({
                "username": username,
                "email": email
            }).execute()

            return redirect(url_for("login"))
        
        except Exception as e:
            print("REGISTRATION ERROR:", repr(e))
            raise

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

@app.route("/music-player")
def music_player():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("music_player.html")

@app.route("/api/songs", methods=["GET"])
def get_songs():
    try:
        response = supabase.table("Songs").select("*").execute()

        return {
            "success": True,
            "songs": response.data
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }, 500

if __name__ == "__main__":
    app.run(debug=True)