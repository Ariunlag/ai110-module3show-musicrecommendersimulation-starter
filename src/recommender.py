import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Song metadata and audio-style features used for recommendation.

    Attributes:
        id: Unique integer song identifier.
        title: Song title.
        artist: Artist name.
        genre: Genre label (for example, pop or lofi).
        mood: Mood label (for example, happy or chill).
        energy: Energy value in the range [0, 1].
        tempo_bpm: Tempo in beats per minute.
        valence: Positivity value in the range [0, 1].
        danceability: Danceability value in the range [0, 1].
        acousticness: Acousticness value in the range [0, 1].
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    User taste preferences for personalized scoring.

    Attributes:
        favorite_genre: User's preferred genre label.
        favorite_mood: User's preferred mood label.
        target_energy: Desired energy level in the range [0, 1].
        likes_acoustic: True if user prefers acoustic songs.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    Object-oriented wrapper for recommendation behavior.

    This class is kept for test compatibility and future extension.
    """
    def __init__(self, songs: List[Song]):
        """Initialize the recommender with an in-memory song list."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Return up to k songs for the given user.

        Note:
            This method is currently a placeholder implementation and
            returns the first k songs.
        """
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """
        Return a plain-language explanation for why a song was suggested.

        Note:
            This method is currently a placeholder implementation.
        """
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Load songs from CSV and return them as dictionaries.

    Numeric columns are converted to numeric Python types so downstream
    scoring can run without additional casting.

    Args:
        csv_path: Relative or absolute path to the songs CSV file.

    Returns:
        A list of song dictionaries with typed values.
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            song = {
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            }
            songs.append(song)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score one song against user preferences.

    Uses a simple weighted formula:
        score = 0.35*genre_match + 0.25*mood_match +
                0.25*energy_fit + 0.15*acoustic_fit

    Args:
        user_prefs: User preference dictionary with keys like
            genre, mood, energy, and likes_acoustic.
        song: Song dictionary with feature keys loaded from CSV.

    Returns:
        Tuple of (numeric_score, reasons_list).
    """
    # Extract user preferences
    favorite_genre = user_prefs.get("genre", "").lower()
    favorite_mood = user_prefs.get("mood", "").lower()
    target_energy = float(user_prefs.get("energy", 0.5))
    likes_acoustic = user_prefs.get("likes_acoustic")
    
    # Extract song features
    song_genre = song.get("genre", "").lower()
    song_mood = song.get("mood", "").lower()
    song_energy = float(song.get("energy", 0.5))
    song_acousticness = float(song.get("acousticness", 0.5))
    
    # Calculate score components
    genre_match = 1.0 if song_genre == favorite_genre else 0.0
    mood_match = 1.0 if song_mood == favorite_mood else 0.0
    energy_fit = max(0.0, 1.0 - abs(song_energy - target_energy))
    
    # Acoustic fit
    if likes_acoustic is None:
        acoustic_fit = 0.5
        acoustic_reason = None
    elif likes_acoustic:
        acoustic_fit = song_acousticness
        acoustic_reason = "matches acoustic preference" if song_acousticness > 0.5 else None
    else:
        acoustic_fit = 1.0 - song_acousticness
        acoustic_reason = "matches non-acoustic preference" if song_acousticness < 0.5 else None
    
    # Weighted score
    score = (
        0.35 * genre_match +
        0.25 * mood_match +
        0.25 * energy_fit +
        0.15 * acoustic_fit
    )
    
    # Build reasons list
    reasons = []
    if genre_match > 0:
        reasons.append(f"genre matches {favorite_genre}")
    if mood_match > 0:
        reasons.append(f"mood matches {favorite_mood}")
    if energy_fit >= 0.8:
        reasons.append(f"energy is close to target ({song_energy:.2f})")
    if acoustic_reason:
        reasons.append(acoustic_reason)
    
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Recommend top-k songs by scoring and ranking the catalog.

    Args:
        user_prefs: User taste profile used for scoring.
        songs: List of song dictionaries.
        k: Number of recommendations to return.

    Returns:
        A list of tuples in the form:
        (song_dict, score, explanation_string), sorted by score descending.
    """
    scored_songs = []
    
    # Score each song
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "overall match with preferences"
        scored_songs.append((song, score, explanation))
    
    # Sort by score descending
    scored_songs.sort(key=lambda item: item[1], reverse=True)
    
    # Return top k
    return scored_songs[:k]
