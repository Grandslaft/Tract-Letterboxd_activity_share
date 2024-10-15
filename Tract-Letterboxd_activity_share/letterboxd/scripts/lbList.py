import requests
import csv

from shared_functions import (
    get_last_page, crawl_movies, 
    crawl_detailed_movies
)

# Define the header for the output CSV
csv_file = "list.csv"
csv_header = ["Letterboxd URL", "TMDB ID", "Type"]

# Function to save the extracted data to a CSV file
def save_to_csv(movie_data):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        writer.writerows(movie_data)
    
    # Feedback after saving
    print(f"- Movies/shows saved to {csv_file}")

# Function to get the Letterboxd list URL and validate it
def get_letterboxd_list_url():
    while True:
        list_url = input("Enter the Letterboxd list URL (e.g., https://letterboxd.com/username/list/some-list/): ").strip()

        # Validate the URL by trying to access the first page
        try:
            response = requests.get(list_url)
            if response.status_code == 200:
                return list_url
            else:
                print(f"Invalid URL or the page doesn't exist. Please try again.")
        except requests.RequestException:
            print("Error accessing the page. Please check your internet connection and try again.")

# Main function to run the script
if __name__ == "__main__":
    # Get the user's Letterboxd list URL
    base_url = get_letterboxd_list_url()
    
    # Find the last page number
    last_page = get_last_page(base_url)
    
    # Crawl all pages to collect movie URLs
    movie_urls = crawl_movies(last_page, base_url)
    
    # Crawl detailed movie pages to extract TMDb links (preserving order)
    movie_data = crawl_detailed_movies(movie_urls)
    
    # Save the data to CSV
    save_to_csv(movie_data)

    print("Script finished.")
