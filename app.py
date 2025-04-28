from coda import format_data
from bkms import update_sheet
import customtkinter
from threading import Thread

class UpdateFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, value):
        super().__init__(master, label_text=title, height=75)
        self.grid_columnconfigure(0, weight=1)
        self.value = value
        self.label = customtkinter.CTkLabel(self, text=self.value, fg_color="transparent")
        self.label.grid(row=0, column=0, pady=(0, 0))

    def change_item(self, new_text):
        self.label.configure(text=new_text)

class GroupFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = customtkinter.StringVar(value="")

        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            radiobutton = customtkinter.CTkRadioButton(self, text=value, value=value, variable=self.variable)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)

class WeekDateFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.entries = []

        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            entry = customtkinter.CTkEntry(self, placeholder_text=value)
            entry.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.entries.append(entry)

    def get(self):
        filled_entries = []
        for entry in self.entries:
            if not entry.get() == "":
                filled_entries.append(entry.get())
        return filled_entries

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("750x350")
        self.grid_columnconfigure((0), weight=1)
        self.title("CODA to BKMS Bot")

        self.weekdate_frame = WeekDateFrame(self, "Date", values=["Date (March 12)"])
        self.weekdate_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.group_frame = GroupFrame(self, "Group", values=["Saturday K1", "Saturday K2", "Sunday K1", "Sunday K2"])
        self.group_frame.grid(row=0, column=1, padx=(0, 0), pady=(10, 0), sticky="nsew")

        self.sabha_held_frame = GroupFrame(self, "Was Sabha Held?", values=["Yes", "No"])
        self.sabha_held_frame.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.p2_guju_frame = GroupFrame(self, "Was P2 in Guju?", values=["Yes", "No"])
        self.p2_guju_frame.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="nsew")

        self.update_frame = UpdateFrame(master=self, title="Bot Updates", value="Bot is up and ready")
        self.update_frame.grid(row=0, column=2, rowspan=2, padx=(10), pady=(10, 0), sticky="nsew")
        self.update_frame._scrollbar.configure(height=0)

        self.button = customtkinter.CTkButton(self, text="Run Bot", command=self.on_button_clicked)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew", columnspan=3)

        self.progress = customtkinter.CTkProgressBar(self, orientation="horizontal")
        self.progress.grid(row=4, column=0, padx=10, pady=(0,10), sticky="ew", columnspan=3)
        self.progress.set(0)

    def on_button_clicked(self):
        btn_thread = Thread(target=self.button_callback, daemon=True)
        btn_thread.start()

    def button_callback(self):
        date = self.weekdate_frame.get()[0]
        sabha_group = self.group_frame.get()
        sabha_held = self.sabha_held_frame.get()
        p2_guju = self.p2_guju_frame.get()

        if date and sabha_group and sabha_held and p2_guju:
            self.update_frame.change_item(f"Group: {sabha_group}\nDate: {date}\n")
            attendance, attendance_count = format_data(sabha_group, date)
            self.update_frame.change_item(f"{attendance_count} Kishores Found\nMoving on to BKMS Reporting\n")
            self.progress.set(0.75)
            update_sheet(attendance, sabha_group, sabha_held, p2_guju)
            self.progress.set(1)
        else:
            self.update_frame.change_item(f"Try Again! Make sure yous elect all required fields\n")

app = App()
app.mainloop()