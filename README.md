# CHERI - Music Recommendation and Listening Behaviour Analysis System

## Project Overview

CHERI is a web-based music recommendation and listening behaviour analysis system developed to provide users with a personalized music experience.

The system combines music recommendation, Spotify integration, favourites, ratings, analytics, and music personality analysis. CHERI uses a cleaned music dataset containing pre-calculated audio features to analyse songs and generate meaningful recommendations.

The system is developed using Python and Flask for the backend, Supabase and PostgreSQL for data storage, and HTML, CSS and JavaScript for the frontend.

---

## Objectives

The main objectives of CHERI are:

- Provide users with a personalized music recommendation system.
- Analyse users' listening behaviour.
- Allow users to search and play music through Spotify.
- Store listening history and favourite songs.
- Allow users to rate songs.
- Recommend songs based on music characteristics.
- Visualize the musical characteristics of individual songs.
- Provide users with a combined music profile based on their listening behaviour.
- Provide a simple, modern and user-friendly music platform.

---

## Main Features

### 1. User Registration and Login

CHERI provides user authentication features that allow users to:

- Create an account.
- Log in securely.
- Log out.
- Reset forgotten passwords.
- Update their password.

Authentication is handled using Supabase Authentication.

---

### 2. CHERI Dashboard

The dashboard acts as the main navigation page of the system.

Users can access important features including:

- Music Player
- Recommendations
- Library
- CHERNOME
- VibeMatch
- Profile

The dashboard uses the CHERI visual identity and provides a simple interface for navigating through the system.

---

### 3. Spotify Integration

CHERI integrates with Spotify services to provide music search and playback functionality.

Users can:

- Connect their Spotify account.
- Search for songs.
- View song information.
- View album artwork.
- Play Spotify tracks.
- Control music playback through the browser.

Spotify Web API is used for music search and track information.

Spotify Web Playback SDK is used for browser-based playback.

---

### 4. Music Player

The CHERI music player allows users to:

- Search for songs.
- Play songs.
- Pause and resume playback.
- View album artwork.
- View song and artist information.
- Add songs to favourites.
- Rate songs.
- Generate recommendations.
- Use the Surprise Me feature.

The player is integrated with Spotify to provide music playback functionality.

---

### 5. Music Recommendations

CHERI provides personalized music recommendations based on song characteristics.

The recommendation system uses music features from the cleaned dataset, including:

- Danceability
- Energy
- Valence
- Acousticness
- Instrumentalness
- Speechiness
- Liveness
- Tempo

The system compares the characteristics of songs and calculates similarity between tracks.

A similarity percentage is displayed to help users understand how closely a recommended song matches the selected song.

---

### 6. Surprise Me

The Surprise Me feature provides users with a randomly selected song from the system.

The selected song is then searched through Spotify and played using the existing music player.

This feature gives users a simple way to discover music without manually searching for a song.


### 8. Library

The Library provides users with an overview of their music activity.

It includes:

- Listening history
- Top songs
- Recently added favourites
- Song play counts

The Top Songs section calculates how frequently each song has been played.

---

### 9. Favourites

Users can add songs to their favourites.

The system allows users to:

- Add songs to favourites.
- Remove songs from favourites.
- View their favourite songs.

Favourite songs are stored in the database and associated with the corresponding user.

---

### 10. Song Ratings

Users can rate songs from 1 to 5 stars.

The rating system allows CHERI to store individual user ratings and associate them with songs.

Ratings are stored in the database using a relationship between the user and the selected song.

---

## CHERNOME

### What is CHERNOME?

CHERNOME stands for CHERI + Genome.

It represents the musical genome of a song.

The feature provides a visual representation of the characteristics of an individual song.

CHERNOME uses pre-calculated audio features from the cleaned music dataset rather than analysing the raw audio file directly.

The system retrieves the following characteristics:

- Danceability
- Energy
- Valence
- Acousticness
- Instrumentalness
- Speechiness
- Liveness
- Tempo

These values are visualized to help users understand the musical characteristics of a song.

---

## CHERNOME Save Feature

Users can save the CHERNOME of songs they have listened to.

When a user has listened to a song for at least 30 seconds, CHERI can ask whether the user wants to discover and save the song's CHERNOME.

Saved CHERNOMEs are associated with the user's account.

Users can:

- Save a CHERNOME.
- View saved CHERNOMEs.
- Remove saved CHERNOMEs.
- View the song's musical characteristics.

---

## CHERI Soundprint

CHERI Soundprint is an additional music analysis feature based on multiple saved CHERNOMEs.

The feature becomes available when the user has saved at least three CHERNOMEs.

Soundprint combines the musical characteristics of the saved songs and calculates an overall music profile.

The system uses the saved songs and their corresponding dataset features to calculate average characteristics.

This provides a broader representation of the user's listening preferences.

The Soundprint feature automatically becomes unavailable when fewer than three CHERNOMEs remain.

---

## VibeMatch

VibeMatch is a music analysis feature designed to help users explore their listening behaviour and musical preferences.

The feature uses music characteristics and user listening information to provide a personalized representation of the user's musical vibe.

---

## Data Processing and Recommendation

CHERI uses a cleaned music dataset for music analysis.

The dataset contains pre-calculated numerical audio features for individual tracks.

Each song is identified using its track ID.

The system retrieves the relevant features using the track ID and uses them for:

- Music recommendation.
- Similarity calculation.
- CHERNOME visualization.
- Soundprint analysis.
- Music behaviour analysis.

The recommendation process compares the audio characteristics of songs to determine their similarity.

---

## System Architecture

CHERI follows a web application architecture consisting of several main components.

### Frontend

The frontend is developed using:

- HTML
- CSS
- JavaScript

The frontend provides the user interface and communicates with the Flask backend through routes and API requests.

### Backend

The backend is developed using:

- Python
- Flask

The Flask backend handles:

- User authentication
- Spotify authentication
- Spotify API requests
- Music recommendations
- Listening history
- Favourites
- Ratings
- CHERNOME
- Soundprint
- Library data
- Password reset functionality

### Database

Supabase is used as the backend database service.

The database uses PostgreSQL.

Main database tables include:

- `users`
- `Songs`
- `listening_history`
- `favourites`
- `ratings`
- `chernomes`

Relationships between tables are maintained using foreign keys.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Backend web framework |
| HTML | Web page structure |
| CSS | User interface styling |
| JavaScript | Frontend interaction and API communication |
| Supabase | Authentication and database services |
| PostgreSQL | Relational database |
| Pandas | Dataset processing and analysis |
| Matplotlib | Data visualization and analysis |
| Spotify Web API | Music search and metadata |
| Spotify Web Playback SDK | Browser-based music playback |
| GitHub | Source code management |
| python-dotenv | Environment variable management |
| OAuth | Spotify account authentication |

---

## Database Structure

### Users

Stores registered CHERI users.

Main information includes:

- User ID
- Username
- Email
- Creation date

---

### Songs

Stores song information used by CHERI.

Main information includes:

- Song ID
- Song title
- Artist
- Genre
- Mood
- Duration
- Spotify track ID
- Album image URL

---

### Listening History

Stores users' listening activity.

Main information includes:

- History ID
- User ID
- Song ID
- Played time
- Duration played

---

### Favourites

Stores songs that users have added to their favourites.

Main information includes:

- Favourite ID
- User ID
- Song ID
- Creation date

---

### Ratings

Stores user ratings for songs.

Main information includes:

- Rating ID
- User ID
- Song ID
- Rating
- Creation date

Ratings are restricted to values from 1 to 5.

---

### CHERNOMEs

Stores songs that users have saved as CHERNOMEs.

Main information includes:

- CHERNOME ID
- User ID
- Spotify track ID
- Track name
- Artists
- Album name
- Album image
- Creation date

---

## APIs and Integrations

CHERI uses internal Flask API routes to communicate between the frontend and backend.

The system includes functionality for:

- Spotify authentication
- Spotify token management
- Spotify music search
- Listening history
- Favourites
- Ratings
- Music recommendations
- CHERNOME saving
- CHERNOME retrieval
- CHERNOME removal
- Soundprint analysis
- Surprise Me
- Library data
- Password reset

The application also communicates with external Spotify services through the Spotify Web API and Spotify Web Playback SDK.

---

## Dataset

CHERI uses a cleaned version of the Spotify Tracks Dataset for music analysis.

The dataset contains information about music tracks and pre-calculated audio features.

Important features used by CHERI include:

- Danceability
- Energy
- Valence
- Acousticness
- Instrumentalness
- Speechiness
- Liveness
- Tempo

The dataset is used for recommendation and music analysis purposes.

### Dataset Source

Spotify Tracks Dataset

Created by Yash Dev and published on Kaggle.

The dataset is credited through the CHERI Credit page within the application.

---

## Spotify Services

CHERI uses Spotify services for music-related functionality.

### Spotify Web API

Used for:

- Searching tracks
- Retrieving track information
- Retrieving artist information
- Retrieving album artwork
- Accessing Spotify track metadata

### Spotify Web Playback SDK

Used for:

- Browser-based playback
- Creating the CHERI Spotify player
- Controlling music playback

Users require an eligible Spotify account for playback functionality.

---

## Project Structure

The project follows a Flask web application structure.

```text
Group-22/
│
├── app.py
├── .env
├── .gitignore
├── README.md
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── music_player.html
│   ├── recommendations.html
│   ├── library.html
│   ├── chernome.html
│   ├── credits.html
│   ├── profile.html
│   ├── update_password.html
│   └── ...
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── cleaned_data/
│   └── clean_music.csv
│
└── venv/

