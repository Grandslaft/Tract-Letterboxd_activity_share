import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Helper function to run tasks using ThreadPoolExecutor
def run_threaded_tasks(task_func, task_args_list, in_order=False, max_workers=20):
    """
    Runs tasks concurrently using ThreadPoolExecutor.

    Parameters:
    - task_func: The function to be executed.
    - task_args_list: List of arguments for each function call.
    - max_workers: The maximum number of threads to use.

    Returns:
    - List of results from each function execution.
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        threads = [executor.submit(task_func, *args) for args in task_args_list]
        if in_order:
            # Collect the results in the correct order
            for thread in threads:
                movie_urls = thread.result()
                if isinstance(movie_urls, dict):
                    results.append(movie_urls)
                else:
                    results.extend(movie_urls)
        else:
            # Collect the results as they are completed
            for thread in as_completed(threads):
                movie_urls = thread.result()
                if isinstance(movie_urls, dict):
                    results.append(movie_urls)
                else:
                    results.extend(movie_urls)
    return results

# Function to extract watched movies (without ratings)
def extract_movie_urls(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    movie_urls = []
    movie_items = soup.find_all('li', class_='poster-container')
    
    for li in movie_items:
        lazy_load_div = li.find('div', class_='really-lazy-load')
        if lazy_load_div and lazy_load_div.get('data-target-link'):
            movie_url = "https://letterboxd.com" + lazy_load_div['data-target-link']
            movie_urls.append(movie_url)
    
    return movie_urls

# Function to extract movie URLs and (optional) ratings from the ratings page
def extract_ratings(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    ratings_data = {}
    
    # Get all rated movie containers (list items)
    movie_items = soup.find_all('li', class_='poster-container')
    
    for li in movie_items:
        lazy_load_div = li.find('div', class_='really-lazy-load')
        if lazy_load_div and lazy_load_div.get('data-target-link'):
            movie_url = "https://letterboxd.com" + lazy_load_div['data-target-link']
            rating_tag = li.find('span', class_='rating')
            if rating_tag:
                # Find the class that contains 'rated-' and extract the rating value
                rating_class = next((cls for cls in rating_tag['class'] if 'rated-' in cls), None)
                if rating_class:
                    # Convert rating by stripping 'rated-' and dividing by 2 to map to the 10-point scale
                    letterboxd_rating = float(rating_class.replace('rated-', '')) / 2
                    ratings_data[movie_url] = letterboxd_rating
    
    return ratings_data

# Function to extract TMDb info from the detailed movie page
def extract_tmdb_info(movie_url):
    response = requests.get(movie_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the TMDb button by class and text content
    tmdb_button = soup.find('a', class_='micro-button track-event', string='TMDb')
    
    if tmdb_button:
        tmdb_link = tmdb_button.get('href')
        
        # Extract TMDB ID and type (movie or tv)
        if "/movie/" in tmdb_link:
            tmdb_id = tmdb_link.split("/movie/")[1].strip("/")
            media_type = "movie"
        elif "/tv/" in tmdb_link:
            tmdb_id = tmdb_link.split("/tv/")[1].strip("/")
            media_type = "show"
        else:
            tmdb_id = None
            media_type = None
        
        return movie_url, tmdb_id, media_type
    else:
        return movie_url, None, None

# Function to find the last page number by parsing pagination
def get_last_page(base_url):
    first_page_url = base_url + "/page/1/"
    response = requests.get(first_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find pagination container
    pagination = soup.find('div', class_='paginate-pages')
    
    if pagination:
        # Find the last page number by looking for the last link in the pagination
        last_page_link = pagination.find_all('a')[-1].get('href')
        last_page_number = int(last_page_link.split('/page/')[-1].strip('/'))
    else:
        # If no pagination is found, we assume there's only one page
        last_page_number = 1

    return last_page_number

def get_urls(crawl_movies_func):
    def wrapper(*args, **kwargs):
        movie_urls = crawl_movies_func(*args, **kwargs)
        return movie_urls
    
    return wrapper

@get_urls
def crawl_movies(last_page, base_url, in_order=False):
    task_args_list = [(f"{base_url}/page/{page}/",) for page in range(1, last_page + 1)]
    return run_threaded_tasks(extract_movie_urls, task_args_list, in_order)

@get_urls
def crawl_detailed_movies(movie_urls, in_order=True):
    task_args_list = [(url,) for url in movie_urls]
    return run_threaded_tasks(extract_tmdb_info, task_args_list, in_order)