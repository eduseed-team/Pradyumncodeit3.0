import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime
import requests

DATA_FILE = "fitness_data.json"

try:
    from config import NUTRITIONIX_APP_ID, NUTRITIONIX_API_KEY
except ImportError:
    NUTRITIONIX_APP_ID = ""
    NUTRITIONIX_API_KEY = ""

MICROGRAVITY_CAL_FACTOR = 0.5

def fetch_nutrition_data(query):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
        "Content-Type": "application/json"
    }
    data = {"query": query}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 429:
            messagebox.showwarning("API Limit Reached", "API usage limit has been reached. Please enter nutrition info manually.")
            return None
        response.raise_for_status()
        return response.json()
    except Exception as e:
        messagebox.showerror("API Error", f"Failed to fetch nutrition info: {e}")
        return None

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            os.rename(DATA_FILE, DATA_FILE + ".corrupt")
            messagebox.showwarning("Data Corrupted", "Existing fitness data is corrupted. Backup created.")
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Astronaut Fitness Tracker")
        self.root.configure(bg="#f4f4f4")
        self.root.resizable(False, False)
        self.data = load_data()

        if not NUTRITIONIX_APP_ID or not NUTRITIONIX_API_KEY:
            messagebox.showwarning(
                "Missing API Configuration",
                "Nutrition API keys are not set.\n\nMeal nutrition auto-fill will not work."
            )

        self.exercises_dict = {
            "Jumping Jacks": 8, "Push-ups": 7, "Sit-ups": 6, "Pull-ups": 9, "Squats": 6,
            "Lunges": 6, "Plank": 4, "Mountain Climbers": 8, "High Knees": 8, "Wall Sit": 5,
            "Crunches": 6, "Leg Raises": 5, "Glute Bridges": 5, "Arm Circles": 3,
            "Calf Raises": 4, "Step-ups": 6, "Chair Dips": 5, "Side Plank": 4,
            "Russian Twists": 6, "Burpees": 10
        }

        self.walking_speeds = {
            "Very Low (1 km/h)": 2,
            "Low (2 km/h)": 3,
            "Moderate (3 km/h)": 4,
            "High (4 km/h)": 5,
            "Very High (5 km/h)": 6,
        }
        self.jogging_speeds = {
            "Low (6 km/h)": 7,
            "Moderate (7 km/h)": 8,
            "High (8 km/h)": 9,
        }

        self.astronaut_name = ""
        self.init_login_screen()

    def get_today(self):
        return str(datetime.now().date())

    def create_labeled_entry(self, parent, label_text, var=None, pack=True, info_text=None, **entry_options):
        frame = tk.Frame(parent, bg="#f4f4f4")
        if pack:
            frame.pack(pady=5, fill='x')

        label_frame = tk.Frame(frame, bg="#f4f4f4")
        label_frame.pack(anchor="w", fill='x')

        label = tk.Label(label_frame, text=label_text, bg="#f4f4f4", font=("Helvetica", 12))
        label.pack(side="left")

        if info_text:
            def show_info():
                messagebox.showinfo("Info", info_text)

            info_btn = tk.Button(label_frame, text="ℹ️", bg="#f4f4f4", relief="flat", borderwidth=0,
                                 font=("Helvetica", 12), command=show_info)
            info_btn.pack(side="left", padx=5)

        if var is None:
            var = tk.StringVar()

        entry = tk.Entry(frame, font=("Helvetica", 12), textvariable=var, **entry_options)
        entry.pack(fill='x')

        return var, frame

    def load_user_data(self, name):
        self.astronaut_name = name
        self.display_name = name.title()
        self.user_data = self.data.setdefault(name, {})

    def init_login_screen(self):
        self.clear_root()
        frame = self.build_frame()

        tk.Label(frame, text="Enter Astronaut Name:", font=("Helvetica", 14), bg="#f4f4f4").pack(pady=10)
        self.name_var = tk.StringVar()
        name_entry = tk.Entry(frame, font=("Helvetica", 12), textvariable=self.name_var, width=25)
        name_entry.pack(pady=5)
        name_entry.focus()
        name_entry.bind('<Return>', lambda e: self.start_main_menu())

        tk.Button(frame, text="Continue", command=self.start_main_menu,
                  bg="#4CAF50", fg="white", font=("Helvetica", 12), width=20).pack(pady=15)

    def start_main_menu(self):
        name = self.name_var.get().strip().lower()
        if not name:
            messagebox.showerror("Error", "Please enter a name.")
            return
        self.load_user_data(name)
        self.show_main_menu()

    def show_main_menu(self):
        self.clear_root()
        frame = self.build_frame()

        tk.Label(frame, text=f"Welcome, {self.display_name}", font=("Helvetica", 16, "bold"), bg="#f4f4f4").pack(pady=10)

        buttons = [
            ("Log Exercise", self.log_exercise_screen),
            ("Log Meal", self.log_meal_screen),
            ("Log Movement", self.log_movement_screen),
            ("View Daily Summary", self.view_summary_screen),
            ("Switch User", self.init_login_screen),
            ("Save & Exit", self.exit_app)
        ]

        for text, command in buttons:
            bg_color = "#4CAF50" if text == "Save & Exit" else "#FF5722" if text == "Switch User" else "#21F3E9"
            tk.Button(frame, text=text, width=30, font=("Helvetica", 12),
                      bg=bg_color, fg="black", command=command).pack(pady=5)

    def log_exercise_screen(self):
        self.clear_root()
        frame = self.build_frame()
        tk.Label(frame, text="Log Exercise", font=("Helvetica", 16), bg="#f4f4f4").pack(pady=10)

        exercise_options = list(self.exercises_dict.keys()) + ["Others"]
        self.selected_exercise = tk.StringVar(value=exercise_options[0])
        tk.Label(frame, text="Select Exercise:", bg="#f4f4f4", font=("Helvetica", 12)).pack(anchor="w")
        tk.OptionMenu(frame, self.selected_exercise, *exercise_options, command=lambda e: self.toggle_other_fields()).pack(pady=5)

        self.duration_var, _ = self.create_labeled_entry(frame, "Duration (minutes):", width=30)

        self.other_name_var, self.other_name_frame = self.create_labeled_entry(frame, "Exercise Name (Other):", pack=False, width=30)
        self.other_cal_var, self.other_cal_frame = self.create_labeled_entry(frame, "Calories per Minute:", pack=False, width=30)

        self.exercise_save_btn = tk.Button(frame, text="Save", command=self.save_exercise_dropdown,
                      bg="#4CAF50", fg="white", font=("Helvetica", 12), width=20)
        self.exercise_back_btn = tk.Button(frame, text="Back", command=self.show_main_menu,
                      bg="#777", fg="white", font=("Helvetica", 12), width=20)

        self.exercise_save_btn.pack(pady=15)
        self.exercise_back_btn.pack()

        self.toggle_other_fields()

    def toggle_other_fields(self):
        is_other = self.selected_exercise.get() == "Others"
        if is_other:
            self.other_name_frame.pack(pady=5, fill='x', before=self.exercise_save_btn)
            self.other_cal_frame.pack(pady=5, fill='x', before=self.exercise_save_btn)
        else:
            self.other_name_frame.pack_forget()
            self.other_cal_frame.pack_forget()

    def save_exercise_dropdown(self):
        selected = self.selected_exercise.get()
        date = self.get_today()
        duration, err = self.validate_and_cast(self.duration_var, float)
        if err or duration <= 0:
            messagebox.showerror("Input Error", "Please enter a valid duration.")
            return

        if selected == "Others":
            name = self.other_name_var.get().strip()
            if not name:
                messagebox.showerror("Input Error", "Please enter an exercise name.")
                return
            cal_per_min, err = self.validate_and_cast(self.other_cal_var, float)
            if err or cal_per_min <= 0:
                messagebox.showerror("Input Error", "Calories per minute must be a positive number.")
                return
        else:
            name = selected
            cal_per_min = self.exercises_dict.get(name, 5)

        calories = round(duration * cal_per_min, 2)
        entry = {"exercise": name, "duration": duration, "calories": calories}
        self.user_data.setdefault('exercises', {}).setdefault(date, []).append(entry)
        save_data(self.data)

        messagebox.showinfo("Saved", f"{name} logged!, {calories} Calories burned!")
        self.show_main_menu()

    def log_meal_screen(self):
        self.build_log_screen("Log Meal", [
            ("Meal Name:", "meal", str),
            ("Calories:", "calories", float),
            ("Protein (g):", "protein", float),
            ("Carbs (g):", "carbs", float)
        ], self.save_meal)

    def auto_fill_meal_info(self):
        food_name = self.log_entries.get("meal").get().strip()
        if not food_name:
            messagebox.showerror("Input Error", "Enter a meal name first.")
            return

        result = fetch_nutrition_data(food_name)
        if not result:
            return

        try:
            item = result["foods"][0]
            self.log_entries["calories"].set(str(round(item["nf_calories"], 2)))
            self.log_entries["protein"].set(str(round(item["nf_protein"], 2)))
            self.log_entries["carbs"].set(str(round(item["nf_total_carbohydrate"], 2)))
            messagebox.showinfo("Success", "Nutrition info auto-filled!")
        except (KeyError, IndexError):
            messagebox.showerror("Error", "Could not parse API response.")


    def save_meal(self, entries, entry_types):
        meal_name = entries["meal"].get().strip()
        if not meal_name:
            messagebox.showerror("Input Error", "Meal name cannot be empty.")
            return
        self.save_entry("meals", entries, entry_types)

    def log_movement_screen(self):
        self.clear_root()
        frame = self.build_frame()
        tk.Label(frame, text="Log Movement", font=("Helvetica", 16), bg="#f4f4f4").pack(pady=10)

        tk.Label(frame, text="Select Activity Type:", bg="#f4f4f4", font=("Helvetica", 12)).pack(anchor="w", pady=(0,5))
        self.activity_type = tk.StringVar(value="Walking")

        activity_frame = tk.Frame(frame, bg="#f4f4f4")
        activity_frame.pack(anchor="w", pady=(0,10))

        tk.Radiobutton(activity_frame, text="Walking", variable=self.activity_type, value="Walking",
                       bg="#f4f4f4", font=("Helvetica", 12), command=self.update_speed_options).pack(side="left", padx=10)
        tk.Radiobutton(activity_frame, text="Jogging", variable=self.activity_type, value="Jogging",
                       bg="#f4f4f4", font=("Helvetica", 12), command=self.update_speed_options).pack(side="left", padx=10)

        self.speed_var = tk.StringVar()
        self.speed_frame = tk.Frame(frame, bg="#f4f4f4")
        self.speed_frame.pack(anchor="w", pady=(0,10))
        self.update_speed_options()

        self.duration_var, _ = self.create_labeled_entry(frame, "Duration (minutes):", width=30)

        microgravity_info = (
            "Microgravity Duration is the part of the whole duration spent moving in microgravity (weightless) conditions.\n"
            "It must be less than or equal to the total movement duration."
        )
        self.microgravity_var, _ = self.create_labeled_entry(
            frame,
            "Microgravity Duration (minutes):",
            width=30,
            info_text=microgravity_info
        )

        tk.Button(frame, text="Save", command=self.save_movement,
                  bg="#4CAF50", fg="white", font=("Helvetica", 12), width=20).pack(pady=15)
        tk.Button(frame, text="Back", command=self.show_main_menu,
                  bg="#777", fg="white", font=("Helvetica", 12), width=20).pack()

    def update_speed_options(self):
        for widget in self.speed_frame.winfo_children():
            widget.destroy()

        speeds = self.walking_speeds if self.activity_type.get() == "Walking" else self.jogging_speeds

        tk.Label(self.speed_frame, text="Select Speed:", bg="#f4f4f4", font=("Helvetica", 12)).pack(anchor="w")
        self.speed_var.set(next(iter(speeds)))

        for speed in speeds:
            tk.Radiobutton(self.speed_frame, text=speed, variable=self.speed_var, value=speed,
                           bg="#f4f4f4", font=("Helvetica", 11)).pack(anchor="w")

    def save_movement(self):
        date = self.get_today()

        duration, err_dur = self.validate_and_cast(self.duration_var, float)
        microgravity_duration, err_micro = self.validate_and_cast(self.microgravity_var, float)

        if err_dur or duration <= 0:
            messagebox.showerror("Input Error", "Please enter a valid total duration.")
            return
        if err_micro or microgravity_duration < 0:
            messagebox.showerror("Input Error", "Please enter a valid microgravity duration (>= 0).")
            return
        if microgravity_duration > duration:
            messagebox.showerror("Input Error", "Microgravity duration cannot exceed total duration.")
            return

        activity = self.activity_type.get()
        speed_key = self.speed_var.get()
        if activity == "Walking":
            cal_per_min = self.walking_speeds.get(speed_key, 3)
        else:
            cal_per_min = self.jogging_speeds.get(speed_key, 8)

        normal_duration = duration - microgravity_duration
        calories = round((normal_duration * cal_per_min) + (microgravity_duration * cal_per_min * MICROGRAVITY_CAL_FACTOR), 2)


        entry = {
            "activity": activity,
            "speed": speed_key,
            "duration": duration,
            "microgravity_duration": microgravity_duration,
            "calories": calories
        }

        self.user_data.setdefault('movements', {}).setdefault(date, []).append(entry)
        save_data(self.data)

        messagebox.showinfo("Saved", f"{activity} logged! Calories burned: {calories}")
        self.show_main_menu()

    def validate_and_cast(self, var, cast_type):
        val = var.get().strip()
        try:
            return cast_type(val), False
        except (ValueError, TypeError):
            return None, True

    def view_summary_screen(self):
        self.clear_root()
        frame = self.build_frame()

        tk.Label(frame, text="View Daily Summary", font=("Helvetica", 16), bg="#f4f4f4").pack(pady=10)

        tk.Label(frame, text="Enter date (YYYY-MM-DD):", font=("Helvetica", 12), bg="#f4f4f4").pack()

        date_var = tk.StringVar()
        date_entry = tk.Entry(frame, font=("Helvetica", 12), textvariable=date_var)
        date_entry.pack(pady=5)

        def use_todays_date():
            from datetime import datetime
            date_var.set(datetime.now().strftime("%Y-%m-%d"))

        tk.Button(frame, text="Use Today's Date", command=use_todays_date,
                  bg="#2196F3", fg="white", font=("Helvetica", 10)).pack(pady=(0, 10))

        def show_summary():
            date = date_entry.get()
            try:
                from datetime import datetime
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Input Error", "Date format should be YYYY-MM-DD.")
                return

            exercises = self.user_data.get('exercises', {}).get(date, [])
            meals = self.user_data.get('meals', {}).get(date, [])
            movements = self.user_data.get('movements', {}).get(date, [])

            if not any([exercises, meals, movements]):
                messagebox.showinfo("No Data", f"No data found for {date}.")
                return

            summary_win = tk.Toplevel(self.root)
            summary_win.title(f"Daily Summary for {self.display_name} on {date}")
            summary_win.geometry("600x400")

            text_frame = tk.Frame(summary_win)
            text_frame.pack(fill="both", expand=True)

            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side="right", fill="y")

            summary_text = tk.Text(text_frame, yscrollcommand=scrollbar.set, font=("Helvetica", 11))
            summary_text.pack(fill="both", expand=True)
            scrollbar.config(command=summary_text.yview)

            summary_text.tag_configure("header", font=("Helvetica", 14, "bold"))
            summary_text.tag_configure("subheader", font=("Helvetica", 12, "bold"))
            summary_text.tag_configure("total", foreground="blue", font=("Helvetica", 12, "bold"))

            summary_text.insert("end", f"Summary for {self.display_name} on {date}:\n\n", "header")

            total_calories_burned = 0
            total_calories_gained = 0
            total_protein = 0
            total_carbs = 0

            if exercises:
                summary_text.insert("end", "Exercises:\n", "subheader")
                for e in exercises:
                    summary_text.insert("end", f"- {e['exercise']} for {e['duration']} min, {e['calories']} cal burned.\n")
                    total_calories_burned += e['calories']
                summary_text.insert("end", "\n")

            if movements:
                summary_text.insert("end", "Movements:\n", "subheader")
                for m in movements:
                    summary_text.insert("end", (f"- {m['activity']} at {m['speed']} speed for {m['duration']} min, "
                                               f"Microgravity: {m['microgravity_duration']} min, "
                                               f"{m['calories']} cal burned.\n"))
                    total_calories_burned += m['calories']
                summary_text.insert("end", "\n")

            if meals:
                summary_text.insert("end", "Meals:\n", "subheader")
                for m in meals:
                    summary_text.insert("end", f"- {m['meal']}: {m['calories']} cal, {m['protein']}g protein, {m['carbs']}g carbs\n")
                    total_calories_gained += m['calories']
                    total_protein += m['protein']
                    total_carbs += m['carbs']
                summary_text.insert("end", "\n")

            net_calories = round(total_calories_gained - total_calories_burned, 2)

            summary_text.insert("end", "---- Totals ----\n", "subheader")
            summary_text.insert("end", f"Total Calories Consumed: {total_calories_gained} cal\n")
            summary_text.insert("end", f"Total Protein: {total_protein} g (Expected Daily Protein Intake for an average adult: 50g)\n")
            summary_text.insert("end", f"Total Carbs: {total_carbs} g (Expected Daily Carbs Intake for an average adult: 300g)\n")
            summary_text.insert("end", f"Total Calories Burned: {total_calories_burned} cal\n")
            summary_text.insert("end", f"Net Calorie {'Gain' if net_calories >= 0 else 'Loss'}: {abs(net_calories)} cal\n", "total")

            summary_text.config(state="disabled")

            def copy_to_clipboard():
                self.root.clipboard_clear()
                self.root.clipboard_append(summary_text.get("1.0", "end"))
                messagebox.showinfo("Copied", "Summary copied to clipboard!")

            btn_frame = tk.Frame(summary_win)
            btn_frame.pack(pady=5)

            tk.Button(btn_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Close", command=summary_win.destroy).pack(side="left", padx=5)

        tk.Button(frame, text="Show Summary", command=show_summary,
                  bg="#4CAF50", fg="white", font=("Helvetica", 12), width=20).pack(pady=15)
        tk.Button(frame, text="Back", command=self.show_main_menu,
                  bg="#777", fg="white", font=("Helvetica", 12), width=20).pack()

    def build_frame(self):
        frame = tk.Frame(self.root, padx=20, pady=20, bg="#f4f4f4")
        frame.pack(expand=True)
        return frame

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def exit_app(self):
        if messagebox.askokcancel("Quit", "Do you want to save and exit?"):
            save_data(self.data)
            self.root.destroy()

    def build_log_screen(self, title, fields, save_callback):
        self.clear_root()
        frame = self.build_frame()
        tk.Label(frame, text=title, font=("Helvetica", 16), bg="#f4f4f4").pack(pady=10)

        self.log_entries = {}
        self.log_types = {}

        for label_text, var_name, var_type in fields:
            var = tk.StringVar()
            self.log_entries[var_name] = var
            self.log_types[var_name] = var_type

            info_text = None
            if var_name == "meal":
                info_text = (
                    "You can include quantity in the meal name.\n"
                    "Examples: '2 eggs', '1 cup rice', '3 slices of bread', '100g butter', '1 tbsp gravy'.\n"
                    "The API will automatically extract the nutrition info."
                )

            self.create_labeled_entry(frame, label_text, var, info_text=info_text)


            if var_name == "meal":
                tk.Button(frame, text="Fetch Nutrition Info", command=self.auto_fill_meal_info,
                          bg="#2196F3", fg="white", font=("Helvetica", 10)).pack(pady=5)

        tk.Button(frame, text="Save", command=lambda: save_callback(self.log_entries, self.log_types),
                  bg="#4CAF50", fg="white", font=("Helvetica", 12), width=20).pack(pady=15)
        tk.Button(frame, text="Back", command=self.show_main_menu,
                  bg="#777", fg="white", font=("Helvetica", 12), width=20).pack()

    def save_entry(self, data_type, entries, entry_types):
        date = self.get_today()
        data_dict = self.user_data.setdefault(data_type, {}).setdefault(date, [])

        entry = {}
        for key, var in entries.items():
            val_str = var.get().strip()
            if not val_str:
                messagebox.showerror("Input Error", f"{key.title()} cannot be empty.")
                return
            try:
                val = entry_types[key](val_str)
            except ValueError:
                messagebox.showerror("Input Error", f"Invalid input for {key.title()}.")
                return
            entry[key] = val

        data_dict.append(entry)
        save_data(self.data)
        messagebox.showinfo("Saved", f"{data_type[:-1].title()} logged!")
        self.show_main_menu()

if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()
