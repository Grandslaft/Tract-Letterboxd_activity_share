import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

from shared_functions import (
    extract_movie_urls, extract_ratings,
    get_last_page, run_threaded_tasks
)

# Define the header for the output CSV
csv_file = "recommendations.csv"

# Function to get the last page number of the user's watched movies list
def get_last_page(base_url):
    first_page_url = base_url + "/page/1/"
    response = requests.get(first_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    pagination = soup.find('div', class_='paginate-pages')
    if pagination:
        last_page_link = pagination.find_all('a')[-1].get('href')
        last_page_number = int(last_page_link.split('/page/')[-1].strip('/'))
    else:
        last_page_number = 1

    return last_page_number

# Function to crawl multiple pages using ThreadPoolExecutor for concurrent execution
def crawl_movies_concurrent(user_url, scrape_ratings=False):
    last_page = get_last_page(user_url)
    all_movies = {}

    # Use ThreadPoolExecutor for concurrent page crawling
    with ThreadPoolExecutor(max_workers=10) as executor:
        task_args_list = [(f"{user_url}/page/{page}/",) for page in range(1, last_page + 1)]
        if scrape_ratings:
            threads = run_threaded_tasks(extract_movie_urls, task_args_list, 10)
        else:
            threads = run_threaded_tasks(extract_movie_urls, task_args_list, 10)
        
    # Collect results as they complete
    for thread in as_completed(threads):
        if scrape_ratings:
            all_movies.update(thread.result())
        else:
            movie_urls = thread.result()
            all_movies.update({url: None for url in movie_urls})
    
    return all_movies

# Function to extract the username from the original Letterboxd URL
def extract_username(url):
    return url.split("/")[-2]  # This will correctly extract the username from the original URL

# Function to compare watched movies between User 1 and User 2
def compare_users(user1_movies, user2_movies):
    recommendations = {url: rating for url, rating in user1_movies.items() if url not in user2_movies}
    return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)

# Function to save the recommendations to a CSV file
def save_to_csv(recommendations, user1_name):
    csv_header = ["Letterboxd URL", f"{user1_name} ratings"]
    
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        for movie_url, rating in recommendations:
            writer.writerow([movie_url, rating])

    print(f"Recommendations saved to {csv_file}")

# Main function to execute the comparison
def main():
    print("Example input for Letterboxd URL: https://letterboxd.com/nigeljordanw/")
    user1_url_input = input("Enter Letterboxd URL for User that has watched: ").strip()
    user2_url_input = input("Enter Letterboxd URL for User that hasn't watched: ").strip()
    
    # Extract usernames from original URLs
    user1_name = extract_username(user1_url_input)
    user2_name = extract_username(user2_url_input)
    
    # Modify the URLs for scraping
    user1_url = user1_url_input + "films/by/entry-rating/"
    user2_url = user2_url_input + "films/"
    
    # Crawl watched movies with ratings for User 1
    print(f"Crawling watched movies for {user1_name} from {user1_url}")
    user1_movies = crawl_movies_concurrent(user1_url, scrape_ratings=True)

    # Crawl watched movies without ratings for User 2
    print(f"Crawling watched movies for {user2_name} from {user2_url}")
    user2_movies = crawl_movies_concurrent(user2_url, scrape_ratings=False)

    # Compare watched movies and get recommendations
    recommendations = compare_users(user1_movies, user2_movies)

    # Save recommendations to CSV
    save_to_csv(recommendations, user1_name)

if __name__ == "__main__":
    main()
