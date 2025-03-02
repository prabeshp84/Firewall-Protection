import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess

# -------------------
# Section: Stylish Button Class
# Description: Custom button with oval shape, hover effects, and shadow
# -------------------
class StylishButton(tk.Frame):
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(parent, bg=FirewallApp.CONFIG["bg"], bd=0)
        
        self.normal_bg = FirewallApp.CONFIG["button"]["normal"]
        self.hover_bg = FirewallApp.CONFIG["button"]["hover"]
        self.active_bg = FirewallApp.CONFIG["button"]["active"]
        
        self.canvas = tk.Canvas(self, width=200, height=40, bg=FirewallApp.CONFIG["bg"], highlightthickness=0)
        self.canvas.pack(pady=2)
        
        self.shadow = self.canvas.create_oval(4, 4, 196, 36, fill='#2D2D2D', outline='')
        self.button_oval = self.canvas.create_oval(2, 2, 198, 38, fill=self.normal_bg, outline='')
        
        self.button_text = self.canvas.create_text(
            100, 20,
            text=text,
            fill='white',
            font=('Arial', 11, 'bold'),
            justify='center'
        )
        
        self.canvas.bind('<Enter>', self.on_hover)
        self.canvas.bind('<Leave>', self.on_leave)
        self.canvas.bind('<Button-1>', lambda e: [self.on_press(e), command()])
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.config(cursor='hand2')
        
    def on_hover(self, event):
        self.canvas.itemconfig(self.button_oval, fill=self.hover_bg)
        self.canvas.itemconfig(self.shadow, fill='#333333')
        
    def on_leave(self, event):
        self.canvas.itemconfig(self.button_oval, fill=self.normal_bg)
        self.canvas.itemconfig(self.shadow, fill='#2D2D2D')
        
    def on_press(self, event):
        self.canvas.itemconfig(self.button_oval, fill=self.active_bg)
        
    def on_release(self, event):
        self.canvas.itemconfig(self.button_oval, fill=self.hover_bg if self.canvas.winfo_containing(event.x_root, event.y_root) else self.normal_bg)

# -------------------
# Section: Tooltip Class
# Description: Displays hover tooltips for buttons
# -------------------
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        self.tip = None

    def show_tip(self, event):
        x, y = self.widget.winfo_pointerxy()
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x+10}+{y+10}")
        label = tk.Label(self.tip, text=self.text, bg="#FFFF99", fg="black", relief="solid", borderwidth=1)
        label.pack()

    def hide_tip(self, event):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# -------------------
# Section: Firewall Application Class
# Description: Main application class with UI and UFW logic
# -------------------
class FirewallApp:
    # Centralized configuration for colors and styles
    CONFIG = {
        "bg": "#1E1E1E",
        "title_fg": {"firewall": "#FFFF00", "protection": "#FF6B6B"},
        "button": {"normal": "#0288D1", "hover": "#0277BD", "active": "#01579B"},
        "menu": {"bg": "#2D2D2D", "fg": "#FFFF00", "active_bg": "#0288D1"}
    }

    def __init__(self, root):
        self.root = root
        self.root.title("UFW Firewall Control")
        self.root.geometry("400x600")
        self.root.configure(bg=self.CONFIG["bg"])

        # Check if UFW is installed
        if not self.check_ufw_installed():
            messagebox.showerror("Error", "UFW is not installed or accessible. Please install UFW.")
            root.quit()
            return

        # Main frame
        main_frame = tk.Frame(root, bg=self.CONFIG["bg"])
        main_frame.pack(expand=True, pady=20)

        # Title with status indicator
        self.title_frame = tk.Frame(main_frame, bg=self.CONFIG["bg"])
        self.title_frame.pack(pady=(0, 30))
        self.status_indicator = tk.Label(self.title_frame, text="●", font=('Arial', 18), bg=self.CONFIG["bg"])
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        tk.Label(self.title_frame, text="Firewall", bg=self.CONFIG["bg"], fg=self.CONFIG["title_fg"]["firewall"], font=('Arial', 18, 'bold')).pack(side=tk.LEFT)
        tk.Label(self.title_frame, text=" Protection", bg=self.CONFIG["bg"], fg=self.CONFIG["title_fg"]["protection"], font=('Arial', 18, 'bold')).pack(side=tk.LEFT)

        # Buttons
        self.firewall_enabled = False
        self.toggle_button = StylishButton(main_frame, "Enable Firewall", self.toggle_firewall)
        self.status_button = StylishButton(main_frame, "Check Status", self.check_status)
        self.allow_port_button = StylishButton(main_frame, "Allow Port", self.add_rule)
        self.block_port_button = StylishButton(main_frame, "Block Port", self.block_rule)
        self.delete_port_button = StylishButton(main_frame, "Delete Port", self.delete_rule)
        self.show_rules_button = StylishButton(main_frame, "Show Rules", self.show_rules)

        # Add tooltips
        Tooltip(self.toggle_button.canvas, "Toggle the firewall on or off")
        Tooltip(self.status_button.canvas, "View current firewall status")
        Tooltip(self.allow_port_button.canvas, "Allow traffic on a specific port")
        Tooltip(self.block_port_button.canvas, "Block traffic on a specific port")
        Tooltip(self.delete_port_button.canvas, "Delete an existing port rule")
        Tooltip(self.show_rules_button.canvas, "Display all active firewall rules")

        # Menu bar
        self.menu_bar = tk.Menu(root, bg=self.CONFIG["menu"]["bg"], fg=self.CONFIG["menu"]["fg"], activebackground=self.CONFIG["menu"]["active_bg"], activeforeground='white')
        self.root.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.CONFIG["menu"]["bg"], fg=self.CONFIG["menu"]["fg"], activebackground=self.CONFIG["menu"]["active_bg"], activeforeground='white')
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Allow Port", command=self.add_rule)
        self.file_menu.add_command(label="Block Port", command=self.block_rule)
        self.file_menu.add_command(label="Delete Port", command=self.delete_rule)
        self.file_menu.add_command(label="Show Rules", command=self.show_rules)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)

        # Place buttons
        for btn in (self.toggle_button, self.status_button, self.allow_port_button, 
                    self.block_port_button, self.delete_port_button, self.show_rules_button):
            btn.pack(pady=10, padx=20)

        # Status bar
        self.status_bar = tk.Label(
            root,
            text="Ready",
            bg='#2D2D2D',
            fg='#FFFFFF',
            font=('Arial', 10),
            anchor='w',
            padx=10
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Credit label - "Designed by Prabesh Paudel"
        self.credit_label = tk.Label(
            root,
            text="Designed by Prabesh Paudel",
            bg='#2D2D2D',
            fg='#BBBBBB',  # Light gray for subtle contrast
            font=('Arial', 8, 'italic'),
            anchor='center'
        )
        self.credit_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize status
        self.check_initial_status()

    # -------------------
    # Section: Helper Methods
    # Description: Utility methods for status updates and UFW checks
    # -------------------
    def update_status(self, message):
        self.status_bar.config(text=message)

    def update_indicator(self):
        self.status_indicator.config(fg='#4CAF50' if self.firewall_enabled else '#FF4444')  # Green if on, red if off

    def check_ufw_installed(self):
        try:
            subprocess.run(["ufw", "--version"], capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_initial_status(self):
        status = self.run_ufw_command("status")
        self.firewall_enabled = "active" in status.lower()
        self.toggle_button.canvas.itemconfig(self.toggle_button.button_text, text="Disable Firewall" if self.firewall_enabled else "Enable Firewall")
        self.update_indicator()

    # -------------------
    # Section: Firewall Control Methods
    # Description: Methods to interact with UFW
    # -------------------
    def toggle_firewall(self):
        if not self.firewall_enabled:
            self.run_ufw_command("enable", "Firewall enabled successfully")
            self.toggle_button.canvas.itemconfig(self.toggle_button.button_text, text="Disable Firewall")
            self.firewall_enabled = True
            self.update_status("Firewall enabled")
        else:
            self.run_ufw_command("disable", "Firewall disabled successfully")
            self.toggle_button.canvas.itemconfig(self.toggle_button.button_text, text="Enable Firewall")
            self.firewall_enabled = False
            self.update_status("Firewall disabled")
        self.update_indicator()

    def check_status(self):
        status = self.run_ufw_command("status")
        messagebox.showinfo("Firewall Status", status)
        self.update_status("Status checked")

    def add_rule(self):
        port = simpledialog.askinteger("Allow Port", "Enter port number:", minvalue=1, maxvalue=65535)
        if port:
            self.run_ufw_command(f"allow {port}", f"Port {port} allowed successfully")
            self.update_status(f"Port {port} allowed")

    def block_rule(self):
        port = simpledialog.askinteger("Block Port", "Enter port number:", minvalue=1, maxvalue=65535)
        if port:
            self.run_ufw_command(f"deny {port}", f"Port {port} blocked successfully")
            self.update_status(f"Port {port} blocked")

    def delete_rule(self):
        port = simpledialog.askinteger("Delete Port", "Enter port number to delete:", minvalue=1, maxvalue=65535)
        if port:
            self.run_ufw_command(f"delete allow {port}", f"Rule allowing port {port} deleted", allow_error=True)
            self.run_ufw_command(f"delete deny {port}", f"Rule blocking port {port} deleted", allow_error=True)
            self.update_status(f"Port {port} rule deleted")

    def show_rules(self):
        rules = self.run_ufw_command("status verbose")
        messagebox.showinfo("UFW Rules", rules)
        self.update_status("Rules displayed")

    def run_ufw_command(self, command, success_message=None, allow_error=False):
        try:
            result = subprocess.run(["sudo", "ufw"] + command.split(), capture_output=True, text=True, check=True)
            if success_message:
                messagebox.showinfo("Success", success_message)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if not allow_error:
                messagebox.showerror("Error", f"Error executing UFW command:\n{e.stderr}")
                self.update_status("Error occurred")
            return e.stderr.strip()

# -------------------
# Section: Main Execution
# Description: Entry point for the application
# -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallApp(root)
    root.mainloop()
