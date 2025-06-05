import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
from pathlib import Path
import logging
from typing import Optional, Dict, List
import json
from datetime import datetime
from .core import DirectoryManager, FileInfo

class DirectoryToolGUI:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.manager = DirectoryManager()
        
        # Create themed root window
        self.root = ThemedTk(theme="radiance")
        self.root.title("Directory Tool")
        self.root.geometry("1024x768")
        
        # Create menu
        self.create_menu()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.create_status_bar()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.create_structure_tab()
        self.create_move_files_tab()
        self.create_organize_tab()
        self.create_templates_tab()
        
        # Load configuration
        self.load_config()
        
    def create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Structure", command=self.new_structure)
        file_menu.add_command(label="Load Template", command=self.load_template)
        file_menu.add_command(label="Save Template", command=self.save_template)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        view_menu.add_separator()
        view_menu.add_command(label="Operation History", command=self.show_history)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Directory Statistics", command=self.show_stats)
        tools_menu.add_command(label="Cleanup Empty Folders", command=self.cleanup_empty)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_status_bar(self):
        """Create status bar at bottom of window."""
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")
        
    def create_structure_tab(self):
        """Create the Define & Create Structure tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Define & Create Structure')
        
        # Structure definition frame
        def_frame = ttk.LabelFrame(tab, text="Structure Definition", padding=5)
        def_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Structure text area with line numbers
        text_frame = ttk.Frame(def_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.line_numbers = tk.Text(text_frame, width=4, padx=3, takefocus=0,
                                  border=0, background='lightgray')
        self.line_numbers.pack(side='left', fill='y')
        
        self.structure_text = tk.Text(text_frame, height=15, wrap='none')
        self.structure_text.pack(side='left', fill='both', expand=True)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(text_frame, orient='vertical', 
                               command=self.structure_text.yview)
        y_scroll.pack(side='right', fill='y')
        
        x_scroll = ttk.Scrollbar(tab, orient='horizontal',
                               command=self.structure_text.xview)
        x_scroll.pack(fill='x')
        
        self.structure_text.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        
        # Bind text changes to line number update
        self.structure_text.bind('<KeyPress>', self.update_line_numbers)
        self.structure_text.bind('<KeyRelease>', self.update_line_numbers)
        
        # Buttons frame
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            btn_frame,
            text="Create Structure",
            command=self.create_structure
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Preview Structure",
            command=self.preview_structure
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Clear",
            command=lambda: self.structure_text.delete('1.0', 'end')
        ).pack(side='left', padx=5)
        
    def create_move_files_tab(self):
        """Create the Quick Move Files tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Quick Move Files')
        
        # File list frame
        list_frame = ttk.LabelFrame(tab, text="Selected Files", padding=5)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # File tree with scrollbar
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill='both', expand=True)
        
        self.file_tree = ttk.Treeview(
            tree_frame,
            columns=('Size', 'Type', 'Modified'),
            selectmode='extended'
        )
        self.file_tree.heading('#0', text='Path')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Modified', text='Modified')
        
        y_scroll = ttk.Scrollbar(tree_frame, orient='vertical',
                               command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=y_scroll.set)
        
        self.file_tree.pack(side='left', fill='both', expand=True)
        y_scroll.pack(side='right', fill='y')
        
        # Buttons frame
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            btn_frame,
            text="Select Files",
            command=self.select_files
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Select Folder",
            command=self.select_folder
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Move Selected",
            command=self.move_selected_files
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Clear Selection",
            command=self.clear_selection
        ).pack(side='left', padx=5)
        
    def create_organize_tab(self):
        """Create the Smart Organize & Package tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Smart Organize & Package')
        
        # Create paned window for left and right sides
        paned = ttk.PanedWindow(tab, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left side - Source files
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Staging area
        stage_frame = ttk.LabelFrame(left_frame, text="Staging Area", padding=5)
        stage_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.stage_tree = ttk.Treeview(
            stage_frame,
            columns=('Size', 'Type'),
            selectmode='extended'
        )
        self.stage_tree.heading('#0', text='Path')
        self.stage_tree.heading('Size', text='Size')
        self.stage_tree.heading('Type', text='Type')
        self.stage_tree.pack(fill='both', expand=True)
        
        # Right side - Target structure
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        # Target structure definition
        target_frame = ttk.LabelFrame(right_frame, text="Target Structure", padding=5)
        target_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.target_tree = ttk.Treeview(
            target_frame,
            columns=('Status',),
            selectmode='extended'
        )
        self.target_tree.heading('#0', text='Path')
        self.target_tree.heading('Status', text='Status')
        self.target_tree.pack(fill='both', expand=True)
        
        # Buttons frame
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            btn_frame,
            text="Add to Stage",
            command=self.add_to_stage
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Auto-Organize",
            command=self.auto_organize
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Create Package",
            command=self.create_package
        ).pack(side='left', padx=5)
        
    def create_templates_tab(self):
        """Create the Manage Templates tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Manage Templates')
        
        # Templates list frame
        list_frame = ttk.LabelFrame(tab, text="Saved Templates", padding=5)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.template_tree = ttk.Treeview(
            list_frame,
            columns=('Modified',),
            selectmode='browse'
        )
        self.template_tree.heading('#0', text='Name')
        self.template_tree.heading('Modified', text='Last Modified')
        self.template_tree.pack(fill='both', expand=True)
        
        # Buttons frame
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            btn_frame,
            text="New Template",
            command=self.new_template
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Import Template",
            command=self.import_template
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Export Template",
            command=self.export_template
        ).pack(side='left', padx=5)
        
    def update_line_numbers(self, event=None):
        """Update line numbers in structure definition."""
        lines = self.structure_text.get('1.0', 'end').count('\n')
        line_numbers = '\n'.join(str(i) for i in range(1, lines + 1))
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers)
        
    def load_config(self):
        """Load application configuration."""
        try:
            config_path = Path('data/config.json')
            if config_path.exists():
                with config_path.open() as f:
                    config = json.load(f)
                    if 'theme' in config:
                        self.root.set_theme(config['theme'])
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            
    def save_config(self):
        """Save application configuration."""
        try:
            config_path = Path('data/config.json')
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config = {
                'theme': self.root.get_theme(),
                'last_save': datetime.now().isoformat()
            }
            with config_path.open('w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_theme = self.root.get_theme()
        new_theme = "equilux" if current_theme == "radiance" else "radiance"
        self.root.set_theme(new_theme)
        self.save_config()
        
    def show_history(self):
        """Show operation history dialog."""
        history = tk.Toplevel(self.root)
        history.title("Operation History")
        history.geometry("600x400")
        
        tree = ttk.Treeview(history, columns=('Time', 'Details'))
        tree.heading('#0', text='Operation')
        tree.heading('Time', text='Time')
        tree.heading('Details', text='Details')
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        for op in self.manager._operation_history:
            tree.insert(
                '',
                'end',
                text=op['operation'],
                values=(
                    op['timestamp'],
                    f"Items: {op.get('items_created', op.get('files_moved', 0))}"
                )
            )
            
    def show_stats(self):
        """Show directory statistics dialog."""
        dir_path = filedialog.askdirectory(title="Select Directory for Statistics")
        if dir_path:
            try:
                stats = self.manager.get_directory_stats(dir_path)
                messagebox.showinfo(
                    "Directory Statistics",
                    f"Files: {stats['file_count']}\n"
                    f"Directories: {stats['dir_count']}\n"
                    f"Total Size: {stats['total_size']:,} bytes\n"
                    f"Last Modified: {stats['last_modified']}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to get statistics: {e}")
                
    def cleanup_empty(self):
        """Clean up empty directories."""
        dir_path = filedialog.askdirectory(title="Select Directory to Clean")
        if dir_path:
            try:
                count = self.manager.cleanup_empty_dirs(dir_path)
                messagebox.showinfo(
                    "Cleanup Complete",
                    f"Removed {count} empty directories."
                )
            except Exception as e:
                messagebox.showerror("Error", f"Cleanup failed: {e}")
                
    def show_docs(self):
        """Show documentation dialog."""
        docs = tk.Toplevel(self.root)
        docs.title("Documentation")
        docs.geometry("800x600")
        
        text = tk.Text(docs, wrap='word', padx=10, pady=10)
        text.pack(fill='both', expand=True)
        
        # Load documentation content
        text.insert('1.0', """Directory Tool Documentation
        
This application helps you manage and organize directory structures and files.

Key Features:
1. Define and create directory structures
2. Quick file moving with conflict resolution
3. Smart organization with templates
4. Package creation and management

For more information, visit the project homepage.""")
        text.config(state='disabled')
        
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Directory Tool",
            "Directory Tool v1.0.0\n\n"
            "A modern directory management and organization tool.\n\n"
            "© 2025 jigar48949"
        )
        
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()
        self.save_config()

def main():
    """Entry point for the GUI application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('directory_tool.log'),
            logging.StreamHandler()
        ]
    )
    
    # Start application
    app = DirectoryToolGUI()
    app.run()

if __name__ == '__main__':
    main()