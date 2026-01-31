import customtkinter as ctk
from vpython import *
import multiprocessing
import sys


# the simulation function
def run_solar_system(custom_data=None, planet_overrides=None):
    """
    Runs the vpython simulation.
    custom_data: Dict for the extra object (optional).
    planet_overrides: Dict { 'Earth': {'pos': (x,y,z), 'v': (vx,vy,vz)}, ... } (optional)
    """
    scene = canvas(title='The Solar System', width=1300, height=700)
    scene.background = color.black

    # Constants
    G = 6.67428e-11
    scale = 1e9  # 1 unit in sim = 1 billion meters in reality

    # 1. Create the Sun
    sun = sphere(pos=vector(0, 0, 0), radius=6.9634 * 10 ** 8 / scale, color=color.yellow, emissive=True)
    sun.mass = 1.98892e30
    sun.v = vector(0, 0, 0)
    sun.label = label(pos=sun.pos + vector(0, sun.radius * 2, 0),
                      text="Sun", height=12, box=False, color=color.yellow)

    # 2. Planet Data (Standard Defaults)
    planets_data = [
        ("Mercury", 6.98173e10, 2.44e6, 3.285e23, color.orange),
        ("Venus",   1.0894e11,  6.052e6, 4.867e24, color.white),
        ("Earth",   1.52096e11, 6.371e6, 5.972e24, color.blue),
        ("Mars",    2.49233e11, 3.39e6,  6.39e23,  color.red),
        ("Jupiter", 8.16038e11, 6.991e7, 1.898e27, color.orange),
        ("Saturn",  1.50724e12, 5.823e7, 5.683e26, color.yellow),
        ("Uranus",  3.01104e12, 2.536e7, 8.681e25, color.cyan),
        ("Neptune", 4.54594e12, 2.462e7, 1.024e26, color.blue)
    ]

    # Default velocities for standard orbits
    v_aphelion = {
        "Mercury": 38860, "Venus": 34790, "Earth": 29290, "Mars": 21970,
        "Jupiter": 12440, "Saturn": 9090, "Uranus": 6490, "Neptune": 5370
    }

    bodies = [sun]

    # Create Planets (Check for overrides)
    for name, distance, radius, mass, color_p in planets_data:

        # Default Values
        pos_vec = vector(distance / scale, 0, 0)
        v_val = v_aphelion.get(name, 0)
        vel_vec = vector(0, v_val / scale, 0)

        # CHECK: Is there a manual override for this planet?
        if planet_overrides and name in planet_overrides:
            ov = planet_overrides[name]

            # Override Position
            if ov.get('pos') is not None:
                pos_vec = vector(ov['pos'][0] / scale, ov['pos'][1] / scale, ov['pos'][2] / scale)

            # Override Velocity
            if ov.get('v') is not None:
                vel_vec = vector(ov['v'][0] / scale, ov['v'][1] / scale, ov['v'][2] / scale)

        p = sphere(pos=pos_vec, radius=radius / scale, color=color_p, make_trail=True)
        p.mass = mass
        p.v = vel_vec
        p.label = label(pos=p.pos + vector(0, p.radius * 2, 0),
                        text=name, height=12, box=False, color=color_p)
        bodies.append(p)

    # 3. Add Custom Object (If provided)
    if custom_data:
        cx, cy, cz = custom_data['pos']
        cvx, cvy, cvz = custom_data['v']

        c_obj = sphere(
            pos=vector(cx / scale, cy / scale, cz / scale),
            radius=custom_data['radius'] / scale,
            color=color.magenta,
            make_trail=True
        )
        c_obj.mass = custom_data['mass']
        c_obj.v = vector(cvx / scale, cvy / scale, cvz / scale)
        c_obj.label = label(pos=c_obj.pos + vector(0, c_obj.radius * 2, 0),
                            text=custom_data['name'], height=12, box=False, color=color.magenta)
        bodies.append(c_obj)

    # 4. Conserve Momentum (Stabilize Sun)
    total_momentum = vector(0, 0, 0)
    for body in bodies:
        if body == sun:
            continue
        total_momentum += body.mass * body.v
    sun.v = -total_momentum / sun.mass

    # 5. Physics Loop: calculates net acceleration vector for each object in each instance
    dt = 3 * 3600.0
    while True:
        rate(60)
        accs = [vector(0, 0, 0) for _ in bodies]

        for i, body in enumerate(bodies):
            total_a = vector(0, 0, 0)
            for j, other in enumerate(bodies):
                if i == j:
                    continue
                r_vec = other.pos - body.pos
                r_mag = mag(r_vec)
                if r_mag == 0:
                    continue
                total_a += (G * other.mass) / (scale ** 3 * r_mag ** 2) * norm(r_vec)
            accs[i] = total_a

        for i, body in enumerate(bodies):
            body.v += accs[i] * dt
            body.pos += body.v * dt
            if hasattr(body, 'label'):
                body.label.pos = body.pos + vector(0, body.radius * 2, 0)


#  UI CLASS
class SolarLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Solar Simulator Launcher")
        self.geometry("450x550")
        ctk.set_appearance_mode("dark")

        ctk.CTkLabel(self, text="SOLAR SYSTEM SIMULATOR", font=("Arial", 22, "bold")).pack(pady=20)

        self.btn1 = ctk.CTkButton(self, text="1. Standard Solar System",
                                  command=self.start_standard, height=45, width=280)
        self.btn1.pack(pady=10)

        self.btn2 = ctk.CTkButton(self, text="2. Add Custom Object (Comet/Asteroid)",
                                  command=self.open_custom_input, height=45, width=280,
                                  fg_color="#D35B58", hover_color="#C77C78")
        self.btn2.pack(pady=10)

        self.btn3 = ctk.CTkButton(self, text="3. Manually Configure Planets",
                                  command=self.open_manual_setup, height=45, width=280,
                                  fg_color="#4a90e2", hover_color="#357abd")
        self.btn3.pack(pady=10)

        self.info_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
        self.info_label.pack(side="bottom", pady=10)

    def start_standard(self):
        p = multiprocessing.Process(target=run_solar_system)
        p.start()

    #  OPTION 2: ONE CUSTOM OBJECT
    def open_custom_input(self):
        input_window = ctk.CTkToplevel(self)
        input_window.title("Configure Custom Object")
        input_window.geometry("500x750")
        input_window.attributes('-topmost', True)

        # Help Button
        def show_help():
            help_win = ctk.CTkToplevel(input_window)
            help_win.title("Valid Input Examples")
            help_win.geometry("400x500")
            help_win.attributes('-topmost', True)

            help_text = """
TIPS:
- Do not use commas (e.g., use 1000 not 1,000)
- Use 'e' for scientific notation (5e10 means 5 with 10 zeros)

EXAMPLE 1: COMET
----------------
Mass:     2.2e14
Radius:   1e6
Pos X:    3e11
Pos Y:    5e10
Pos Z:    0
Vel X:   -15000
Vel Y:    5000
Vel Z:    2000

EXAMPLE 2: SECOND EARTH
-----------------------
Mass:     5.97e24
Radius:   6.37e6
Pos X:    0
Pos Y:    1.52e11
Pos Z:    0
Vel X:   -29290
Vel Y:    0
Vel Z:    0
            """

            textbox = ctk.CTkTextbox(help_win, width=380, height=480, font=("Courier", 12))
            textbox.insert("0.0", help_text)
            textbox.configure(state="disabled")  # Make read-only
            textbox.pack(padx=10, pady=10)

        # Main Input UI
        frame = ctk.CTkScrollableFrame(input_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # HELP BUTTON
        ctk.CTkButton(frame, text="❓ Need Help? Click for Examples",
                      command=show_help, fg_color="#555555").pack(pady=10)

        ctk.CTkLabel(frame, text="Object Parameters", font=("Arial", 18, "bold")).pack(pady=5)

        entries = {}

        def create_entry(label_text, key):
            ctk.CTkLabel(frame, text=label_text, anchor="w").pack(fill="x", padx=10, pady=(10, 0))
            ent = ctk.CTkEntry(frame)
            ent.pack(fill="x", padx=10, pady=(0, 5))
            entries[key] = ent

        create_entry("Object Name (e.g. Comet)", "name")
        create_entry("Mass (kg)", "mass")
        create_entry("Radius (m)", "radius")

        ctk.CTkLabel(frame, text="--- Vectors ---", font=("Arial", 14, "bold")).pack(pady=15)

        create_entry("Position X (meters)", "pos_x")
        create_entry("Position Y (meters)", "pos_y")
        create_entry("Position Z (meters)", "pos_z")

        create_entry("Velocity X (m/s)", "vel_x")
        create_entry("Velocity Y (m/s)", "vel_y")
        create_entry("Velocity Z (m/s)", "vel_z")

        error_label = ctk.CTkLabel(frame, text="", font=("Arial", 12))
        error_label.pack(pady=5)

        def submit():
            try:
                # Validation: Check for empty strings first
                for key, ent in entries.items():
                    if ent.get().strip() == "":
                        raise ValueError("Empty Field")

                data = {
                    'name': entries['name'].get(),
                    'mass': float(entries['mass'].get()),
                    'radius': float(entries['radius'].get()),
                    'pos': (float(entries['pos_x'].get()), float(entries['pos_y'].get()),
                            float(entries['pos_z'].get())),
                    'v': (float(entries['vel_x'].get()), float(entries['vel_y'].get()),
                          float(entries['vel_z'].get()))
                }
                input_window.destroy()

                # Keep original logic same: run_solar_system(custom_data, planet_overrides=None)
                p = multiprocessing.Process(target=run_solar_system, args=(data, None))
                p.start()

            except ValueError:
                error_label.configure(
                    text="Error: Please enter valid numbers in all fields.\n(No empty boxes, no commas)",
                    text_color="red"
                )

        ctk.CTkButton(frame, text="LAUNCH SIMULATION", command=submit,
                      fg_color="green", hover_color="darkgreen").pack(pady=20)

    # OPTION 3: MANUAL PLANET CONFIGURATION + OPTIONAL CUSTOM OBJECT
    def open_manual_setup(self):
        win = ctk.CTkToplevel(self)
        win.title("Full Manual Configuration")
        win.geometry("900x800")

        # Help window: reference values with example XYZ components
        def open_help_window():
            h_win = ctk.CTkToplevel(win)
            h_win.title("Solar System Reference Values")
            h_win.geometry("650x750")
            h_win.attributes('-topmost', True)

            h_frame = ctk.CTkScrollableFrame(h_win)
            h_frame.pack(fill="both", expand=True, padx=10, pady=10)

            ctk.CTkLabel(h_frame, text="REFERENCE VALUES (XYZ COMPONENTS)", font=("Arial", 16, "bold")).pack(pady=10)

            help_text = (
                "UNITS KEY:\n"
                "  • Position components: meters (m)\n"
                "  • Velocity components: meters/sec (m/s)\n"
                "  • Mass: kilograms (kg)\n"
                "  • Radius: meters (m)\n"
                "  (Use scientific notation like 1.5e11)\n\n"
                "IMPORTANT:\n"
                "  The defaults assume planets start on the +X axis and move in +Y direction.\n"
                "  Default components are:\n"
                "    Pos = (Dist, 0, 0)\n"
                "    Vel = (0, VelY, 0)\n\n"
                "--------------------------------------------------\n"
                "SUN:\n"
                "  Mass: 1.989e30\n"
                "  Radius: 6.96e8\n\n"
                "MERCURY:\n"
                "  Pos = (6.98173e10, 0, 0)\n"
                "  Vel = (0, 38860, 0)\n"
                "  Mass: 3.285e23   Radius: 2.44e6\n\n"
                "VENUS:\n"
                "  Pos = (1.0894e11, 0, 0)\n"
                "  Vel = (0, 34790, 0)\n"
                "  Mass: 4.867e24   Radius: 6.052e6\n\n"
                "EARTH:\n"
                "  Pos = (1.52096e11, 0, 0)\n"
                "  Vel = (0, 29290, 0)\n"
                "  Mass: 5.972e24   Radius: 6.371e6\n\n"
                "MARS:\n"
                "  Pos = (2.49233e11, 0, 0)\n"
                "  Vel = (0, 21970, 0)\n"
                "  Mass: 6.39e23    Radius: 3.39e6\n\n"
                "--------------------------------------------------\n"
                "JUPITER:\n"
                "  Pos = (8.16038e11, 0, 0)\n"
                "  Vel = (0, 12440, 0)\n"
                "  Mass: 1.898e27   Radius: 6.991e7\n\n"
                "SATURN:\n"
                "  Pos = (1.50724e12, 0, 0)\n"
                "  Vel = (0, 9090, 0)\n"
                "  Mass: 5.683e26   Radius: 5.823e7\n\n"
                "URANUS:\n"
                "  Pos = (3.01104e12, 0, 0)\n"
                "  Vel = (0, 6490, 0)\n"
                "  Mass: 8.681e25   Radius: 2.536e7\n\n"
                "NEPTUNE:\n"
                "  Pos = (4.54594e12, 0, 0)\n"
                "  Vel = (0, 5370, 0)\n"
                "  Mass: 1.024e26   Radius: 2.462e7\n"
            )

            txt_box = ctk.CTkTextbox(h_frame, height=650, font=("Consolas", 12))
            txt_box.pack(fill="x", padx=10, pady=5)
            txt_box.insert("0.0", help_text)
            txt_box.configure(state="disabled")
            ctk.CTkButton(h_frame, text="Close", command=h_win.destroy, fg_color="gray").pack(pady=10)

        # Custom object help: SAME help text/style as Option 2
        def open_custom_help():
            help_win = ctk.CTkToplevel(win)
            help_win.title("Valid Input Examples (Custom Object)")
            help_win.geometry("400x520")
            help_win.attributes('-topmost', True)

            help_text = """
TIPS:
- Do not use commas (e.g., use 1000 not 1,000)
- Use 'e' for scientific notation (5e10 means 5 with 10 zeros)
- If you enter a custom object NAME, you must fill ALL fields (Mass, Radius, X/Y/Z, VX/VY/VZ)

EXAMPLE 1: COMET
----------------
Mass:     2.2e14
Radius:   1e6
Pos X:    3e11
Pos Y:    5e10
Pos Z:    0
Vel X:   -15000
Vel Y:    5000
Vel Z:    2000

EXAMPLE 2: SECOND EARTH
-----------------------
Mass:     5.97e24
Radius:   6.37e6
Pos X:    0
Pos Y:    1.52e11
Pos Z:    0
Vel X:   -29290
Vel Y:    0
Vel Z:    0
            """

            textbox = ctk.CTkTextbox(help_win, width=380, height=500, font=("Courier", 12))
            textbox.insert("0.0", help_text)
            textbox.configure(state="disabled")
            textbox.pack(padx=10, pady=10)

        # Scrollable container for the main manual setup
        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Header with Help Button
        header_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(header_frame, text="MANUAL CONFIGURATION", font=("Arial", 20, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(header_frame, text="? Help / Reference Values", width=180,
                      command=open_help_window, fg_color="#F39C12", hover_color="#D68910").pack(side="right", padx=10)

        ctk.CTkLabel(scroll,
                     text="Leave all fields blank for a planet to use standard default orbits.",
                     text_color="gray").pack(pady=5)

        planet_names = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
        planet_entries = {}

        # GRID FOR PLANETS
        grid_frame = ctk.CTkFrame(scroll)
        grid_frame.pack(fill="x", padx=5, pady=10)

        headers = ["Planet", "Pos X (m)", "Pos Y (m)", "Pos Z (m)", "Vel X (m/s)", "Vel Y (m/s)", "Vel Z (m/s)"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(grid_frame, text=h, font=("Arial", 11, "bold")).grid(row=0, column=i, padx=5, pady=5)

        for idx, p_name in enumerate(planet_names):
            ctk.CTkLabel(grid_frame, text=p_name).grid(row=idx + 1, column=0, padx=5, pady=2)

            planet_entries[p_name] = []
            for col in range(6):  # 3 for Pos, 3 for Vel
                ent = ctk.CTkEntry(grid_frame, width=90, placeholder_text="Default")
                ent.grid(row=idx + 1, column=col + 1, padx=2, pady=2)
                planet_entries[p_name].append(ent)

        ctk.CTkLabel(scroll, text="-" * 100).pack(pady=20)

        # optional custom object selection
        custom_header = ctk.CTkFrame(scroll, fg_color="transparent")
        custom_header.pack(fill="x", pady=(5, 0), padx=10)

        ctk.CTkLabel(custom_header,
                     text="ADDITIONAL CUSTOM OBJECT (OPTIONAL)",
                     font=("Arial", 16, "bold"),
                     text_color="#D35B58").pack(side="left")

        ctk.CTkButton(custom_header,
                      text="Examples",
                      width=120,
                      command=open_custom_help,
                      fg_color="#555555").pack(side="right")

        ctk.CTkLabel(scroll,
                     text="If you enter a Name, you must fill ALL fields below (Mass, Radius, X/Y/Z, VX/VY/VZ).",
                     text_color="gray").pack(pady=(5, 10))

        custom_frame = ctk.CTkFrame(scroll)
        custom_frame.pack(fill="x", padx=20)

        custom_entries = {}

        def add_custom_field(parent, key, txt, r, c):
            ctk.CTkLabel(parent, text=txt).grid(row=r, column=c, padx=5, pady=2, sticky="e")
            e = ctk.CTkEntry(parent, width=120)
            e.grid(row=r, column=c + 1, padx=5, pady=2)
            custom_entries[key] = e

        add_custom_field(custom_frame, 'name', "Name:", 0, 0)
        add_custom_field(custom_frame, 'mass', "Mass (kg):", 0, 2)
        add_custom_field(custom_frame, 'radius', "Radius (m):", 0, 4)

        ctk.CTkLabel(custom_frame, text="Vectors:", font=("Arial", 12, "bold")).grid(row=1, column=0, pady=5)

        add_custom_field(custom_frame, 'px', "Pos X:", 2, 0)
        add_custom_field(custom_frame, 'py', "Pos Y:", 2, 2)
        add_custom_field(custom_frame, 'pz', "Pos Z:", 2, 4)

        add_custom_field(custom_frame, 'vx', "Vel X:", 3, 0)
        add_custom_field(custom_frame, 'vy', "Vel Y:", 3, 2)
        add_custom_field(custom_frame, 'vz', "Vel Z:", 3, 4)

        # SUBMIT LOGIC
        error_lbl = ctk.CTkLabel(scroll, text="", text_color="red")
        error_lbl.pack(pady=10)

        def manual_launch():
            overrides = {}
            custom_obj_data = None

            try:
                # 1. Parse Planets (logic unchanged)
                for name, ents in planet_entries.items():
                    vals = [e.get().strip() for e in ents]

                    # If ALL fields are empty, skip (use default)
                    if all(v == "" for v in vals):
                        continue

                    def safe_float(s):
                        return float(s) if s else 0.0

                    pos = (safe_float(vals[0]), safe_float(vals[1]), safe_float(vals[2]))
                    vel = (safe_float(vals[3]), safe_float(vals[4]), safe_float(vals[5]))

                    overrides[name] = {'pos': pos, 'v': vel}

                # 2. Parse Custom Object (ONLY if name is provided) — now strict validation
                name_val = custom_entries['name'].get().strip()
                if name_val != "":
                    required_keys = ['mass', 'radius', 'px', 'py', 'pz', 'vx', 'vy', 'vz']
                    missing = [k for k in required_keys if custom_entries[k].get().strip() == ""]
                    if missing:
                        raise ValueError("Missing custom fields")

                    custom_obj_data = {
                        'name': name_val,
                        'mass': float(custom_entries['mass'].get()),
                        'radius': float(custom_entries['radius'].get()),
                        'pos': (float(custom_entries['px'].get()), float(custom_entries['py'].get()),
                                float(custom_entries['pz'].get())),
                        'v': (float(custom_entries['vx'].get()), float(custom_entries['vy'].get()),
                              float(custom_entries['vz'].get()))
                    }

                win.destroy()
                p = multiprocessing.Process(target=run_solar_system, args=(custom_obj_data, overrides))
                p.start()

            except ValueError:
                error_lbl.configure(
                    text="Error: For Custom Object, if Name is entered you must fill ALL fields with valid numbers.\n"
                         "(No empty boxes, no commas)",
                )

        ctk.CTkButton(scroll, text="LAUNCH CONFIGURATION", command=manual_launch,
                      height=50, fg_color="green", hover_color="darkgreen").pack(pady=30, fill="x", padx=50)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = SolarLauncher()
    app.mainloop()

