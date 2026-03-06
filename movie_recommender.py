#!/usr/bin/env python3
"""
Movie Analyzer - CLI tool to load and display movie and ratings data.
Compatible with Python 3.12+
"""

import sys
import pandas as pd


def load_movies_file(filepath: str) -> pd.DataFrame:
    """Read movies file line by line and return a DataFrame.

    Movie_id must be a whole number (int); non-numeric values are replaced with NA.
    """
    records = []
    na_movie_id_count = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) != 3:
                print(f"  [WARNING] Line {lineno}: wrong number of fields — skipping: {line!r}")
                continue

            genre = parts[0].strip()
            raw_id = parts[1].strip()
            movie_name = parts[2].strip()

            movie_id = to_int_or_na(raw_id)

            if pd.isna(movie_id):
                na_movie_id_count += 1
                print(f"  [WARNING] Line {lineno}: non-numeric Movie_id {raw_id!r} → NA")

            records.append({"Genre": genre, "Movie_id": movie_id, "Movie_name": movie_name})

    df = pd.DataFrame(records, columns=["Genre", "Movie_id", "Movie_name"])
    df["Movie_id"] = df["Movie_id"].astype(pd.Int64Dtype())

    if na_movie_id_count:
        print(f"  WARNING: {na_movie_id_count} Movie_id value(s) replaced with NA.")

    return df


def to_float_or_na(value: str):
    """Return a float if value is a valid decimal number, otherwise return pd.NA."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return pd.NA


def to_int_or_na(value: str):
    """Return an int if value is a valid whole number, otherwise return pd.NA."""
    try:
        f = float(value)
        if f == int(f):
            return int(f)
        return pd.NA
    except (ValueError, TypeError):
        return pd.NA


def load_ratings_file(filepath: str) -> pd.DataFrame:
    """Read ratings file line by line and return a DataFrame.

    Rating must be numeric (float); non-numeric values are replaced with NA.
    User_id must be a whole number (int); non-numeric values are replaced with NA.
    """
    records = []
    na_rating_count = 0
    na_user_id_count = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) != 3:
                print(f"  [WARNING] Line {lineno}: wrong number of fields — skipping: {line!r}")
                continue

            movie_name = parts[0].strip()
            raw_rating = parts[1].strip()
            raw_user = parts[2].strip()

            rating = to_float_or_na(raw_rating)
            user_id = to_int_or_na(raw_user)

            if pd.isna(rating):
                na_rating_count += 1
                print(f"  [WARNING] Line {lineno}: non-numeric Rating {raw_rating!r} → NA")

            if pd.isna(user_id):
                na_user_id_count += 1
                print(f"  [WARNING] Line {lineno}: non-numeric User_id {raw_user!r} → NA")

            records.append({"Movie_name": movie_name, "Rating": rating, "User_id": user_id})

    df = pd.DataFrame(records, columns=["Movie_name", "Rating", "User_id"])
    df["Rating"] = df["Rating"].astype(pd.Float64Dtype())
    df["User_id"] = df["User_id"].astype(pd.Int64Dtype())

    if na_rating_count:
        print(f"  ⚠️  {na_rating_count} Rating value(s) replaced with NA.")
    if na_user_id_count:
        print(f"  ⚠️  {na_user_id_count} User_id value(s) replaced with NA.")

    return df


def print_header():
    """Print the program header."""
    print("=" * 55)
    print("         Movie Analyzer CLI")
    print("=" * 55)


def print_menu(movies_df: pd.DataFrame | None, ratings_df: pd.DataFrame | None):
    """Print the main menu."""
    print("\n── Main Menu ──────────────────────────────────────────")
    print("  1. Load Movies File")
    print("  2. Load Ratings File")
    print("  3. Display Movies DataFrame")
    print("  4. Display Ratings DataFrame")
    print("  5. Top Movie Ratings")
    print("  6. Top N Movies in a Genre")
    print("  7. Top N Genres")
    print("  8. User's Top Genre")
    print("  9. Recommend Movies for a User")
    print("  0. Exit")
    print("───────────────────────────────────────────────────────")

    status_movies = "✅ Loaded" if movies_df is not None else "❌ Not loaded"
    status_ratings = "✅ Loaded" if ratings_df is not None else "❌ Not loaded"
    print(f"  Movies File : {status_movies}")
    print(f"  Ratings File: {status_ratings}")
    print("───────────────────────────────────────────────────────")


def prompt_filepath(label: str) -> str:
    """Prompt user for file path."""
    return input(f"Enter path to {label}: ").strip()


def display_dataframe(df: pd.DataFrame, title: str):
    """Display a DataFrame with a title."""
    print(f"\n── {title} ({df.shape[0]} rows × {df.shape[1]} cols) ──")
    print(df.to_string(index=True))


def top_n_movies(n: int, ratings_df: pd.DataFrame) -> None:
    """Print the top n movies ranked by average rating from the ratings DataFrame.

    Movie name comparison is case-insensitive, so 'toy story' and 'Toy Story'
    are treated as the same movie. The most common casing is used for display.
    """
    valid = ratings_df.dropna(subset=["Rating"]).copy()

    if valid.empty:
        print("  [INFO] No valid ratings to rank.")
        return

    valid["Movie_name_lower"] = valid["Movie_name"].str.lower()

    display_name = (
        valid.groupby("Movie_name_lower")["Movie_name"]
        .agg(lambda names: names.value_counts().idxmax())
        .rename("Display_name")
    )

    summary = (
        valid.groupby("Movie_name_lower", as_index=False)
        .agg(Avg_Rating=("Rating", "mean"), Num_Ratings=("Rating", "count"))
        .merge(display_name, on="Movie_name_lower")
        .sort_values(["Avg_Rating", "Num_Ratings", "Display_name"], ascending=[False, False, True])
        .reset_index(drop=True)
    )

    total_movies = len(summary)
    n_capped = min(n, total_movies)

    print(f"\n── Top {n_capped} Rated Movies (of {total_movies} total) ────────────────")
    print(f"  {'Rank':<6} {'Avg Rating':<12} {'# Ratings':<12} Movie")
    print(f"  {'────':<6} {'──────────':<12} {'─────────':<12} ─────")

    for rank, row in enumerate(summary.head(n_capped).itertuples(), start=1):
        print(f"  {rank:<6} {row.Avg_Rating:<12.2f} {row.Num_Ratings:<12} {row.Display_name}")


def merge_movies_and_ratings(movies_df: pd.DataFrame, ratings_df: pd.DataFrame) -> pd.DataFrame:
    """Merge ratings with movies so each rating row includes genre.

    Matching is case-insensitive on Movie_name.
    Rows with NA ratings are excluded.
    """
    valid_ratings = ratings_df.dropna(subset=["Rating"]).copy()

    movies = movies_df.copy()
    ratings = valid_ratings.copy()

    movies["movie_key"] = movies["Movie_name"].astype(str).str.strip().str.lower()
    ratings["movie_key"] = ratings["Movie_name"].astype(str).str.strip().str.lower()

    merged = ratings.merge(
        movies[["movie_key", "Genre", "Movie_name"]],
        on="movie_key",
        how="inner",
        suffixes=("_rating", "_movie")
    )

    merged["Movie_name"] = merged["Movie_name_movie"]

    return merged[["Genre", "Movie_name", "Rating", "User_id"]]


def top_n_movies_in_genre(genre: str, n: int, movies_df: pd.DataFrame, ratings_df: pd.DataFrame) -> pd.DataFrame:
    """Return the top n movies in a genre ranked by average rating."""
    merged = merge_movies_and_ratings(movies_df, ratings_df)
    genre_key = genre.strip().lower()

    merged["genre_key"] = merged["Genre"].astype(str).str.strip().str.lower()
    genre_rows = merged[merged["genre_key"] == genre_key].copy()

    if genre_rows.empty:
        return pd.DataFrame(columns=["Movie_name", "Avg_Rating", "Num_Ratings"])

    summary = (
        genre_rows.groupby("Movie_name", as_index=False)
        .agg(Avg_Rating=("Rating", "mean"), Num_Ratings=("Rating", "count"))
        .sort_values(["Avg_Rating", "Num_Ratings", "Movie_name"], ascending=[False, False, True])
        .reset_index(drop=True)
    )

    return summary.head(n)


def top_n_genres(n: int, movies_df: pd.DataFrame, ratings_df: pd.DataFrame) -> pd.DataFrame:
    """Return the top n genres ranked by average of movie-average ratings."""
    merged = merge_movies_and_ratings(movies_df, ratings_df)

    movie_avgs = (
        merged.groupby(["Genre", "Movie_name"], as_index=False)
        .agg(Movie_Avg=("Rating", "mean"))
    )

    genre_scores = (
        movie_avgs.groupby("Genre", as_index=False)
        .agg(Genre_Score=("Movie_Avg", "mean"), Num_Movies=("Movie_name", "count"))
        .sort_values(["Genre_Score", "Num_Movies", "Genre"], ascending=[False, False, True])
        .reset_index(drop=True)
    )

    return genre_scores.head(n)


def user_top_genre(user_id: int, movies_df: pd.DataFrame, ratings_df: pd.DataFrame) -> str | None:
    """Return the user's top genre based on average ratings."""
    merged = merge_movies_and_ratings(movies_df, ratings_df)
    user_rows = merged[merged["User_id"] == user_id].copy()

    if user_rows.empty:
        return None

    genre_scores = (
        user_rows.groupby("Genre", as_index=False)
        .agg(User_Genre_Score=("Rating", "mean"), Num_Ratings=("Rating", "count"))
        .sort_values(["User_Genre_Score", "Num_Ratings", "Genre"], ascending=[False, False, True])
        .reset_index(drop=True)
    )

    return str(genre_scores.iloc[0]["Genre"])


def recommend_movies_for_user(user_id: int, movies_df: pd.DataFrame, ratings_df: pd.DataFrame, k: int = 3) -> list[str]:
    """Recommend k movies from the user's top genre that they have not rated."""
    top_genre = user_top_genre(user_id, movies_df, ratings_df)

    if top_genre is None:
        return []

    movies_in_genre = movies_df.copy()
    movies_in_genre["genre_key"] = movies_in_genre["Genre"].astype(str).str.strip().str.lower()
    top_genre_key = str(top_genre).strip().lower()

    movies_in_genre = movies_in_genre[movies_in_genre["genre_key"] == top_genre_key].copy()

    if movies_in_genre.empty:
        return []

    user_rated = ratings_df[ratings_df["User_id"] == user_id].copy()
    rated_keys = set(user_rated["Movie_name"].astype(str).str.strip().str.lower())

    movies_in_genre["movie_key"] = movies_in_genre["Movie_name"].astype(str).str.strip().str.lower()
    candidates = movies_in_genre[~movies_in_genre["movie_key"].isin(rated_keys)].copy()

    if candidates.empty:
        return []

    merged = merge_movies_and_ratings(movies_df, ratings_df)
    overall = (
        merged.groupby("Movie_name", as_index=False)
        .agg(Avg_Rating=("Rating", "mean"), Num_Ratings=("Rating", "count"))
    )

    candidates = candidates.merge(overall, on="Movie_name", how="left")
    candidates = candidates.dropna(subset=["Avg_Rating"]).copy()

    if candidates.empty:
        return []

    candidates = candidates.sort_values(["Avg_Rating", "Num_Ratings", "Movie_name"], ascending=[False, False, True])
    return candidates["Movie_name"].head(k).tolist()


def main():
    """Run the CLI program."""
    print_header()

    movies_df: pd.DataFrame | None = None
    ratings_df: pd.DataFrame | None = None

    while True:
        print_menu(movies_df, ratings_df)
        choice = input("Select an option: ").strip()

        if choice == "1":
            filepath = prompt_filepath("movie_file")
            try:
                movies_df = load_movies_file(filepath)
                print(f"   Movies file loaded successfully — {len(movies_df)} records.")
            except FileNotFoundError:
                print(f"   File not found: {filepath!r}")
            except Exception as e:
                print(f"   Error loading file: {e}")

        elif choice == "2":
            filepath = prompt_filepath("ratings_file")
            try:
                ratings_df = load_ratings_file(filepath)
                print(f"   Ratings file loaded successfully — {len(ratings_df)} records.")
            except FileNotFoundError:
                print(f"   File not found: {filepath!r}")
            except Exception as e:
                print(f"   Error loading file: {e}")

        elif choice == "3":
            if movies_df is not None:
                display_dataframe(movies_df, "Movies DataFrame")
            else:
                print("  [INFO] Movies file not loaded yet. Choose option 1 first.")

        elif choice == "4":
            if ratings_df is not None:
                display_dataframe(ratings_df, "Ratings DataFrame")
            else:
                print("  [INFO] Ratings file not loaded yet. Choose option 2 first.")

        elif choice == "5":
            if ratings_df is None:
                print("  [INFO] Ratings file not loaded yet. Choose option 2 first.")
            else:
                raw_n = input("  Enter number of top movies to display: ").strip()
                try:
                    n = int(raw_n)
                    if n <= 0:
                        print("  [ERROR] Please enter a positive integer.")
                    else:
                        top_n_movies(n, ratings_df)
                except ValueError:
                    print(f"  [ERROR] {raw_n!r} is not a valid integer.")

        elif choice == "6":
            if movies_df is None or ratings_df is None:
                print("  [INFO] Load both files first (options 1 and 2).")
            else:
                genre = input("  Enter genre: ").strip()
                raw_n = input("  Enter number of top movies to display: ").strip()
                try:
                    n = int(raw_n)
                    if n <= 0:
                        print("  [ERROR] Please enter a positive integer.")
                    else:
                        result = top_n_movies_in_genre(genre, n, movies_df, ratings_df)
                        if result.empty:
                            print("  [INFO] No rated movies found for that genre.")
                        else:
                            print(result.to_string(index=False))
                except ValueError:
                    print("  [ERROR] N must be an integer.")

        elif choice == "7":
            if movies_df is None or ratings_df is None:
                print("  [INFO] Load both files first (options 1 and 2).")
            else:
                raw_n = input("  Enter number of top genres to display: ").strip()
                try:
                    n = int(raw_n)
                    if n <= 0:
                        print("  [ERROR] Please enter a positive integer.")
                    else:
                        result = top_n_genres(n, movies_df, ratings_df)
                        if result.empty:
                            print("  [INFO] No genre stats available.")
                        else:
                            print(result.to_string(index=False))
                except ValueError:
                    print("  [ERROR] N must be an integer.")

        elif choice == "8":
            if movies_df is None or ratings_df is None:
                print("  [INFO] Load both files first (options 1 and 2).")
            else:
                raw_user = input("  Enter user id: ").strip()
                try:
                    user_id = int(raw_user)
                    top_genre = user_top_genre(user_id, movies_df, ratings_df)
                    if top_genre is None:
                        print("  [INFO] That user has no valid ratings.")
                    else:
                        print(f"  User {user_id}'s top genre: {top_genre}")
                except ValueError:
                    print("  [ERROR] User id must be an integer.")

        elif choice == "9":
            if movies_df is None or ratings_df is None:
                print("  [INFO] Load both files first (options 1 and 2).")
            else:
                raw_user = input("  Enter user id: ").strip()
                try:
                    user_id = int(raw_user)
                    recs = recommend_movies_for_user(user_id, movies_df, ratings_df, k=3)
                    if not recs:
                        print("  [INFO] No recommendations available for that user.")
                    else:
                        print("  Recommended movies:")
                        for movie in recs:
                            print(f"   - {movie}")
                except ValueError:
                    print("  [ERROR] User id must be an integer.")

        elif choice == "0":
            print("\n  Goodbye! 🎬\n")
            sys.exit(0)

        else:
            print("  [ERROR] Invalid option. Please enter a number from the menu.")


if __name__ == "__main__":
    main()
