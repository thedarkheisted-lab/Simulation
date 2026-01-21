import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from .war_engine import WarEngine

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WarGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cosmic War Simulator")
        self.geometry("1200x850")
        self.resizable(True, True)

        self.engine = WarEngine(logger=self.log)

        self.turn = 0
        self.running = False

        self.entities = self.engine.entities


        self.build_ui()
        self.update_stats()
        self.log("Welcome to the Cosmic War Simulator!")

    def build_ui(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Cosmic War Simulator", font=("Arial", 24, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.cosmic_label = ctk.CTkLabel(self, text="Cosmic Event: None", font=("Arial", 14))
        self.cosmic_label.grid(row=1, column=0, columnspan=2, pady=5)

        self.status_frame = ctk.CTkScrollableFrame(self, width=1150, height=250)
        self.status_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.status_widgets = []
        for i, entity in enumerate(self.entities):
            frame = self.create_status_frame(self.status_frame, entity)
            frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            self.status_widgets.append(frame)

        self.log_box = ctk.CTkTextbox(self, width=1100, height=300)
        self.log_box.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.controls = ctk.CTkFrame(self)
        self.controls.grid(row=4, column=0, columnspan=2, pady=10)

        self.next_btn = ctk.CTkButton(self.controls, text="Next Turn", command=self.next_turn)
        self.next_btn.pack(side="left", padx=10)

        self.auto_btn = ctk.CTkButton(self.controls, text="Auto Run", command=self.toggle_auto)
        self.auto_btn.pack(side="left", padx=10)

        self.reset_btn = ctk.CTkButton(self.controls, text="Reset", command=self.reset)
        self.reset_btn.pack(side="left", padx=10)

    def create_status_frame(self, parent, entity):
        frame = ctk.CTkFrame(parent)
        color_map = {
            "Priest": "#88e0ff",
            "Mechanist": "#ffa07a",
            "Intern": "#dddddd"
        }
        class_name = entity.__class__.__name__
        border_color = color_map.get(class_name, "#bbbbbb")

        frame.configure(border_color=border_color, border_width=2)

        entity.name_label = ctk.CTkLabel(frame, text=entity.name, font=("Arial", 18, "bold"))
        entity.name_label.pack(pady=5)

        entity.health_bar = ctk.CTkProgressBar(frame)
        entity.health_bar.set(entity.health / entity.max_health)
        entity.health_bar.pack(fill="x", padx=10)
        entity.health_text = ctk.CTkLabel(frame, text=f"❤️ Health: {entity.health:.1f}/{entity.max_health}")
        entity.health_text.pack()

        entity.mana_text = ctk.CTkLabel(frame, text=f"🔋 Mana: {entity.mana:.1f}/{entity.max_mana}")
        entity.mana_text.pack()

        entity.stamina_text = ctk.CTkLabel(frame, text=f"⚡ Stamina: {entity.stamina:.1f}/{entity.max_stamina}")
        entity.stamina_text.pack()

        return frame

    def log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def update_stats(self):
        for entity in self.entities:
            if hasattr(entity, 'health_bar'):
                entity.health_bar.set(entity.health / entity.max_health)
                entity.health_text.configure(text=f"❤️ Health: {entity.health:.1f}/{entity.max_health}")
                entity.mana_text.configure(text=f"🔋 Mana: {entity.mana:.1f}/{entity.max_mana}")
                entity.stamina_text.configure(text=f"⚡ Stamina: {entity.stamina:.1f}/{entity.max_stamina}")

    def next_turn(self):
        if self.engine.is_over():
            self.end_battle()
            return
        
        self.engine.step()
        self.turn = self.engine.turn
        if self.engine.current_event:
            self.cosmic_label.configure(text=f"Cosmic Event: {self.engine.current_event.name}")

        self.update_stats()

        if self.engine.is_over():
            self.end_battle()

    def toggle_auto(self):
        self.running = not self.running
        self.auto_btn.configure(text="Pause" if self.running else "Auto Run")
        if self.running:
            self.run_auto()

    def run_auto(self):
        if self.running and not self.engine.is_over():
            self.next_turn()
            self.after(1000, self.run_auto)

    def reset(self):
        self.engine = WarEngine(logger=self.log)
        self.entities = self.engine.entities
        self.turn = self.engine.turn
        self.running = False
        self.log_box.delete("1.0", "end")

        for frame in self.status_widgets:
            frame.destroy()
        self.status_widgets = []

        for i, entity in enumerate(self.entities):
            frame = self.create_status_frame(self.status_frame, entity)
            frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            self.status_widgets.append(frame)

        self.update_stats()
        self.cosmic_label.configure(text="Cosmic Event: None")

    def end_battle(self):
        alive = [e for e in self.entities if e.is_alive()]
        if len(alive) == 1:
            winner = alive[0].name
            result = f"{winner} is victorious!"
        elif len(alive) == 0:
            result = "No one survived."
        else:
            result = "No one (stalemate)."
        self.log(f"\n*** {result} ***")
        messagebox.showinfo("Battle Over", result)

if __name__ == "__main__":
    app = WarGUI()
    app.mainloop()
