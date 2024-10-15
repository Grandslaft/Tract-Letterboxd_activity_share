import tkinter as tk
import customtkinter as ctk

import os
import global_parameters as gp

from letterboxd.base import letterboxd_frame

from letterboxd.widgets import (
    extract_list,
    compare_histories
)

from letterboxd.widgets.extract_history import extract_history

gp.CURRENT_DIR = os.path.dirname(__file__)

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
gp.Light_mode('System')
ctk.set_default_color_theme(os.path.join(gp.CURRENT_DIR,'theme.json'))

LB_buttons = {
    "Watch history": extract_history,
    # "Extract list": extract_list,
    # "Compare histories": compare_histories
}
trakt_buttons = {
    
}

def choose_service(generate_buttons):
    def fetch_scripts(self, *args, **kwargs):
        chosen_service = args[0]
        match chosen_service:
            case 'Letterboxd':
                generate_buttons(self, LB_buttons)
            case 'Trakt':
                generate_buttons(self, trakt_buttons)
    return fetch_scripts

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
    
        # configure window
        self.title("Tract-Letterboxd activity share")
        self.geometry(f"{700}x{500}")
        self.minsize(700, 500)
        
        # configure grid layout (3x3)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.save_path = gp.CURRENT_DIR
        
        self.sidebar_frame = ctk.CTkFrame(self, width=300)
        self.sidebar_frame.grid(
            row=0, column=0, 
            sticky="nsew"
        )
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        
        self.service_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["Letterboxd", "Trakt"],
            corner_radius=gp.CORNER_RADIUS,
            dropdown_fg_color=["#e6e7ed", "#1a1b26"],
            dropdown_hover_color=["#325882", "#324578"],
            command=self.generate_buttons
        )
        self.service_optionemenu.grid(
            row=0, column=0, 
            padx=gp.INNER_PAD, 
            pady=(gp.OUTER_PAD, gp.INNER_PAD),
            sticky='ew'
        )
        
        self.sidebar_buttons_frame = ctk.CTkScrollableFrame(
            self.sidebar_frame, 
            fg_color=["#e6e7ed", "#1a1b26"],
            corner_radius=gp.CORNER_RADIUS,
        )
        self.sidebar_buttons_frame.grid(
            row=1, column=0, 
            padx=gp.INNER_PAD, 
            pady=(0, gp.INNER_PAD),
            sticky="nsew"
        )
        self.sidebar_buttons_frame.grid_columnconfigure(0, weight=1)
        
        # light theme of the GUI
        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Appearance mode:", 
            anchor="w"
        )
        self.appearance_mode_label.grid(
            row=3, column=0, 
            padx=gp.INNER_PAD, 
            pady=(0, gp.INNER_PAD), 
            sticky='ew'
        )
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["System", "Light", "Dark"],
            corner_radius=gp.CORNER_RADIUS,
            dropdown_fg_color=["#e6e7ed", "#1a1b26"],
            dropdown_hover_color=["#325882", "#324578"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(
            row=3, column=0, 
            padx=gp.INNER_PAD, 
            pady=(0, gp.OUTER_PAD),
            sticky='ew'
        )

        self.script_frame = letterboxd_frame(
            self, 
            fg_color=["#d6d8df", "#1a1b26"],
            corner_radius=gp.CORNER_RADIUS
        )
        self.script_frame.grid(
            row=0, column=1, 
            padx=gp.OUTER_PAD, 
            pady=gp.OUTER_PAD, 
            sticky="nsew"
        )
        
        self.generate_buttons('Letterboxd')
        
    @choose_service
    def generate_buttons(self, service_scripts: str):
        self.sidebar_button = dict()
        for ind, button_info in enumerate(service_scripts.items()):
            button_name, widget = button_info
            self.sidebar_button[button_name] = ctk.CTkButton(
                self.sidebar_buttons_frame,
                text=button_name,
                height=28,
                corner_radius=gp.CORNER_RADIUS,
                command=lambda master=self: widget(master)
            )
            self.sidebar_button[button_name].grid(
                row=ind, column=0, 
                padx=gp.ELEMENTS_PAD, 
                pady=gp.INNER_PAD, 
                sticky='ew'
            )
    
    # handler for the button click, which calls 
    def function_call(self, function_number):
        self.flag = function_number # flag to know what function's been called
    
    # Appearance changer
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode) # change appearance in custom_tkinter
        gp.Light_mode(new_appearance_mode) # change global parameter to change others' appearance
        
    def show_error_message(self, message):
        # Create the error label if it doesn't exist already
        self.error_label = ctk.CTkLabel(
            master=self,  # Or your main window or frame
            text=message,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="red",  # Background color of the label
            text_color="white",  # Color of the text
            corner_radius=10
        )
        
        # Position it to cover a portion of the screen
        self.error_label.place(relx=0.5, rely=0.05, anchor='center')
        
        # Optionally, hide the message after a few seconds
        self.after(3000, self.error_label.destroy)  # This will destroy the label after 3 seconds

if __name__ == "__main__":
    app = App()
    app.mainloop()