import requests
import csv
import math
import os

from .shared_functions import (
    get_last_page, crawl_movies
)

# Define the header for the output CSV files
csv_file_name = "watched_movies_tmdb.csv"
watchlist_csv_file_name = "watchlist_tmdb.csv"
csv_header = ["Letterboxd URL", "TMDB ID", "Type"]

# Function to save the extracted data to a CSV file
def save_to_csv(save_path, movie_data, ratings_data=None, csv_file_name=csv_file_name):
    if ratings_data:
        csv_header.append("Rating")
    movie_data_reshaped = [movie_data[i:i+3] for i in range(0, len(movie_data), 3)]
    with open(os.path.join(save_path, csv_file_name), mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        for movie in movie_data_reshaped:
            row = list(movie)
            if ratings_data and movie[0] in ratings_data:
                # Ensure the rating is a whole number for Trakt (rounded after doubling)
                trakt_rating = math.ceil(ratings_data[movie[0]] * 2)
                row.append(trakt_rating)  # Add the Trakt-compliant rating
            writer.writerow(row)

# Function to get the Letterboxd username and validate the input URL
def validate_username(username: str):
    username = username.strip()
    base_url = f"https://letterboxd.com/{username}/films"
    
    # Validate the URL by trying to access the first page
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            return base_url, None
        
        error = "Invalid username or the page doesn't exist. Please try again."
        return base_url, error
    
    except requests.RequestException:
        error = "Error accessing the page. Please check your internet connection and try again."
        return base_url, error

# Function to crawl the watchlist
def crawl_watchlist(username):
    watchlist_url = f"https://letterboxd.com/{username}/watchlist/"
    last_page = get_last_page(watchlist_url)
    watchlist_movies = crawl_movies(last_page, watchlist_url)  # Reusing the function to scrape watchlist
    return watchlist_movies
