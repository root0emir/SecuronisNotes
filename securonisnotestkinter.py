#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import calendar
import json
import csv
import os
from cryptography.fernet import Fernet
from tkinter import font as tkfont
import webbrowser
from tkcalendar import Calendar

class TerminalNotes:
    def __init__(self, file_path='notes.json', key_path=None):
        if key_path is None:
            key_path = '/etc/secure_notes/secret.key'
        self.file_path = file_path
        self.key_path = key_path
        self.key = self.load_key()
        self.fernet = Fernet(self.key)
        self.notes = self.load_notes()

    def load_key(self):
        os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
            os.chmod(self.key_path, 0o600)  # Set permissions to read/write for owner only
            return key

    def load_notes(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'rb') as file:
                encrypted_data = file.read()
                decrypted_data = self.fernet.decrypt(encrypted_data).decode()
                return json.loads(decrypted_data)
        return []

    def save_notes(self):
        encrypted_data = self.fernet.encrypt(json.dumps(self.notes).encode())
        with open(self.file_path, 'wb') as file:
            file.write(encrypted_data)

    def add_note(self, note, tags, priority, date_time, note_type):
        self.notes.append({
            "note": note,
            "tags": tags,
            "priority": priority,
            "date_time": date_time,
            "type": note_type
        })
        self.save_notes()
        print("Note added.")

    def list_notes(self):
        if not self.notes:
            print("No notes found.")
            return
        for idx, note in enumerate(self.notes, 1):
            tags = ", ".join(note["tags"])
            print(f"{idx}. [{note['priority'].capitalize()}] {note['note']} [Tags: {tags}] [Date: {note['date_time']}] [Type: {note['type']}]")

    def update_note(self, note_index, new_note, new_tags, new_priority, new_date_time, new_type):
        try:
            self.notes[note_index - 1] = {
                "note": new_note,
                "tags": new_tags,
                "priority": new_priority,
                "date_time": new_date_time,
                "type": new_type
            }
            self.save_notes()
            print("Note updated.")
        except IndexError:
            print("Invalid note index.")

    def delete_note(self, note_index):
        try:
            note = self.notes.pop(note_index - 1)
            self.save_notes()
            print(f"Deleted note: {note['note']}")
        except IndexError:
            print("Invalid note index.")

    def search_notes(self, keyword):
        results = [note for note in self.notes if keyword.lower() in note["note"].lower()]
        if not results:
            print("No matching notes found.")
        else:
            for idx, note in enumerate(results, 1):
                tags = ", ".join(note["tags"])
                print(f"{idx}. [{note['priority'].capitalize()}] {note['note']} [Tags: {tags}] [Date: {note['date_time']}] [Type: {note['type']}]")

    def import_notes(self, csv_file):
        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    note = row['note']
                    tags = row['tags'].split(',')
                    priority = row['priority']
                    date_time = row['date_time']
                    note_type = row['type']
                    self.add_note(note, tags, priority, date_time, note_type)
            print("Notes imported successfully.")
        except Exception as e:
            print(f"Error importing notes: {e}")

    def export_notes(self, csv_file):
        try:
            with open(csv_file, 'w', newline='') as file:
                fieldnames = ['note', 'tags', 'priority', 'date_time', 'type']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for note in self.notes:
                    writer.writerow({
                        'note': note['note'],
                        'tags': ','.join(note['tags']),
                        'priority': note['priority'],
                        'date_time': note['date_time'],
                        'type': note['type']
                    })
            print(f"Notes exported to {csv_file}.")
        except Exception as e:
            print(f"Error exporting notes: {e}")

    def export_notes_html(self, html_file):
        try:
            with open(html_file, 'w') as file:
                file.write("""
                <html>
                <head>
                    <title>Notes</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            margin: 20px;
                            background-color: #1e1e1e;
                            color: #ffffff;
                        }
                        h1 {
                            color: #007acc;
                        }
                        ul {
                            list-style-type: none;
                            padding: 0;
                        }
                        li {
                            background-color: #2d2d2d;
                            margin: 10px 0;
                            padding: 15px;
                            border-radius: 5px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                        }
                        .priority-high {
                            border-left: 4px solid #f44336;
                        }
                        .priority-medium {
                            border-left: 4px solid #ff9800;
                        }
                        .priority-low {
                            border-left: 4px solid #4caf50;
                        }
                        .tags {
                            color: #007acc;
                            font-size: 0.9em;
                        }
                        .date {
                            color: #888;
                            font-size: 0.8em;
                        }
                    </style>
                </head>
                <body>
                    <h1>Notlarım</h1>
                    <ul>
                """)
                for note in self.notes:
                    tags = ", ".join(note["tags"])
                    priority_class = f"priority-{note['priority']}"
                    file.write(f"""
                        <li class="{priority_class}">
                            <strong>{note['note']}</strong>
                            <div class="tags">Etiketler: {tags}</div>
                            <div class="date">Tarih: {note['date_time']} | Tip: {note['type']}</div>
                        </li>
                    """)
                file.write("</ul></body></html>")
            print(f"Notes exported to {html_file}.")
        except Exception as e:
            print(f"Error exporting notes: {e}")

class ModernButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.default_bg = self.cget('style')
    
    def on_enter(self, e):
        self.configure(style='Accent.TButton')
    
    def on_leave(self, e):
        self.configure(style=self.default_bg)

class NotesGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Securonis Notes")
        self.root.geometry("1200x800")
        self.notes_app = TerminalNotes()
        
        # Modern tema renkleri
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'accent_hover': '#0099ff',
            'button_bg': '#2d2d2d',
            'button_fg': '#ffffff',
            'entry_bg': '#2d2d2d',
            'entry_fg': '#ffffff',
            'text_bg': '#2d2d2d',
            'text_fg': '#ffffff',
            'tree_bg': '#2d2d2d',
            'tree_fg': '#ffffff',
            'tree_selected': '#3d3d3d',
            'border': '#404040',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336'
        }
        
        # Ana pencere stil ayarları
        self.root.configure(bg=self.colors['bg'])
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Özel fontlar
        self.title_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
        self.heading_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.text_font = tkfont.Font(family="Helvetica", size=10)
        
        # Widget stilleri
        self.style.configure("TFrame", background=self.colors['bg'])
        self.style.configure("TLabel", 
                           background=self.colors['bg'],
                           foreground=self.colors['fg'],
                           font=self.text_font)
        
        # Normal buton stili
        self.style.configure("TButton",
                           background=self.colors['button_bg'],
                           foreground=self.colors['button_fg'],
                           padding=8,
                           font=self.text_font)
        
        # Vurgu buton stili
        self.style.configure("Accent.TButton",
                           background=self.colors['accent'],
                           foreground=self.colors['button_fg'],
                           padding=8,
                           font=self.text_font)
        
        self.style.configure("TRadiobutton",
                           background=self.colors['bg'],
                           foreground=self.colors['fg'],
                           font=self.text_font)
        
        self.style.configure("Treeview",
                           background=self.colors['tree_bg'],
                           foreground=self.colors['tree_fg'],
                           fieldbackground=self.colors['tree_bg'],
                           rowheight=30,
                           font=self.text_font)
        
        self.style.configure("Treeview.Heading",
                           background=self.colors['button_bg'],
                           foreground=self.colors['fg'],
                           font=self.text_font)
        
        self.style.map("Treeview",
                      background=[('selected', self.colors['tree_selected'])])
        
        self.create_widgets()
        
    def create_widgets(self):
        # Üst menü çubuğu
        self.create_menu_bar()
        
        # Ana container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Sol panel - Not listesi
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Not listesi başlığı ve arama
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="My Notes", 
                 font=self.title_font).pack(side=tk.LEFT)
        
        # Arama çubuğu
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_notes)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X)
        
        # Filtreler
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_priority = ttk.Combobox(filter_frame, values=["All", "Low", "Medium", "High"], 
                                          state="readonly", width=10)
        self.filter_priority.set("All")
        self.filter_priority.pack(side=tk.LEFT, padx=5)
        self.filter_priority.bind('<<ComboboxSelected>>', self.apply_filters)
        
        self.filter_type = ttk.Combobox(filter_frame, values=["All", "Event", "Reminder"], 
                                      state="readonly", width=10)
        self.filter_type.set("All")
        self.filter_type.pack(side=tk.LEFT, padx=5)
        self.filter_type.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Not listesi
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notes_list = ttk.Treeview(list_frame, 
                                     columns=("priority", "date", "type"),
                                     show="headings",
                                     height=20)
        self.notes_list.heading("priority", text="Priority")
        self.notes_list.heading("date", text="Date")
        self.notes_list.heading("type", text="Type")
        self.notes_list.column("priority", width=100)
        self.notes_list.column("date", width=150)
        self.notes_list.column("type", width=100)
        self.notes_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.notes_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_list.configure(yscrollcommand=scrollbar.set)
        
        # Sağ panel - Not detayları ve işlemler
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Not detayları başlığı
        ttk.Label(right_frame, text="Note Details", 
                 font=self.heading_font).pack(pady=(0, 10))
        
        # Not içeriği
        note_frame = ttk.Frame(right_frame)
        note_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(note_frame, text="Note:", font=self.text_font).pack(anchor=tk.W)
        self.note_text = tk.Text(note_frame, height=4, width=40,
                               bg=self.colors['text_bg'],
                               fg=self.colors['text_fg'],
                               insertbackground=self.colors['fg'],
                               font=self.text_font,
                               relief="flat")
        self.note_text.pack(fill=tk.X)
        
        # Etiketler
        tags_frame = ttk.Frame(right_frame)
        tags_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(tags_frame, text="Tags (comma separated):", 
                 font=self.text_font).pack(anchor=tk.W)
        self.tags_entry = ttk.Entry(tags_frame)
        self.tags_entry.pack(fill=tk.X)
        
        # Öncelik seçimi
        priority_frame = ttk.Frame(right_frame)
        priority_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(priority_frame, text="Priority:", 
                 font=self.text_font).pack(anchor=tk.W)
        self.priority_var = tk.StringVar(value="low")
        for priority in ["low", "medium", "high"]:
            ttk.Radiobutton(priority_frame, text=priority.capitalize(),
                          variable=self.priority_var,
                          value=priority).pack(side=tk.LEFT, padx=5)
        
        # Tarih ve saat
        datetime_frame = ttk.Frame(right_frame)
        datetime_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(datetime_frame, text="Date and Time:", 
                 font=self.text_font).pack(anchor=tk.W)
        
        date_time_container = ttk.Frame(datetime_frame)
        date_time_container.pack(fill=tk.X)
        
        self.datetime_entry = ttk.Entry(date_time_container)
        self.datetime_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.datetime_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        ttk.Button(date_time_container, text="Calendar", 
                  command=self.show_calendar_picker).pack(side=tk.RIGHT, padx=5)
        
        # Not tipi
        type_frame = ttk.Frame(right_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(type_frame, text="Type:", 
                 font=self.text_font).pack(anchor=tk.W)
        self.type_var = tk.StringVar(value="event")
        for note_type in ["event", "reminder"]:
            ttk.Radiobutton(type_frame, text=note_type.capitalize(),
                          variable=self.type_var,
                          value=note_type).pack(side=tk.LEFT, padx=5)
        
        # Butonlar
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ModernButton(button_frame, text="New Note", 
                    command=self.add_note,
                    style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ModernButton(button_frame, text="Update", 
                    command=self.update_note).pack(side=tk.LEFT, padx=5)
        ModernButton(button_frame, text="Delete", 
                    command=self.delete_note).pack(side=tk.LEFT, padx=5)
        
        # İçe/Dışa aktarma butonları
        import_export_frame = ttk.Frame(right_frame)
        import_export_frame.pack(fill=tk.X, pady=5)
        
        ModernButton(import_export_frame, text="Import from CSV",
                    command=self.import_notes).pack(side=tk.LEFT, padx=5)
        ModernButton(import_export_frame, text="Export to CSV",
                    command=self.export_notes).pack(side=tk.LEFT, padx=5)
        ModernButton(import_export_frame, text="Export to HTML",
                    command=self.export_notes_html).pack(side=tk.LEFT, padx=5)
        
        # İstatistikler
        stats_frame = ttk.Frame(right_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        self.stats_label = ttk.Label(stats_frame, text="", font=self.text_font)
        self.stats_label.pack(fill=tk.X)
        
        # Not listesini güncelle
        self.refresh_notes_list()
        
        # Not seçildiğinde detayları göster
        self.notes_list.bind('<<TreeviewSelect>>', self.on_select_note)
        
        # İstatistikleri güncelle
        self.update_stats()
    
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu styles
        menu_bg = self.colors['bg']
        menu_fg = self.colors['fg']
        menu_active_bg = self.colors['accent']
        menu_active_fg = self.colors['fg']
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, 
                          bg=menu_bg, fg=menu_fg,
                          activebackground=menu_active_bg,
                          activeforeground=menu_active_fg,
                          selectcolor=menu_bg)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Note", command=self.add_note)
        file_menu.add_command(label="Import from CSV", command=self.import_notes)
        file_menu.add_command(label="Export to CSV", command=self.export_notes)
        file_menu.add_command(label="Export to HTML", command=self.export_notes_html)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0,
                          bg=menu_bg, fg=menu_fg,
                          activebackground=menu_active_bg,
                          activeforeground=menu_active_fg,
                          selectcolor=menu_bg)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Update", command=self.update_note)
        edit_menu.add_command(label="Delete", command=self.delete_note)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all)
        edit_menu.add_command(label="Deselect All", command=self.deselect_all)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0,
                          bg=menu_bg, fg=menu_fg,
                          activebackground=menu_active_bg,
                          activeforeground=menu_active_fg,
                          selectcolor=menu_bg)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Calendar", command=self.show_calendar)
        view_menu.add_separator()
        view_menu.add_command(label="Show/Hide Statistics", command=self.toggle_stats)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0,
                           bg=menu_bg, fg=menu_fg,
                           activebackground=menu_active_bg,
                           activeforeground=menu_active_fg,
                           selectcolor=menu_bg)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Backup Notes", command=self.backup_notes)
        tools_menu.add_command(label="Restore from Backup", command=self.restore_notes)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0,
                          bg=menu_bg, fg=menu_fg,
                          activebackground=menu_active_bg,
                          activeforeground=menu_active_fg,
                          selectcolor=menu_bg)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="User Guide", command=self.show_help)
    
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x300")
        about_window.configure(bg=self.colors['bg'])
        
        ttk.Label(about_window, text="Securonis Notes",
                 font=self.title_font).pack(pady=20)
        
        ttk.Label(about_window, text="Secure Note Taking Application",
                 font=self.heading_font).pack(pady=10)
        
        ttk.Label(about_window, text="Version 1.0\n\n"
                 "This application allows you to securely\n"
                 "store and manage your notes.",
                 font=self.text_font).pack(pady=20)
    
    def show_calendar_picker(self):
        calendar_window = tk.Toplevel(self.root)
        calendar_window.title("Date Picker")
        calendar_window.geometry("300x400")
        calendar_window.configure(bg=self.colors['bg'])
        
        cal = Calendar(calendar_window, selectmode='day',
                      year=datetime.now().year,
                      month=datetime.now().month,
                      day=datetime.now().day,
                      background=self.colors['bg'],
                      foreground=self.colors['fg'],
                      selectbackground=self.colors['accent'],
                      normalbackground=self.colors['button_bg'],
                      normalforeground=self.colors['fg'])
        cal.pack(pady=20)
        
        def set_date():
            selected_date = cal.get_date()
            current_time = datetime.now().strftime("%H:%M")
            self.datetime_entry.delete(0, tk.END)
            self.datetime_entry.insert(0, f"{selected_date} {current_time}")
            calendar_window.destroy()
        
        ttk.Button(calendar_window, text="Select",
                  command=set_date).pack(pady=10)
    
    def update_stats(self):
        total_notes = len(self.notes_app.notes)
        high_priority = sum(1 for note in self.notes_app.notes if note["priority"] == "high")
        medium_priority = sum(1 for note in self.notes_app.notes if note["priority"] == "medium")
        low_priority = sum(1 for note in self.notes_app.notes if note["priority"] == "low")
        
        stats_text = f"Total Notes: {total_notes} | High Priority: {high_priority} | "
        stats_text += f"Medium Priority: {medium_priority} | Low Priority: {low_priority}"
        
        self.stats_label.configure(text=stats_text)
    
    def apply_filters(self, *args):
        self.refresh_notes_list()
    
    def filter_notes(self, *args):
        search_term = self.search_var.get().lower()
        self.refresh_notes_list(search_term)
    
    def refresh_notes_list(self, search_term=None):
        # Mevcut listeyi temizle
        for item in self.notes_list.get_children():
            self.notes_list.delete(item)
        
        # Filtreleri al
        priority_filter = self.filter_priority.get()
        type_filter = self.filter_type.get()
        
        # Notları listeye ekle
        for note in self.notes_app.notes:
            # Arama filtresi
            if search_term and search_term not in note["note"].lower():
                continue
            
            # Öncelik filtresi
            if priority_filter != "All" and note["priority"].capitalize() != priority_filter:
                continue
            
            # Tip filtresi
            if type_filter != "All" and note["type"].capitalize() != type_filter:
                continue
            
            self.notes_list.insert("", tk.END, values=(
                note["priority"].capitalize(),
                note["date_time"],
                note["type"].capitalize()
            ), text=note["note"])
        
        # İstatistikleri güncelle
        self.update_stats()
    
    def on_select_note(self, event):
        selected = self.notes_list.selection()
        if not selected:
            return
        
        note_index = self.notes_list.index(selected[0])
        note = self.notes_app.notes[note_index]
        
        # Form alanlarını doldur
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", note["note"])
        
        self.tags_entry.delete(0, tk.END)
        self.tags_entry.insert(0, ", ".join(note["tags"]))
        
        self.priority_var.set(note["priority"])
        self.datetime_entry.delete(0, tk.END)
        self.datetime_entry.insert(0, note["date_time"])
        self.type_var.set(note["type"])
    
    def add_note(self):
        note = self.note_text.get("1.0", tk.END).strip()
        tags = [tag.strip() for tag in self.tags_entry.get().split(",")]
        priority = self.priority_var.get()
        date_time = self.datetime_entry.get()
        note_type = self.type_var.get()
        
        if not note:
            messagebox.showerror("Error", "Note content cannot be empty!")
            return
        
        self.notes_app.add_note(note, tags, priority, date_time, note_type)
        self.refresh_notes_list()
        self.clear_fields()
        messagebox.showinfo("Success", "Note added!")
    
    def update_note(self):
        selected = self.notes_list.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a note to update!")
            return
        
        note_index = self.notes_list.index(selected[0])
        new_note = self.note_text.get("1.0", tk.END).strip()
        new_tags = [tag.strip() for tag in self.tags_entry.get().split(",")]
        new_priority = self.priority_var.get()
        new_date_time = self.datetime_entry.get()
        new_type = self.type_var.get()
        
        if not new_note:
            messagebox.showerror("Error", "Note content cannot be empty!")
            return
        
        self.notes_app.update_note(note_index + 1, new_note, new_tags, new_priority, new_date_time, new_type)
        self.refresh_notes_list()
        self.clear_fields()
        messagebox.showinfo("Success", "Note updated!")
    
    def delete_note(self):
        selected = self.notes_list.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a note to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this note?"):
            note_index = self.notes_list.index(selected[0])
            self.notes_app.delete_note(note_index + 1)
            self.refresh_notes_list()
            self.clear_fields()
            messagebox.showinfo("Success", "Note deleted!")
    
    def import_notes(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.notes_app.import_notes(file_path)
            self.refresh_notes_list()
    
    def export_notes(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.notes_app.export_notes(file_path)
    
    def export_notes_html(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        if file_path:
            self.notes_app.export_notes_html(file_path)
    
    def show_calendar(self):
        calendar_window = tk.Toplevel(self.root)
        calendar_window.title("Calendar")
        calendar_window.geometry("300x300")
        calendar_window.configure(bg=self.colors['bg'])
        
        current_date = datetime.now()
        cal_text = calendar.month(current_date.year, current_date.month)
        
        text_widget = tk.Text(calendar_window, height=10, width=30,
                            bg=self.colors['text_bg'],
                            fg=self.colors['text_fg'],
                            font=('Courier', 10))
        text_widget.pack(padx=10, pady=10)
        text_widget.insert("1.0", cal_text)
        text_widget.config(state="disabled")
    
    def clear_fields(self):
        self.note_text.delete("1.0", tk.END)
        self.tags_entry.delete(0, tk.END)
        self.priority_var.set("low")
        self.datetime_entry.delete(0, tk.END)
        self.datetime_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.type_var.set("event")
    
    def select_all(self):
        for item in self.notes_list.get_children():
            self.notes_list.selection_add(item)
    
    def deselect_all(self):
        for item in self.notes_list.get_children():
            self.notes_list.selection_remove(item)
    
    def toggle_stats(self):
        if self.stats_label.winfo_viewable():
            self.stats_label.pack_forget()
        else:
            self.stats_label.pack(fill=tk.X)
    
    def backup_notes(self):
        try:
            backup_dir = os.path.join(os.path.expanduser("~"), "SecuronisNotes", "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"notes_backup_{timestamp}.json")
            
            # Backup notes
            with open(backup_file, 'wb') as file:
                file.write(self.notes_app.fernet.encrypt(json.dumps(self.notes_app.notes).encode()))
            
            messagebox.showinfo("Success", f"Notes successfully backed up to:\n{backup_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Error during backup:\n{str(e)}")
    
    def restore_notes(self):
        try:
            backup_dir = os.path.join(os.path.expanduser("~"), "SecuronisNotes", "backups")
            if not os.path.exists(backup_dir):
                messagebox.showerror("Error", "Backup directory not found!")
                return
            
            file_path = filedialog.askopenfilename(
                initialdir=backup_dir,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'rb') as file:
                    encrypted_data = file.read()
                    decrypted_data = self.notes_app.fernet.decrypt(encrypted_data).decode()
                    self.notes_app.notes = json.loads(decrypted_data)
                    self.notes_app.save_notes()
                    self.refresh_notes_list()
                    messagebox.showinfo("Success", "Notes successfully restored!")
        except Exception as e:
            messagebox.showerror("Error", f"Error during restore:\n{str(e)}")
    
    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("User Guide")
        help_window.geometry("600x400")
        help_window.configure(bg=self.colors['bg'])
        
        help_text = """
Securonis Notes User Guide

1. Adding Notes:
   - Click "New Note" button
   - Enter note content
   - Add tags (comma separated)
   - Set priority level
   - Select date and time
   - Choose note type (Event/Reminder)

2. Editing Notes:
   - Select a note from the list
   - Edit required fields
   - Click "Update" button

3. Deleting Notes:
   - Select a note from the list
   - Click "Delete" button
   - Confirm deletion

4. Filtering Notes:
   - Use search bar
   - Use priority and type filters

5. Import/Export:
   - Import from CSV
   - Export to CSV
   - Export to HTML

6. Backup:
   - Manual backup
   - Restore from backup

7. Security:
   - Notes are encrypted
   - Secure key management
"""
        
        text_widget = tk.Text(help_window, wrap=tk.WORD,
                            bg=self.colors['text_bg'],
                            fg=self.colors['text_fg'],
                            font=self.text_font)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled")

def main():
    root = tk.Tk()
    app = NotesGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
