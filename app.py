import os
import secrets
import hashlib
import base64
import requests
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


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

@app.route("/favourites")
def favourites():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("favourites.html")

@app.route("/spotify/login")
def spotify_login():

    code_verifier = secrets.token_urlsafe(64)

    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")

    session["spotify_code_verifier"] = code_verifier

    spotify_url = (
        "https://accounts.spotify.com/authorize"
        "?client_id=" + SPOTIFY_CLIENT_ID
        + "&response_type=code"
        + "&redirect_uri=" + SPOTIFY_REDIRECT_URI
        + "&code_challenge_method=S256"
        + "&code_challenge=" + code_challenge
        + "&scope=user-read-playback-state%20user-modify-playback-state%20streaming"
    )

    return redirect(spotify_url)

@app.route("/spotify/callback")
def spotify_callback():

    code = request.args.get("code")

    if not code:
        return "Spotify authorization failed."

    code_verifier = session.get("spotify_code_verifier")

    if not code_verifier:
        return "Spotify code verifier missing."

    token_response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "client_id": SPOTIFY_CLIENT_ID,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "code_verifier": code_verifier
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    if token_response.status_code != 200:
        return f"Spotify token error: {token_response.text}"

    token_data = token_response.json()

    session["spotify_access_token"] = token_data["access_token"]
    session["spotify_refresh_token"] = token_data.get("refresh_token")

    return "Spotify connected successfully! "

@app.route("/api/spotify/search", methods=["GET"])
def spotify_search():

    access_token = session.get("spotify_access_token")

    if not access_token:
        return {
            "success": False,
            "error": "Spotify is not connected."
        }, 401

    query = request.args.get("q")

    if not query:
        return {
            "success": False,
            "error": "Please provide a search query."
        }, 400

    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        params={
            "q": query,
            "type": "track",
            "limit": 10
        }
    )

    if response.status_code != 200:
        return {
            "success": False,
            "error": response.text
        }, response.status_code

    data = response.json()

    tracks = []

    for track in data["tracks"]["items"]:
        tracks.append({
            "id": track["id"],
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "image": track["album"]["images"][0]["url"]
                if track["album"]["images"] else None,
            "spotify_url": track["external_urls"]["spotify"]
        })

    return {
        "success": True,
        "tracks": tracks
    }

@app.route("/spotify/token")
def spotify_token():

    access_token = session.get("spotify_access_token")

    if not access_token:
        return {
            "success": False,
            "error": "Spotify is not connected."
        }, 401

    return {
        "success": True,
        "access_token": access_token
    }

if __name__ == "__main__":
    app.run(debug=True)