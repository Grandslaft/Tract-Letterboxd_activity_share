# Main function to run the script
if __name__ == "__main__":
    # Get the user's Letterboxd URL and username
    base_url, username = get_letterboxd_url()
    
    # Ask if the user wants to scrape ratings
    scrape_ratings = input("Do you want to scrape ratings? (yes/no): ").strip().lower() == "yes"
    
    # Ask if the user wants to scrape their watchlist
    scrape_watchlist = input("Do you want to scrape your watchlist? (yes/no): ").strip().lower() == "yes"

    # Find the last page number for watched movies
    last_page = get_last_page(base_url)
    
    # Crawl all pages to collect movie URLs
    movie_urls = crawl_movies(last_page, base_url)
    
    # Crawl detailed movie pages to extract TMDb links
    movie_data = crawl_detailed_movies(movie_urls)

    ratings_data = None
    if scrape_ratings:
        # If ratings scraping is selected, scrape from the ratings page
        ratings_url = f"https://letterboxd.com/{username}/films/by/entry-rating/"
        ratings_data = {}
        last_ratings_page = get_last_page(ratings_url)
        for page in range(1, last_ratings_page + 1):
            page_url = ratings_url + f"page/{page}/"
            ratings_data.update(extract_ratings(page_url))
    
    # Optionally crawl the watchlist
    if scrape_watchlist:
        watchlist_urls = crawl_watchlist(username)
        watchlist_data = crawl_detailed_movies(watchlist_urls)
        # Save the watchlist to a separate CSV
        save_to_csv(watchlist_data, csv_file=watchlist_csv_file)

    # Save the watched movies data to CSV
    save_to_csv(movie_data, ratings_data)

    print("Script finished.")