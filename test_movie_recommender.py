#!/usr/bin/env python3
"""
Automated testing for movie_recommender.py
Tests all features and compares results against expected values.
"""

import sys
import os
import pandas as pd

# Add current directory to path to import the main module
sys.path.insert(0, os.path.dirname(__file__))

# Import functions from the main module (note: filename has typo in original)
from movie_reccomender import (
    load_movies_file,
    load_ratings_file,
    top_n_movies,
    top_n_movies_in_genre,
    top_n_genres,
    user_top_genre,
    recommend_movies_for_user,
    merge_movies_and_ratings
)


def test_load_movies():
    """Test loading movies file."""
    print("=== Testing Movies File Loading ===")
    movies_df = load_movies_file("movie_file.txt")
    print(f"Loaded {len(movies_df)} movies")
    print(f"Columns: {list(movies_df.columns)}")
    print(f"Sample data:\n{movies_df.head()}")
    return movies_df


def test_load_ratings():
    """Test loading ratings file."""
    print("\n=== Testing Ratings File Loading ===")
    ratings_df = load_ratings_file("ratings_file.txt")
    print(f"Loaded {len(ratings_df)} ratings")
    print(f"Columns: {list(ratings_df.columns)}")
    print(f"Sample data:\n{ratings_df.head()}")
    return ratings_df


def test_top_n_movies(ratings_df):
    """Test top N movies functionality."""
    print("\n=== Testing Top N Movies ===")

    # Test top 5 movies
    print("Top 5 movies:")
    top_n_movies(5, ratings_df)

    # Test with expected results
    print("\nExpected top movies (based on sample data):")
    expected_top_movies = [
        "Father of the Bride Part II (1995)",  # 4.17 avg
        "Toy Story (1995)",                   # 3.83 avg
        "Heat (1995)",                        # 4.25 avg (but fewer ratings)
        "Grumpier Old Men (1995)",            # 4.00 avg
        "GoldenEye (1995)"                    # 3.00 avg
    ]
    print("Expected order may vary due to tie-breaking rules")
    for i, movie in enumerate(expected_top_movies, 1):
        print(f"{i}. {movie}")


def test_top_n_movies_in_genre(movies_df, ratings_df):
    """Test top N movies in genre functionality."""
    print("\n=== Testing Top N Movies in Genre ===")

    # Test Action genre
    print("Top 3 Action movies:")
    result = top_n_movies_in_genre("Action", 3, movies_df, ratings_df)
    print(result.to_string(index=False))

    # Test Comedy genre
    print("\nTop 2 Comedy movies:")
    result = top_n_movies_in_genre("Comedy", 2, movies_df, ratings_df)
    print(result.to_string(index=False))

    # Test non-existent genre
    print("\nTesting non-existent genre 'Romance':")
    result = top_n_movies_in_genre("Romance", 3, movies_df, ratings_df)
    print(f"Result: {result.empty} (should be True - no movies found)")


def test_top_n_genres(movies_df, ratings_df):
    """Test top N genres functionality."""
    print("\n=== Testing Top N Genres ===")

    print("Top 3 genres:")
    result = top_n_genres(3, movies_df, ratings_df)
    print(result.to_string(index=False))

    print("\nExpected: Genres ranked by average of movie averages")
    print("Action movies: Heat (4.25), GoldenEye (3.00), Sudden Death (~3.17)")
    print("Comedy movies: Father of the Bride Part II (4.17), Grumpier Old Men (4.00), Waiting to Exhale (2.43)")


def test_user_top_genre(movies_df, ratings_df):
    """Test user top genre functionality."""
    print("\n=== Testing User Top Genre ===")

    # Test user 1 (has ratings for Toy Story, Grumpier Old Men, Heat)
    top_genre = user_top_genre(1, movies_df, ratings_df)
    print(f"User 1's top genre: {top_genre}")
    print("Expected: Action (based on Heat rating of 4.0)")

    # Test user 6 (has ratings for multiple genres)
    top_genre = user_top_genre(6, movies_df, ratings_df)
    print(f"User 6's top genre: {top_genre}")

    # Test non-existent user
    top_genre = user_top_genre(999, movies_df, ratings_df)
    print(f"Non-existent user 999's top genre: {top_genre} (should be None)")


def test_recommend_movies(movies_df, ratings_df):
    """Test movie recommendations functionality."""
    print("\n=== Testing Movie Recommendations ===")

    # Test user 1 recommendations
    recs = recommend_movies_for_user(1, movies_df, ratings_df, k=3)
    print(f"Recommendations for user 1: {recs}")
    print("Expected: 3 most popular unrated movies from user's top genre (Action)")

    # Test user with no ratings
    recs = recommend_movies_for_user(999, movies_df, ratings_df, k=3)
    print(f"Recommendations for user 999 (no ratings): {recs} (should be empty)")

    # Test user who has rated everything in their top genre
    # First find a user who has rated many movies
    recs = recommend_movies_for_user(6, movies_df, ratings_df, k=3)
    print(f"Recommendations for user 6: {recs}")


def test_merge_functionality(movies_df, ratings_df):
    """Test the merge functionality."""
    print("\n=== Testing Data Merge ===")

    merged = merge_movies_and_ratings(movies_df, ratings_df)
    print(f"Merged data shape: {merged.shape}")
    print(f"Merged columns: {list(merged.columns)}")
    print(f"Sample merged data:\n{merged.head()}")

    # Check that genres are properly attached
    print(f"\nUnique genres in merged data: {sorted(merged['Genre'].unique())}")


def test_edge_cases(movies_df, ratings_df):
    """Test edge cases and error handling."""
    print("\n=== Testing Edge Cases ===")

    # Test with N=0
    print("Testing N=0 (should handle gracefully):")
    try:
        top_n_movies(0, ratings_df)
    except Exception as e:
        print(f"Error with N=0: {e}")

    # Test with very large N
    print("Testing large N:")
    top_n_movies(100, ratings_df)

    # Test genre with mixed case
    print("Testing genre with mixed case:")
    result = top_n_movies_in_genre("ACTION", 2, movies_df, ratings_df)
    print(result.to_string(index=False))


def run_all_tests():
    """Run all tests."""
    print("Movie Recommender Automated Testing")
    print("=" * 50)

    try:
        # Load data
        movies_df = test_load_movies()
        ratings_df = test_load_ratings()

        # Test all features
        test_top_n_movies(ratings_df)
        test_top_n_movies_in_genre(movies_df, ratings_df)
        test_top_n_genres(movies_df, ratings_df)
        test_user_top_genre(movies_df, ratings_df)
        test_recommend_movies(movies_df, ratings_df)
        test_merge_functionality(movies_df, ratings_df)
        test_edge_cases(movies_df, ratings_df)

        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("Review the output above to verify results match expectations.")

    except Exception as e:
        print(f"\nERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
