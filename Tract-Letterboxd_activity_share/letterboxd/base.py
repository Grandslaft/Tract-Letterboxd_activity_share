import tkinter as tk
import customtkinter as ctk

import threading

import global_parameters as gp

from .scripts.lbHistory import validate_username

class letterboxd_frame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)
        
        self.login_frame = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        self.login_frame.grid(
            row=0, column=0, 
            padx=gp.INNER_PAD, 
            pady=gp.INNER_PAD, 
            sticky="nsew"
        )
        self.login_frame.grid_columnconfigure((0,1), weight=1)
        self.login_frame.grid_rowconfigure(0, weight=1)
        
        self.login_label = ctk.CTkLabel(
                self.login_frame, 
                text='Username',
                font=ctk.CTkFont(
                    size=14,
                ),
            )
        
        self.login_label.grid(
            row=0, column=0, 
            padx=(0, gp.INNER_PAD),
            pady=(0, gp.ELEMENTS_PAD),
            sticky='nsew'
        )
        
        self.username = ctk.StringVar(self.login_frame, value='')
        self.login_input = ctk.CTkEntry(
            self.login_frame, 
            textvariable = self.username,
            placeholder_text='Enter your username e.g. Grandslaft',
        )
        self.login_input.grid(
            row=1, column=0, 
            padx=(0, gp.INNER_PAD),
            sticky='nsew'
        )
        
        self.login_input.bind('<KeyRelease>', self.on_entry_change)
        
        # Bind events to manage placeholder
        self.login_input.bind("<FocusIn>", self.clear_placeholder)
        self.login_input.bind("<FocusOut>", self.set_placeholder)

        # Set the placeholder initially if needed
        self.set_placeholder()

    def clear_placeholder(self, event):
        if self.username.get() == 'Enter your username e.g. Grandslaft':
            self.username.set('')  # Clear placeholder on focus
            self.login_input.configure(placeholder_text_color='white')  # Change text color if needed

    def set_placeholder(self, event=None):
        if not self.username.get():
            self.username.set('Enter your username e.g. Grandslaft')  # Set placeholder if empty
            self.login_input.configure(placeholder_text_color='lightgray')  # Change text color for placeholder

    def on_entry_change(self, event):
        # Cancel any previously scheduled validation (debouncing)
        if hasattr(self, 'debounce_id'):
            self.after_cancel(self.debounce_id)
        
        # Schedule the validation after a delay (e.g., 300 ms)
        self.debounce_id = self.after(100, self.start_validation_thread)

    def start_validation_thread(self):
        # Start a new thread for the validation to avoid blocking the UI
        validation_thread = threading.Thread(target=self.validate_username_thread)
        validation_thread.start()

    def validate_username_thread(self):
        # Perform the validation request here
        new_base_url, error = validate_username(self.username.get())
        
        # Update the UI with the result in the main thread
        self.master.after(0, self.update_base_url, new_base_url, error)

    def update_base_url(self, new_base_url, error):
        # Update the base_url and any related UI elements
        self.base_url = new_base_url
        if error is not None:
            self.master.show_error_message(error)
