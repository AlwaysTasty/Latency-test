import tkinter as tk
from tkinter import messagebox
import random
import time
import os 
from PIL import Image, ImageTk

#Config
MIN_DELAY_S = 1.0  
MAX_DELAY_S = 2.0  
IMAGE_FILENAME = "purple.png" 
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Reaction Time Test")

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        center_x = int(screen_width/2 - WINDOW_WIDTH / 2)
        center_y = int(screen_height/2 - WINDOW_HEIGHT / 2 - 50)

        self.master.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{center_x}+{center_y}')
        self.master.resizable(False, False) 

        self.start_time = None
        self.is_waiting_for_click = False
        self.is_test_running = False
        self.timer_id = None

        try:
            # --- FIX: Get the absolute path to the image ---
            # This finds the folder where the script is running
            script_directory = os.path.dirname(os.path.abspath(__file__))
            # This combines the folder path with the filename
            image_path = os.path.join(script_directory, IMAGE_FILENAME)
            
            self.target_image = Image.open(image_path)
            self.target_image.thumbnail((WINDOW_WIDTH - 50, WINDOW_HEIGHT // 2))
            self.target_photo = ImageTk.PhotoImage(self.target_image)
        except FileNotFoundError:
            # Shows the path it tried to look in, helping debug if it fails again
            messagebox.showerror("Error", f"Image file not found at:\n{image_path}\n\nMake sure '{IMAGE_FILENAME}' is in the same folder.")
            self.master.destroy()
            return
            
        self.setup_widgets()
        
        self.master.bind("<Button-1>", self.on_click)

    def setup_widgets(self):
        control_frame = tk.Frame(self.master, pady=10)
        control_frame.pack()

        self.instruction_label = tk.Label(control_frame, text="Click the center area to begin.", font=("Helvetica", 14))
        self.instruction_label.pack()

        self.result_label = tk.Label(control_frame, text="Reaction Time: -", font=("Helvetica", 16, "bold"), pady=10)
        self.result_label.pack()
        
        self.image_label = tk.Label(self.master, text="[ Click Here to Start ]", font=("Helvetica", 24, "bold"), fg="#555555", bg="#f0f0f0", relief="groove")
        self.image_label.pack(pady=20, expand=True, fill=tk.BOTH, padx=50)
        self.image_label.bind("<Button-1>", self.on_click)

        history_frame = tk.Frame(self.master, pady=10)
        history_frame.pack(fill=tk.X, padx=20)
        
        title_frame = tk.Frame(history_frame)
        title_frame.pack(fill=tk.X)
        
        history_title_label = tk.Label(title_frame, text="History (ms)", font=("Helvetica", 12, "underline"))
        history_title_label.pack(side=tk.LEFT)
        
        self.average_label = tk.Label(title_frame, text="Average: ---", font=("Helvetica", 12))
        self.average_label.pack(side=tk.RIGHT)
        
        self.history_listbox = tk.Listbox(history_frame, height=5, font=("Courier", 12))
        self.history_listbox.pack(fill=tk.X, expand=True, pady=(5,5))

        self.clear_button = tk.Button(history_frame, text="Clear History", command=self.clear_history)
        self.clear_button.pack()

    def start_test(self):
        self.is_test_running = True
        self.is_waiting_for_click = False
        
        self.result_label.config(text="Reaction Time: ...")
        self.instruction_label.config(text="Wait for the image...")
        self.image_label.config(image='', text="Wait for it...", font=("Helvetica", 32), bg="#e0e0e0")

        delay_ms = int(random.uniform(MIN_DELAY_S, MAX_DELAY_S) * 1000)
        self.timer_id = self.master.after(delay_ms, self.show_image)
        
    def show_image(self):
        self.image_label.config(image=self.target_photo, text="", bg="white") 
        self.instruction_label.config(text="Click Now!")
        self.is_waiting_for_click = True
        self.start_time = time.perf_counter()

    def on_click(self, event):
        if not self.is_test_running:
            self.start_test()
            return "break" 

        if not self.is_waiting_for_click:
            if self.timer_id:
                self.master.after_cancel(self.timer_id)   
            self.result_label.config(text="False Start!")
            self.image_label.config(text="Too Soon!\nClick to Try Again", image='', bg="#ffcccc")
            self.log_result("Too soon")
            self.end_test()
            
        elif self.is_waiting_for_click:
            end_time = time.perf_counter()
            reaction_time_ms = (end_time - self.start_time) * 1000
            
            self.result_label.config(text=f"Reaction Time: {reaction_time_ms:.2f} ms")
            self.image_label.config(text=f"{reaction_time_ms:.0f} ms\nClick to Play Again", image='', bg="#ccffcc")
            self.log_result(f"{reaction_time_ms:.2f}")
            self.end_test()
        
        return "break"

    def end_test(self):
        self.is_waiting_for_click = False
        self.is_test_running = False
        self.timer_id = None
        self.instruction_label.config(text="Click the center area to restart.")
    
    def log_result(self, result_text):
        self.history_listbox.insert(0, result_text)
        self.update_average()

    def clear_history(self):
        self.history_listbox.delete(0, tk.END)
        self.update_average()

    def update_average(self):
        items = self.history_listbox.get(0, tk.END)
        valid_times = []
        for item in items:
            try:
                time_val = float(item)
                valid_times.append(time_val)
            except ValueError:
                continue
        
        if valid_times:
            average = sum(valid_times) / len(valid_times)
            self.average_label.config(text=f"Average: {average:.2f} ms")
        else:
            self.average_label.config(text="Average: ---")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()