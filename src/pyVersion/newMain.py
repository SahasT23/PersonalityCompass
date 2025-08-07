import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
import json
import os
import stat
from datetime import datetime
import platform

class PersonalityCompass:
    def __init__(self, root):
        self.root = root
        self.root.title("Personality Compass")
        self.root.geometry("1000x700")
        
        # Data storage
        self.people = {}  # {name: {'x': float, 'y': float, 'scatter': matplotlib_scatter, 'annotation': matplotlib_annotation, 'date_added': str, 'quadrant': str}}
        self.dragging = None
        self.drag_offset = (0, 0)
        self.edit_history = []  # Track all edit operations
        
        # Create data directory and hide it
        self.data_dir = "personality_compass_data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            self.hide_folder(self.data_dir)
        self.data_file = os.path.join(self.data_dir, "people_data.json")
        
        self.setup_gui()
        self.setup_plot()
        self.load_data()  # Load saved data after GUI is set up
        
        # Bind window close event to save data
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Add Person", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=(0, 5))
        
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(input_frame, textvariable=self.name_var, width=20)
        name_entry.grid(row=0, column=1, padx=(0, 10))
        name_entry.bind('<Return>', lambda e: self.add_person())
        
        add_btn = ttk.Button(input_frame, text="Add Person", command=self.add_person)
        add_btn.grid(row=0, column=2, padx=(0, 10))
        
        clear_btn = ttk.Button(input_frame, text="Clear All", command=self.clear_all)
        clear_btn.grid(row=0, column=3)
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="10")
        instructions_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N), padx=(10, 0), pady=(0, 10))
        
        instructions = """Keyboard Shortcuts:
• Enter: Add person after typing name
• Delete: Remove selected person from list
• Escape: Cancel current drag operation

Mouse Controls:
• Left-click + drag: Move person on grid
• Right-click: Remove person from grid

Data is automatically saved to:
personality_compass_data/ folder"""
        
        ttk.Label(instructions_frame, text=instructions, justify=tk.LEFT).pack()
        
        # People list
        list_frame = ttk.LabelFrame(main_frame, text="People", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.people_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set)
        self.people_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.people_listbox.yview)
        
        # Bind keyboard events
        self.people_listbox.bind('<Delete>', self.delete_selected_person)
        self.people_listbox.bind('<BackSpace>', self.delete_selected_person)
        self.people_listbox.bind('<Double-Button-1>', self.edit_coordinates)
        self.people_listbox.bind('<<ListboxSelect>>', self.on_person_select)
        
        # Coordinate editing frame
        coord_frame = ttk.LabelFrame(list_frame, text="Edit Coordinates", padding="5")
        coord_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(coord_frame, text="X:").grid(row=0, column=0, padx=(0, 5))
        self.x_var = tk.StringVar()
        self.x_entry = ttk.Entry(coord_frame, textvariable=self.x_var, width=8)
        self.x_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(coord_frame, text="Y:").grid(row=0, column=2, padx=(0, 5))
        self.y_var = tk.StringVar()
        self.y_entry = ttk.Entry(coord_frame, textvariable=self.y_var, width=8)
        self.y_entry.grid(row=0, column=3, padx=(0, 10))
        
        update_pos_btn = ttk.Button(coord_frame, text="Update Position", command=self.update_coordinates)
        update_pos_btn.grid(row=0, column=4, padx=(5, 0))
        
        # Bind Enter key to update coordinates
        self.x_entry.bind('<Return>', lambda e: self.update_coordinates())
        self.y_entry.bind('<Return>', lambda e: self.update_coordinates())
        
        # Plot frame
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
        
        self.plot_container = plot_frame
        
    def setup_plot(self):
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        
        # Set up the plot
        self.ax.set_xlim(-100, 100)
        self.ax.set_ylim(-100, 100)
        self.ax.set_xlabel('Not ← → Gnatty', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Non NPC ← → NPC', fontsize=12, fontweight='bold')
        self.ax.set_title('Personality Compass', fontsize=14, fontweight='bold', pad=20)
        
        # Add grid
        self.ax.grid(True, alpha=0.3)
        
        # Add quadrant lines
        self.ax.axhline(y=0, color='black', linewidth=1.5, alpha=0.8)
        self.ax.axvline(x=0, color='black', linewidth=1.5, alpha=0.8)
        
        # Add quadrant labels
        self.ax.text(110, 50, 'Gnatty,\nNPC', ha='center', va='center', 
                    fontsize=10, alpha=0.6, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.5))
        self.ax.text(-110, 50, 'Not,\nNPC', ha='center', va='center', 
                    fontsize=10, alpha=0.6, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.5))
        self.ax.text(-110, -50, 'Not,\nNon NPC', ha='center', va='center', 
                    fontsize=10, alpha=0.6, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.5))
        self.ax.text(110, -50, 'Gnatty,\nNon NPC', ha='center', va='center', 
                    fontsize=10, alpha=0.6, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.5))
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind mouse events
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        # Bind keyboard events
        self.root.bind('<Escape>', self.cancel_drag)
        
    def hide_folder(self, folder_path):
        """Hide the data folder based on the operating system"""
        try:
            system = platform.system()
            if system == "Windows":
                # Windows: Use attrib command to hide folder
                os.system(f'attrib +h "{folder_path}"')
            elif system in ["Darwin", "Linux"]:  # macOS and Linux
                # Unix-like: Folders starting with . are hidden by default
                # If folder doesn't start with ., create a .hidden file
                hidden_file = os.path.join(os.path.dirname(folder_path), ".hidden")
                if not folder_path.startswith('.'):
                    with open(hidden_file, 'a') as f:
                        f.write(f"{os.path.basename(folder_path)}\n")
        except Exception as e:
            print(f"Could not hide folder: {e}")
    
    def log_edit(self, action, details=None):
        """Log an edit operation with timestamp"""
        edit_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "action": action,
            "details": details or {}
        }
        self.edit_history.append(edit_entry)
        
        # Keep only last 100 edits to prevent file from growing too large
        if len(self.edit_history) > 100:
            self.edit_history = self.edit_history[-100:]
        
    def hide_folder(self, folder_path):
        """Hide the data folder based on the operating system"""
        try:
            system = platform.system()
            if system == "Windows":
                # Windows: Use attrib command to hide folder
                os.system(f'attrib +h "{folder_path}"')
            elif system in ["Darwin", "Linux"]:  # macOS and Linux
                # Unix-like: Folders starting with . are hidden by default
                # If folder doesn't start with ., create a .hidden file
                hidden_file = os.path.join(os.path.dirname(folder_path), ".hidden")
                if not folder_path.startswith('.'):
                    with open(hidden_file, 'a') as f:
                        f.write(f"{os.path.basename(folder_path)}\n")
        except Exception as e:
            print(f"Could not hide folder: {e}")
    
    def get_quadrant(self, x, y):
        """Determine which quadrant a point is in"""
        if x >= 0 and y >= 0:
            return "Gnatty NPC"
        elif x < 0 and y >= 0:
            return "Not NPC"
        elif x < 0 and y < 0:
            return "Not Non-NPC"
        else:  # x >= 0 and y < 0
            return "Gnatty Non-NPC"
    
    def cancel_drag(self, event=None):
        """Cancel current drag operation"""
        self.dragging = None
        self.drag_offset = (0, 0)
        
    def delete_selected_person(self, event=None):
        """Delete the selected person from the listbox"""
        selection = self.people_listbox.curselection()
        if selection:
            selected_text = self.people_listbox.get(selection[0])
            # Extract name from the listbox text (format: "Name (x, y) - Quadrant")
            name = selected_text.split(' (')[0]
            if name in self.people:
                self.remove_person(name)
    
    def edit_coordinates(self, event=None):
        """Load coordinates of selected person into edit fields"""
        selection = self.people_listbox.curselection()
        if selection:
            selected_text = self.people_listbox.get(selection[0])
            name = selected_text.split(' (')[0]
            if name in self.people:
                person_data = self.people[name]
                self.x_var.set(f"{person_data['x']:.1f}")
                self.y_var.set(f"{person_data['y']:.1f}")
                # Focus on X entry for immediate editing
                self.x_entry.focus()
                self.x_entry.select_range(0, tk.END)
    
    def update_coordinates(self):
        """Update the selected person's coordinates from the input fields"""
        selection = self.people_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a person from the list first.")
            return
        
        try:
            # Get and validate coordinates
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            
            # Constrain to plot bounds
            x = max(-100, min(100, x))
            y = max(-100, min(100, y))
            
            # Get selected person
            selected_text = self.people_listbox.get(selection[0])
            name = selected_text.split(' (')[0]
            
            if name in self.people:
                # Store old position for logging
                old_x = self.people[name]['x']
                old_y = self.people[name]['y']
                old_quadrant = self.people[name]['quadrant']
                
                # Update position
                self.update_person_position(name, x, y)
                
                # Update quadrant
                new_quadrant = self.get_quadrant(x, y)
                self.people[name]['quadrant'] = new_quadrant
                
                # Log the coordinate edit
                self.log_edit("coordinates_edited", {
                    "name": name,
                    "old_position": {"x": old_x, "y": old_y},
                    "new_position": {"x": x, "y": y},
                    "old_quadrant": old_quadrant,
                    "new_quadrant": new_quadrant,
                    "method": "manual_input"
                })
                
                # Update display and save
                self.update_listbox()
                self.save_data()
                
                # Update the input fields with constrained values
                self.x_var.set(f"{x:.1f}")
                self.y_var.set(f"{y:.1f}")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for X and Y coordinates.\nX and Y must be between -100 and 100.")
    
    def on_person_select(self, event=None):
        """Handle person selection in listbox - populate coordinate fields"""
        selection = self.people_listbox.curselection()
        if selection:
            selected_text = self.people_listbox.get(selection[0])
            name = selected_text.split(' (')[0]
            if name in self.people:
                person_data = self.people[name]
                self.x_var.set(f"{person_data['x']:.1f}")
                self.y_var.set(f"{person_data['y']:.1f}")
        
    def add_person(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a name.")
            return
            
        if name in self.people:
            messagebox.showwarning("Warning", f"{name} is already on the grid.")
            return
        
        # Add person at center (0, 0)
        x, y = 0, 0
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        quadrant = self.get_quadrant(x, y)
        
        # Plot the point
        scatter = self.ax.scatter([x], [y], s=100, c='red', alpha=0.7, 
                                edgecolors='darkred', linewidth=2, zorder=5)
        
        # Add annotation with better positioning
        annotation = self.ax.annotate(name, (x, y), xytext=(8, 8), 
                                    textcoords='offset points', fontsize=9,
                                    bbox=dict(boxstyle="round,pad=0.3", 
                                            facecolor='white', alpha=0.9,
                                            edgecolor='gray'),
                                    zorder=6, ha='left', va='bottom')
        
        # Store the person data
        self.people[name] = {
            'x': x, 
            'y': y, 
            'scatter': scatter,
            'annotation': annotation,
            'date_added': date_added,
            'quadrant': quadrant
        }
        
        # Log the addition
        self.log_edit("person_added", {
            "name": name,
            "position": {"x": x, "y": y},
            "quadrant": quadrant
        })
        
        # Update listbox
        self.people_listbox.insert(tk.END, f"{name} ({x:.0f}, {y:.0f})")
        
        # Clear input
        self.name_var.set("")
        
        # Refresh canvas
        self.canvas.draw()
        
        # Save data after position update
        self.save_data()
        
        # Save data after adding person
        self.save_data()
        
    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all people from the grid?"):
            # Log the clear operation before clearing
            people_cleared = list(self.people.keys())
            self.log_edit("all_people_cleared", {
                "people_count": len(people_cleared),
                "people_names": people_cleared
            })
            
            # Clear plot
            for person_data in self.people.values():
                person_data['scatter'].remove()
                person_data['annotation'].remove()
            
            # Clear data
            self.people.clear()
            
            # Clear listbox
            self.people_listbox.delete(0, tk.END)
            
            # Refresh canvas
            self.canvas.draw()
            
            # Save data after removing person
            self.save_data()
            
            # Save data after clearing
            self.save_data()
    
    def find_person_at_point(self, event):
        if event.inaxes != self.ax:
            return None
            
        for name, data in self.people.items():
            # Check if click is near the person's position
            dx = abs(event.xdata - data['x'])
            dy = abs(event.ydata - data['y'])
            
            # Adjust sensitivity based on plot scale
            sensitivity = 5
            if dx < sensitivity and dy < sensitivity:
                return name
        return None
    
    def on_press(self, event):
        if event.inaxes != self.ax:
            return
            
        person = self.find_person_at_point(event)
        
        if event.button == 3:  # Right click - remove person
            if person:
                self.remove_person(person)
        elif event.button == 1 and person:  # Left click - start drag
            self.dragging = person
            self.drag_offset = (event.xdata - self.people[person]['x'], 
                              event.ydata - self.people[person]['y'])
    
    def on_motion(self, event):
        if self.dragging and event.inaxes == self.ax:
            # Calculate new position
            new_x = event.xdata - self.drag_offset[0]
            new_y = event.ydata - self.drag_offset[1]
            
            # Constrain to plot bounds
            new_x = max(-100, min(100, new_x))
            new_y = max(-100, min(100, new_y))
            
            # Update position
            self.update_person_position(self.dragging, new_x, new_y)
    
    def on_release(self, event):
        if self.dragging:
            # Update quadrant when drag is finished
            person_data = self.people[self.dragging]
            old_quadrant = person_data['quadrant']
            new_quadrant = self.get_quadrant(person_data['x'], person_data['y'])
            person_data['quadrant'] = new_quadrant
            
            # Log the position change
            self.log_edit("person_moved", {
                "name": self.dragging,
                "new_position": {"x": person_data['x'], "y": person_data['y']},
                "old_quadrant": old_quadrant,
                "new_quadrant": new_quadrant
            })
            
            self.update_listbox()
            
        self.dragging = None
        self.drag_offset = (0, 0)
    
    def update_person_position(self, name, x, y):
        if name not in self.people:
            return
            
        # Update stored position
        self.people[name]['x'] = x
        self.people[name]['y'] = y
        
        # Update scatter plot
        self.people[name]['scatter'].set_offsets([[x, y]])
        
        # Update annotation
        self.people[name]['annotation'].set_position((x, y))
        
        # Update listbox
        self.update_listbox()
        
        # Refresh canvas
        self.canvas.draw()
    
    def remove_person(self, name):
        if name in self.people:
            # Log the removal before removing
            person_data = self.people[name]
            self.log_edit("person_removed", {
                "name": name,
                "position": {"x": person_data['x'], "y": person_data['y']},
                "quadrant": person_data['quadrant'],
                "date_added": person_data['date_added']
            })
            
            # Remove from plot
            self.people[name]['scatter'].remove()
            self.people[name]['annotation'].remove()
            
            # Remove from data
            del self.people[name]
            
            # Update listbox
            self.update_listbox()
            
            # Refresh canvas
            self.canvas.draw()
            
            # Save data after removing person
            self.save_data()
    
    def update_listbox(self):
        self.people_listbox.delete(0, tk.END)
        for name, data in self.people.items():
            self.people_listbox.insert(tk.END, f"{name} ({data['x']:.0f}, {data['y']:.0f}) - {data['quadrant']}")
    
    def save_data(self):
        """Save people data to JSON file with enhanced information and edit history"""
        try:
            # Extract all data including metadata
            save_data = {
                "metadata": {
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    "total_people": len(self.people),
                    "version": "2.1",
                    "total_edits": len(self.edit_history),
                    "session_started": getattr(self, 'session_start', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                },
                "edit_history": self.edit_history,
                "people": {}
            }
            
            for name, data in self.people.items():
                save_data["people"][name] = {
                    'x': float(data['x']),
                    'y': float(data['y']),
                    'quadrant': data['quadrant'],
                    'date_added': data['date_added'],
                    'last_moved': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                }
            
            with open(self.data_file, 'w') as f:
                json.dump(save_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load people data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    loaded_data = json.load(f)
                
                # Load edit history if available
                self.edit_history = loaded_data.get("edit_history", [])
                
                # Log the session start
                if not hasattr(self, 'session_start'):
                    self.session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.log_edit("session_started", {
                        "previous_total_people": loaded_data.get("metadata", {}).get("total_people", 0),
                        "previous_last_updated": loaded_data.get("metadata", {}).get("last_updated", "Unknown")
                    })
                
                # Handle both old and new data formats
                if "people" in loaded_data:
                    people_data = loaded_data["people"]
                else:
                    people_data = loaded_data  # Old format
                
                # Add each person back to the plot
                for name, pos_data in people_data.items():
                    x, y = pos_data['x'], pos_data['y']
                    
                    # Get additional data if available
                    date_added = pos_data.get('date_added', 'Unknown')
                    quadrant = pos_data.get('quadrant', self.get_quadrant(x, y))
                    
                    # Plot the point
                    scatter = self.ax.scatter([x], [y], s=100, c='red', alpha=0.7, 
                                            edgecolors='darkred', linewidth=2, zorder=5)
                    
                    # Add annotation with better positioning
                    annotation = self.ax.annotate(name, (x, y), xytext=(8, 8), 
                                                textcoords='offset points', fontsize=9,
                                                bbox=dict(boxstyle="round,pad=0.3", 
                                                        facecolor='white', alpha=0.9,
                                                        edgecolor='gray'),
                                                zorder=6, ha='left', va='bottom')
                    
                    # Store the person data
                    self.people[name] = {
                        'x': x, 
                        'y': y, 
                        'scatter': scatter,
                        'annotation': annotation,
                        'date_added': date_added,
                        'quadrant': quadrant
                    }
                
                # Update listbox and canvas
                self.update_listbox()
                self.canvas.draw()
                
                print(f"Loaded {len(people_data)} people from saved data")
                print(f"Edit history contains {len(self.edit_history)} entries")
                
        except Exception as e:
            print(f"Error loading data: {e}")
            # Initialize session start even if loading fails
            if not hasattr(self, 'session_start'):
                self.session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def on_closing(self):
        """Handle window closing - ensure data is saved"""
        self.log_edit("session_ended", {
            "final_people_count": len(self.people),
            "session_duration_seconds": (datetime.now() - datetime.strptime(self.session_start, "%Y-%m-%d %H:%M:%S")).total_seconds() if hasattr(self, 'session_start') else 0
        })
        self.save_data()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = PersonalityCompass(root)
    root.mainloop()

if __name__ == "__main__":
    main()