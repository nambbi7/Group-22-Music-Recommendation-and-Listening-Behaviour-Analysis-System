import os
import secrets
import hashlib
import base64
import requests

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from dotenv import load_dotenv
from supabase import create_client

from week4_recommendation.recommendation import recommend_songs_with_fallback


load_dotenv()


app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "dev-secret-key"
)


supabase_url = os.getenv(
    "SUPABASE_URL"
)

supabase_key = os.getenv(
    "SUPABASE_KEY"
)


supabase = create_client(
    supabase_url,
    supabase_key
)


SPOTIFY_CLIENT_ID = os.getenv(
    "SPOTIFY_CLIENT_ID"
)

SPOTIFY_REDIRECT_URI = os.getenv(
    "SPOTIFY_REDIRECT_URI"
)


@app.route("/")
def home():

    return render_template(
        "home.html"
    )


@app.route("/test-users")
def test_users():

    response = (
        supabase
        .table("users")
        .select("*")
        .execute()
    )

    return str(
        response.data
    )


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:

            response = (
                supabase
                .auth
                .sign_in_with_password({
                    "email": email,
                    "password": password
                })
            )

            session["user_id"] = (
                response.user.id
            )

            session["email"] = (
                response.user.email
            )

            print(
                "LOGIN SUCCESS:",
                response.user.email
            )

            return redirect(
                url_for("dashboard")
            )

        except Exception as e:

            print(
                "LOGIN ERROR:",
                repr(e)
            )

            return (
                f"Login failed: {str(e)}"
            )

    return render_template(
        "login.html"
    )


@app.route("/logout")
def logout():

    try:

        supabase.auth.sign_out()

    except Exception:

        pass

    session.clear()

    return "Logged out successfully!"


@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]

        try:

            response = (
                supabase
                .auth
                .sign_up({
                    "email": email,
                    "password": password
                })
            )

            if response.session:

                supabase.auth.set_session(
                    response.session.access_token,
                    response.session.refresh_token
                )

            supabase.table(
                "users"
            ).insert({
                "username": username,
                "email": email
            }).execute()

            return redirect(
                url_for("login")
            )

        except Exception as e:

            print(
                "REGISTRATION ERROR:",
                repr(e)
            )

            raise

    return render_template(
        "register.html"
    )


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "dashboard.html"
    )


@app.route("/music-player")
def music_player():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "music_player.html"
    )


@app.route("/favourites")
def favourites():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "favourites.html"
    )


@app.route("/recommendations")
def recommendations():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "recommendations.html"
    )


@app.route("/vibematch")
def vibematch():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "vibematch.html"
    )


@app.route(
    "/api/ratings",
    methods=["GET", "POST"]
)
def ratings():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "error": "Not logged in"
        }), 401

    user_id = get_database_user_id()

    if not user_id:

        return jsonify({
            "success": False,
            "error": "User account not found"
        }), 404

    if request.method == "GET":

        spotify_track_id = request.args.get(
            "spotify_track_id"
        )

        if not spotify_track_id:

            return jsonify({
                "success": False,
                "error": "Spotify track ID is required"
            }), 400

        song_response = (
            supabase
            .table("Songs")
            .select("id")
            .eq(
                "spotify_track_id",
                spotify_track_id
            )
            .limit(1)
            .execute()
        )

        if not song_response.data:

            return jsonify({
                "success": True,
                "rated": False
            })

        song_id = song_response.data[0]["id"]

        rating_response = (
            supabase
            .table("ratings")
            .select("id, rating")
            .eq(
                "user_id",
                user_id
            )
            .eq(
                "song_id",
                song_id
            )
            .limit(1)
            .execute()
        )

        return jsonify({
            "success": True,
            "rated": bool(
                rating_response.data
            ),
            "rating": (
                rating_response.data[0]["rating"]
                if rating_response.data
                else None
            )
        })

    data = request.get_json() or {}

    spotify_track_id = data.get(
        "spotify_track_id"
    )

    title = data.get(
        "title"
    )

    artist = data.get(
        "artist"
    )

    image_url = data.get(
        "image_url"
    )

    duration = data.get(
        "duration"
    )

    rating = data.get(
        "rating"
    )

    if not spotify_track_id:

        return jsonify({
            "success": False,
            "error": "Spotify track ID is required"
        }), 400

    try:

        rating = int(rating)

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "error": "Rating must be a number"
        }), 400

    if rating < 1 or rating > 5:

        return jsonify({
            "success": False,
            "error": "Rating must be between 1 and 5"
        }), 400

    song_response = (
        supabase
        .table("Songs")
        .select("*")
        .eq(
            "spotify_track_id",
            spotify_track_id
        )
        .limit(1)
        .execute()
    )

    if song_response.data:

        song_id = song_response.data[0]["id"]

        existing_song = song_response.data[0]

        update_data = {}

        if (
            image_url
            and not existing_song.get(
                "image_url"
            )
        ):

            update_data[
                "image_url"
            ] = image_url

        if (
            duration is not None
            and not existing_song.get(
                "duration"
            )
        ):

            update_data[
                "duration"
            ] = duration

        if update_data:

            (
                supabase
                .table("Songs")
                .update(update_data)
                .eq(
                    "id",
                    song_id
                )
                .execute()
            )

    else:

        song_data = {

            "tittle":
                title or "Unknown",

            "artist":
                artist or "Unknown",

            "spotify_track_id":
                spotify_track_id

        }

        if image_url:

            song_data[
                "image_url"
            ] = image_url

        if duration is not None:

            song_data[
                "duration"
            ] = duration

        new_song_response = (
            supabase
            .table("Songs")
            .insert(song_data)
            .execute()
        )

        if not new_song_response.data:

            return jsonify({
                "success": False,
                "error": "Unable to save song"
            }), 500

        song_id = (
            new_song_response
            .data[0]["id"]
        )

    rating_response = (
        supabase
        .table("ratings")
        .upsert(
            {
                "user_id":
                    user_id,

                "song_id":
                    song_id,

                "rating":
                    rating
            },
            on_conflict="user_id,song_id"
        )
        .execute()
    )

    if not rating_response.data:

        return jsonify({
            "success": False,
            "error": "Unable to save rating"
        }), 500

    return jsonify({
        "success": True,
        "rating": rating
    })


@app.route("/admin-dashboard")
def admin_dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    try:

        users_response = (
            supabase
            .table("users")
            .select(
                "id",
                count="exact"
            )
            .execute()
        )

        songs_response = (
            supabase
            .table("Songs")
            .select(
                "id",
                count="exact"
            )
            .execute()
        )

        history_response = (
            supabase
            .table("listening_history")
            .select(
                "id, duration_played",
                count="exact"
            )
            .execute()
        )

        total_users = (
            users_response.count or 0
        )

        total_songs = (
            songs_response.count or 0
        )

        total_plays = (
            history_response.count or 0
        )

        total_minutes = 0

        for item in history_response.data:

            duration = (
                item.get(
                    "duration_played"
                ) or 0
            )

            total_minutes += duration

        total_minutes = round(
            total_minutes / 60
        )

        return render_template(
            "admin_dashboard.html",
            total_users=total_users,
            total_songs=total_songs,
            total_plays=total_plays,
            total_minutes=total_minutes
        )

    except Exception as e:

        print(
            "ADMIN DASHBOARD ERROR:",
            repr(e)
        )

        return render_template(
            "admin_dashboard.html",
            total_users=0,
            total_songs=0,
            total_plays=0,
            total_minutes=0
        )


@app.route(
    "/api/vibematch/ratings",
    methods=["GET"]
)
def vibematch_ratings():

    if "user_id" not in session:

        return {
            "success": False,
            "error": "User is not logged in."
        }, 401

    try:

        database_user_id = (
            get_database_user_id()
        )

        if not database_user_id:

            return {
                "success": False,
                "error": "Database user not found."
            }, 404

        response = (
            supabase
            .table("ratings")
            .select(
                "id, rating, created_at, song_id, Songs(*)"
            )
            .eq(
                "user_id",
                database_user_id
            )
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )

        ratings = []

        for item in response.data:

            song = item.get(
                "Songs"
            )

            if not song:
                continue

            ratings.append({

                "rating_id":
                    item["id"],

                "rating":
                    item["rating"],

                "created_at":
                    item["created_at"],

                "song_id":
                    song["id"],

                "title":
                    song.get(
                        "tittle",
                        "Unknown"
                    ),

                "artist":
                    song.get(
                        "artist",
                        "Unknown"
                    ),

                "genre":
                    song.get(
                        "genre"
                    ),

                "mood":
                    song.get(
                        "mood"
                    ),

                "duration":
                    song.get(
                        "duration"
                    ),

                "image":
                    song.get(
                        "image_url"
                    ),

                "spotify_track_id":
                    song.get(
                        "spotify_track_id"
                    )

            })

        five_star_ratings = [
            item for item in ratings
            if item["rating"] == 5
        ]

        return {

            "success":
                True,

            "ratings":
                ratings,

            "five_star_ratings":
                five_star_ratings

        }

    except Exception as e:

        print(
            "VIBEMATCH RATINGS ERROR:",
            repr(e)
        )

        return {

            "success":
                False,

            "error":
                str(e)

        }, 500


@app.route("/spotify/login")
def spotify_login():

    code_verifier = (
        secrets.token_urlsafe(64)
    )

    code_challenge = (
        base64
        .urlsafe_b64encode(
            hashlib.sha256(
                code_verifier.encode()
            ).digest()
        )
        .decode()
        .rstrip("=")
    )

    session[
        "spotify_code_verifier"
    ] = code_verifier

    spotify_url = (
        "https://accounts.spotify.com/authorize"
        "?client_id="
        + SPOTIFY_CLIENT_ID
        + "&response_type=code"
        + "&redirect_uri="
        + SPOTIFY_REDIRECT_URI
        + "&code_challenge_method=S256"
        + "&code_challenge="
        + code_challenge
        + "&scope="
        + "user-read-playback-state%20"
        + "user-modify-playback-state%20"
        + "streaming"
    )

    return redirect(
        spotify_url
    )


@app.route("/spotify/callback")
def spotify_callback():

    code = request.args.get(
        "code"
    )

    if not code:

        return (
            "Spotify authorization failed."
        )

    code_verifier = session.get(
        "spotify_code_verifier"
    )

    if not code_verifier:

        return (
            "Spotify code verifier missing."
        )

    token_response = requests.post(
        "https://accounts.spotify.com/api/token",

        data={

            "client_id":
                SPOTIFY_CLIENT_ID,

            "grant_type":
                "authorization_code",

            "code":
                code,

            "redirect_uri":
                SPOTIFY_REDIRECT_URI,

            "code_verifier":
                code_verifier
        },

        headers={

            "Content-Type":
                "application/x-www-form-urlencoded"

        }
    )

    if token_response.status_code != 200:

        return (
            "Spotify token error: "
            + token_response.text
        )

    token_data = (
        token_response.json()
    )

    session[
        "spotify_access_token"
    ] = token_data[
        "access_token"
    ]

    session[
        "spotify_refresh_token"
    ] = token_data.get(
        "refresh_token"
    )

    return redirect(
        url_for("music_player")
    )


@app.route(
    "/api/spotify/search",
    methods=["GET"]
)
def spotify_search():

    access_token = session.get(
        "spotify_access_token"
    )

    if not access_token:

        return {
            "success": False,
            "error":
                "Spotify is not connected."
        }, 401

    query = request.args.get(
        "q"
    )

    if not query:

        return {
            "success": False,
            "error":
                "Please provide a search query."
        }, 400

    response = requests.get(
        "https://api.spotify.com/v1/search",

        headers={
            "Authorization":
                f"Bearer {access_token}"
        },

        params={

            "q":
                query,

            "type":
                "track",

            "limit":
                10

        }
    )

    if response.status_code != 200:

        return {
            "success": False,
            "error":
                response.text
        }, response.status_code

    data = response.json()

    tracks = []

    for track in data[
        "tracks"
    ][
        "items"
    ]:

        tracks.append({

            "id":
                track["id"],

            "name":
                track["name"],

            "artist":
                track["artists"][0]["name"],

            "album":
                track["album"]["name"],

            "image":
                track["album"]["images"][0]["url"]
                if track["album"]["images"]
                else None,

            "duration":
                track.get(
                    "duration_ms",
                    0
                ) / 1000,

            "spotify_url":
                track[
                    "external_urls"
                ][
                    "spotify"
                ]

        })

    return {
        "success": True,
        "tracks":
            tracks
    }


@app.route("/spotify/token")
def spotify_token():

    access_token = session.get(
        "spotify_access_token"
    )

    if not access_token:

        return {
            "success": False,
            "error":
                "Spotify is not connected."
        }, 401

    return {
        "success": True,
        "access_token":
            access_token
    }


@app.route(
    "/api/recommendations/<track_id>",
    methods=["GET"]
)
def get_recommendations(
    track_id
):

    if "user_id" not in session:

        return {
            "success": False,
            "error":
                "User is not logged in."
        }, 401

    try:

        song_response = (
            supabase
            .table("Songs")
            .select(
                "tittle, artist"
            )
            .eq(
                "spotify_track_id",
                track_id
            )
            .limit(1)
            .execute()
        )

        song_name = None
        artist = None

        if song_response.data:

            song_name = (
                song_response
                .data[0]
                .get("tittle")
            )

            artist = (
                song_response
                .data[0]
                .get("artist")
            )

        recommendations = (
            recommend_songs_with_fallback(
                track_id,
                song_name,
                artist,
                3
            )
        )

        if not recommendations:

            return {
                "success": False,
                "error":
                    "No recommendations found."
            }, 404

        return {

            "success":
                True,

            "track_id":
                track_id,

            "recommendations":
                recommendations
        }

    except Exception as e:

        print(
            "RECOMMENDATION ERROR:",
            repr(e)
        )

        return {

            "success":
                False,

            "error":
                str(e)

        }, 500


def get_database_user_id():

    email = session.get(
        "email"
    )

    print(
        "LOGIN EMAIL:",
        email
    )

    if not email:

        print(
            "NO EMAIL FOUND IN SESSION"
        )

        return None

    try:

        response = (
            supabase
            .table("users")
            .select(
                "id, username, email"
            )
            .ilike(
                "email",
                email
            )
            .limit(1)
            .execute()
        )

        print(
            "DATABASE USER:",
            response.data
        )

        if not response.data:

            print(
                "NO DATABASE USER FOUND"
            )

            return None

        return response.data[0]["id"]

    except Exception as e:

        print(
            "USER LOOKUP ERROR:",
            repr(e)
        )

        return None


@app.route(
    "/api/listening/start",
    methods=["POST"]
)
def start_listening():

    print(
        "LISTENING START REQUEST RECEIVED"
    )

    if "user_id" not in session:

        print(
            "NO AUTH USER IN SESSION"
        )

        return {
            "success": False,
            "error":
                "User is not logged in."
        }, 401

    data = request.get_json()

    print(
        "LISTENING DATA:",
        data
    )

    if not data:

        return {
            "success": False,
            "error":
                "No song data received."
        }, 400

    spotify_track_id = data.get(
        "spotify_track_id"
    )

    title = data.get(
        "title"
    )

    artist = data.get(
        "artist"
    )

    image_url = data.get(
        "image_url"
    )

    duration = data.get(
        "duration"
    )

    if not spotify_track_id:

        return {
            "success": False,
            "error":
                "Spotify track ID is required."
        }, 400

    if not title:

        title = "Unknown"

    if not artist:

        artist = "Unknown"

    try:

        song_response = (
            supabase
            .table("Songs")
            .select("*")
            .eq(
                "spotify_track_id",
                spotify_track_id
            )
            .limit(1)
            .execute()
        )

        print(
            "EXISTING SONG:",
            song_response.data
        )

        if not song_response.data:

            new_song = {

                "tittle":
                    title,

                "artist":
                    artist,

                "spotify_track_id":
                    spotify_track_id,

                "image_url":
                    image_url,

                "duration":
                    duration

            }

            print(
                "CREATING SONG:",
                new_song
            )

            insert_response = (
                supabase
                .table("Songs")
                .insert(
                    new_song
                )
                .execute()
            )

            print(
                "SONG INSERT RESULT:",
                insert_response.data
            )

            if not insert_response.data:

                return {
                    "success": False,
                    "error":
                        "Unable to create song."
                }, 500

            song_id = (
                insert_response
                .data[0]["id"]
            )

        else:

            song_id = (
                song_response
                .data[0]["id"]
            )

            existing_song = (
                song_response
                .data[0]
            )

            update_data = {}

            if (
                image_url
                and not existing_song.get(
                    "image_url"
                )
            ):

                update_data[
                    "image_url"
                ] = image_url

            if (
                duration
                and not existing_song.get(
                    "duration"
                )
            ):

                update_data[
                    "duration"
                ] = duration

            if update_data:

                (
                    supabase
                    .table("Songs")
                    .update(update_data)
                    .eq(
                        "id",
                        song_id
                    )
                    .execute()
                )

        print(
            "SONG ID:",
            song_id
        )

        database_user_id = (
            get_database_user_id()
        )

        print(
            "DATABASE USER ID:",
            database_user_id
        )

        if not database_user_id:

            return {
                "success": False,
                "error":
                    "Database user not found."
            }, 404

        history_data = {

            "user_id":
                database_user_id,

            "song_id":
                song_id,

            "duration_played":
                0

        }

        print(
            "CREATING HISTORY:",
            history_data
        )

        history_response = (
            supabase
            .table("listening_history")
            .insert(
                history_data
            )
            .execute()
        )

        print(
            "HISTORY INSERT RESULT:",
            history_response.data
        )

        if not history_response.data:

            return {
                "success": False,
                "error":
                    "Unable to save listening history."
            }, 500

        history_id = (
            history_response
            .data[0]["id"]
        )

        print(
            "LISTENING HISTORY SAVED:",
            history_id
        )

        return {

            "success":
                True,

            "message":
                "Listening started.",

            "history_id":
                history_id,

            "song_id":
                song_id

        }

    except Exception as e:

        print(
            "LISTENING ERROR:",
            repr(e)
        )

        return {

            "success":
                False,

            "error":
                str(e)

        }, 500


@app.route(
    "/api/listening/update",
    methods=["POST"]
)
def update_listening():

    if "user_id" not in session:

        return {
            "success": False,
            "error":
                "User is not logged in."
        }, 401

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "error":
                "No data received."
        }, 400

    history_id = data.get(
        "history_id"
    )

    duration_played = data.get(
        "duration_played"
    )

    if not history_id:

        return {
            "success": False,
            "error":
                "History ID is required."
        }, 400

    if duration_played is None:

        return {
            "success": False,
            "error":
                "Duration is required."
        }, 400

    try:

        database_user_id = (
            get_database_user_id()
        )

        if not database_user_id:

            return {
                "success": False,
                "error":
                    "Database user not found."
            }, 404

        existing_history = (
            supabase
            .table("listening_history")
            .select(
                "id, user_id"
            )
            .eq(
                "id",
                history_id
            )
            .limit(1)
            .execute()
        )

        if not existing_history.data:

            return {
                "success": False,
                "error":
                    "Listening history not found."
            }, 404

        if (
            existing_history
            .data[0]["user_id"]
            != database_user_id
        ):

            return {
                "success": False,
                "error":
                    "You cannot update this listening history."
            }, 403

        response = (
            supabase
            .table("listening_history")
            .update({
                "duration_played":
                    int(duration_played)
            })
            .eq(
                "id",
                history_id
            )
            .execute()
        )

        print(
            "LISTENING DURATION UPDATED:",
            response.data
        )

        return {
            "success": True,
            "message":
                "Listening duration updated."
        }

    except Exception as e:

        print(
            "DURATION UPDATE ERROR:",
            repr(e)
        )

        return {
            "success": False,
            "error":
                str(e)
        }, 500


@app.route(
    "/api/favourites/add",
    methods=["POST"]
)
def add_favourite():

    if "user_id" not in session:

        return {
            "success": False,
            "error":
                "User is not logged in."
        }, 401

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "error":
                "No data received."
        }, 400

    spotify_track_id = data.get(
        "spotify_track_id"
    )

    title = data.get(
        "title"
    )

    artist = data.get(
        "artist"
    )

    image_url = data.get(
        "image_url"
    )

    duration = data.get(
        "duration"
    )

    if not spotify_track_id:

        return {
            "success": False,
            "error":
                "Spotify track ID is required."
        }, 400

    try:

        database_user_id = (
            get_database_user_id()
        )

        if not database_user_id:

            return {
                "success": False,
                "error":
                    "Database user not found."
            }, 404

        access_token = session.get(
            "spotify_access_token"
        )

        spotify_track = None

        if access_token:

            spotify_response = requests.get(
                "https://api.spotify.com/v1/tracks/"
                + spotify_track_id,

                headers={
                    "Authorization":
                        "Bearer "
                        + access_token
                }
            )

            if spotify_response.status_code == 200:

                spotify_track = (
                    spotify_response.json()
                )

        if spotify_track:

            title = (
                spotify_track.get(
                    "name"
                )
                or title
                or "Unknown"
            )

            artists = (
                spotify_track.get(
                    "artists",
                    []
                )
            )

            if artists:

                artist = (
                    artists[0].get(
                        "name"
                    )
                    or artist
                    or "Unknown"
                )

            album = spotify_track.get(
                "album",
                {}
            )

            images = album.get(
                "images",
                []
            )

            if images:

                image_url = (
                    images[0].get(
                        "url"
                    )
                    or image_url
                )

            spotify_duration = (
                spotify_track.get(
                    "duration_ms"
                )
            )

            if spotify_duration:

                duration = (
                    spotify_duration
                    / 1000
                )

        song_response = (
            supabase
            .table("Songs")
            .select("*")
            .eq(
                "spotify_track_id",
                spotify_track_id
            )
            .limit(1)
            .execute()
        )

        if song_response.data:

            song = (
                song_response.data[0]
            )

            song_id = song["id"]

            update_data = {}

            if (
                image_url
                and not song.get(
                    "image_url"
                )
            ):

                update_data[
                    "image_url"
                ] = image_url

            if (
                duration
                and not song.get(
                    "duration"
                )
            ):

                update_data[
                    "duration"
                ] = duration

            if update_data:

                (
                    supabase
                    .table("Songs")
                    .update(update_data)
                    .eq(
                        "id",
                        song_id
                    )
                    .execute()
                )

        else:

            new_song = {

                "tittle":
                    title or "Unknown",

                "artist":
                    artist or "Unknown",

                "spotify_track_id":
                    spotify_track_id,

                "image_url":
                    image_url,

                "duration":
                    duration

            }

            insert_response = (
                supabase
                .table("Songs")
                .insert(
                    new_song
                )
                .execute()
            )

            if not insert_response.data:

                return {
                    "success": False,
                    "error":
                        "Unable to create song."
                }, 500

            song_id = (
                insert_response
                .data[0]["id"]
            )

        existing = (
            supabase
            .table("favourites")
            .select("id")
            .eq(
                "user_id",
                database_user_id
            )
            .eq(
                "song_id",
                song_id
            )
            .limit(1)
            .execute()
        )

        if existing.data:

            return {
                "success": True,
                "message":
                    "Song is already in favourites.",
                "favourite_id":
                    existing.data[0]["id"]
            }

        favourite_response = (
            supabase
            .table("favourites")
            .insert({

                "user_id":
                    database_user_id,

                "song_id":
                    song_id

            })
            .execute()
        )

        if not favourite_response.data:

            return {
                "success": False,
                "error":
                    "Unable to save favourite."
            }, 500

        return {

            "success":
                True,

            "message":
                "Song added to favourites.",

            "favourite_id":
                favourite_response
                .data[0]["id"]

        }

    except Exception as e:

        print(
            "ADD FAVOURITE ERROR:",
            repr(e)
        )

        return {

            "success":
                False,

            "error":
                str(e)

        }, 500


@app.route(
    "/api/favourites/remove",
    methods=["POST"]
)
def remove_favourite():

    if "user_id" not in session:

        return {
            "success": False,
            "error":
                "User is not logged in."
        }, 401

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "error":
                "No data received."
        }, 400

    spotify_track_id = data.get(
        "spotify_track_id"
    )

    if not spotify_track_id:

        return {
            "success": False,
            "error":
                "Spotify track ID is required."
        }, 400

    try:

        database_user_id = (
            get_database_user_id()
        )

        if not database_user_id:

            return {
                "success": False,
                "error":
                    "Database user not found."
            }, 404

        song_response = (
            supabase
            .table("Songs")
            .select("id")
            .eq(
                "spotify_track_id",
                spotify_track_id
            )
            .limit(1)
            .execute()
        )

        if not song_response.data:

            return {
                "success": False,
                "error":
                    "Song not found."
            }, 404

        song_id = (
            song_response
            .data[0]["id"]
        )

        (
            supabase
            .table("favourites")
            .delete()
            .eq(
                "user_id",
                database_user_id
            )
            .eq(
                "song_id",
                song_id
            )
            .execute()
        )

        return {
            "success": True,
            "message":
                "Song removed from favourites."
        }

    except Exception as e:

        print(
            "REMOVE FAVOURITE ERROR:",
            repr(e)
        )

        return {
            "success": False,
            "error":
                str(e)
        }, 500


@app.route(
    "/api/favourites",
    methods=["GET"]
)
def get_favourites():

    if "user_id" not in session:

        return {
            "success": False,
            "error":
                "User is not logged in."
        }, 401

    try:

        database_user_id = (
            get_database_user_id()
        )

        if not database_user_id:

            return {
                "success": False,
                "error":
                    "Database user not found."
            }, 404

        response = (
            supabase
            .table("favourites")
            .select(
                "id, created_at, song_id, Songs(*)"
            )
            .eq(
                "user_id",
                database_user_id
            )
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )

        favourites = []

        for item in response.data:

            song = item.get(
                "Songs"
            )

            if not song:

                continue

            favourites.append({

                "favourite_id":
                    item["id"],

                "song_id":
                    song["id"],

                "title":
                    song.get(
                        "tittle",
                        "Unknown"
                    ),

                "artist":
                    song.get(
                        "artist",
                        "Unknown"
                    ),

                "genre":
                    song.get(
                        "genre"
                    ),

                "duration":
                    song.get(
                        "duration"
                    ),

                "image":
                    song.get(
                        "image_url"
                    ),

                "spotify_track_id":
                    song.get(
                        "spotify_track_id"
                    )

            })

        return {

            "success":
                True,

            "favourites":
                favourites

        }

    except Exception as e:

        print(
            "GET FAVOURITES ERROR:",
            repr(e)
        )

        return {

            "success":
                False,

            "error":
                str(e)

        }, 500


if __name__ == "__main__":

    print(
        app.url_map
    )

    app.run(
        debug=True
    )