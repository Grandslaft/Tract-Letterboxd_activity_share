import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

import os
import global_parameters as gp

from ..base import letterboxd_frame
from ..scripts.lbHistory import (
    validate_username, crawl_watchlist,
    save_to_csv
)
from ..scripts.shared_functions import (
    get_last_page, crawl_movies, 
    crawl_detailed_movies, extract_ratings,
    run_threaded_tasks
)

import threading
import queue

watchlist_csv_file = 'watchlist_csv_file.csv'

def extract_history(master):
    # Create an instance of the frame
    letterboxd_frame = master.script_frame

    # Adding a new label dynamically
    letterboxd_frame.scrape_ratings = ctk.CTkCheckBox(
        letterboxd_frame, text="Scrape ratings?", 
        onvalue=True, offvalue=False
    )
    letterboxd_frame.scrape_ratings.grid(
        row=1, column=0, 
        padx=gp.ELEMENTS_PAD,
        pady=(0, gp.ELEMENTS_PAD),
        sticky='nsew'
    )
    
    letterboxd_frame.scrape_watchlist = ctk.CTkCheckBox(
        letterboxd_frame, text="Scrape watchlist?",
        onvalue=True, offvalue=False
    )
    letterboxd_frame.scrape_watchlist.grid(
        row=2, column=0, 
        padx=gp.ELEMENTS_PAD,
        pady=(0, gp.ELEMENTS_PAD),
        sticky='nsew'
    )
    
    letterboxd_frame.export_button = ctk.CTkButton(
        letterboxd_frame, text="Extract history", 
        command=lambda self=letterboxd_frame: export_function(self=self),
    )
    letterboxd_frame.export_button.grid(
        row=3, column=0, 
        padx=gp.ELEMENTS_PAD,
        pady=(0, gp.ELEMENTS_PAD),
        sticky='nsew'
    )

def export_function(self):
    self.file_path = filedialog.askdirectory(
            initialdir=self.master.save_path,
            title="Choose save directory"
        )
    
    process_watched(self)
    watchlist_scrape(self)
    
    
def process_watched(self):
    # Step 1: Find the last page number for watched movies
    last_page_queue = run_in_thread(get_last_page, self.base_url)
    check_result_queue(self, last_page_queue, process_last_page)

def process_last_page(self, last_page):
    # Step 2: Crawl all pages to collect movie URLs
    movie_urls_queue = run_in_thread(crawl_movies, last_page, self.base_url)
    check_result_queue(self, movie_urls_queue, process_movie_urls)

def process_movie_urls(self, movie_urls):
    # Step 3: Crawl detailed movie pages to extract TMDb links
    movie_data_queue = run_in_thread(crawl_detailed_movies, movie_urls)
    check_result_queue(self, movie_data_queue, ratings_scrape)

def ratings_scrape(self, movie_data):
    def get_last_ratings_page(self):
        last_ratings_page_queue = run_in_thread(get_last_page, self.base_url)
        check_result_queue(self, last_ratings_page_queue, get_ratings)
    
    def get_ratings(self, last_ratings_page):
        ratings_url = f"https://letterboxd.com/{self.username.get()}/films/by/entry-rating/"
        task_args_list = [(ratings_url + f"page/{page}/",) for page in range(1, last_ratings_page + 1)]
        ratings_queue = run_in_thread(run_threaded_tasks, extract_ratings, task_args_list)
        check_result_queue(self, ratings_queue, save_csv)
    
    def save_csv(self, ratings_mas):
        ratings_data = {}
        for dictionary in ratings_mas:
            ratings_data.update(dictionary)
            
        save_to_csv(self.file_path, movie_data, ratings_data)
            
    if self.scrape_ratings.get():
        # If ratings scraping is selected, scrape from the ratings page
        get_last_ratings_page(self)
    else:
        ratings = None
        save_to_csv(self.file_path, movie_data, ratings)

def watchlist_scrape(self):
    def get_watchlist(self):
        watchlist = run_in_thread(crawl_watchlist, self.username.get())
        check_result_queue(self, watchlist, get_watchlist_details)
        
    def get_watchlist_details(self, watchlist_urls):
        watchlist_movies_info = run_in_thread(crawl_detailed_movies, watchlist_urls)
        check_result_queue(self, watchlist_movies_info, save_csv)
    
    def save_csv(self, watchlist_movies_data):
        save_to_csv(self.file_path, watchlist_movies_data, csv_file_name=watchlist_csv_file)

    if self.scrape_watchlist.get():
        get_watchlist(self)
        
    
def run_in_thread(func, *args, **kwargs):
    result_queue = queue.Queue()

    def queued_func(queue, *args, **kwargs):
        result = func(*args, **kwargs)
        queue.put(result)

    thread = threading.Thread(target=queued_func, args=(result_queue, *args), kwargs=kwargs)
    thread.start()
    
    return result_queue

def check_result_queue(self, result_queue, callback=None):
    try:
        # Try to get the result from the queue
        data = result_queue.get_nowait()
        if callback is None:
            return data
        callback(self, data)
    # If no result yet, keep checking
    except queue.Empty:
        self.master.after(100, check_result_queue, self, result_queue, callback)
        