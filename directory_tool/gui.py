import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from pathlib import Path
import logging
from typing import Optional
from .core import DirectoryManager

class DirectoryToolGUI:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.manager = DirectoryManager()
        
        # Create themed root window
        self.root = ThemedTk(theme="radiance")
        self.root.title("Directory Tool")
        self.root.geometry("800x600")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.create_structure_tab()
        self.create_move_files_tab()
        self.create_organize_tab()
        self.create_templates_tab()
        
    def create_structure_tab(self):
        """Create the Define & Create Structure tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Define & Create Structure')
        
        # Structure definition text area
        self.structure_text = tk.Text(tab, height=10)
        self.structure_text.pack(fill='both', expand=True, padx=5, pady=5)
        
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
        
    def create_move_files_tab(self):
        """Create the Quick Move Files tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Quick Move Files')
        
        # File list
        self.file_tree = ttk.Treeview(tab, columns=('Size', 'Type'))
        self.file_tree.heading('#0', text='Path')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
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
            text="Move Selected",
            command=self.move_selected_files
        ).pack(side='left', padx=5)
        
    def create_organize_tab(self):
        """Create the Smart Organize & Package tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Smart Organize & Package')
        
        # To be implemented
        ttk.Label(tab, text="Smart organization features coming soon...").pack()
        
    def create_templates_tab(self):
        """Create the Manage Templates tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Manage Templates')
        
        # To be implemented
        ttk.Label(tab, text="Template management features coming soon...").pack()
        
    def create_structure(self):
        """Create directory structure from text input."""
        structure = self.structure_text.get('1.0', 'end')
        # Add file dialog to select base path
        
    def preview_structure(self):
        """Preview the directory structure."""
        # Implement structure preview
        pass
        
    def select_files(self):
        """Open file dialog to select files."""
        # Implement file selection
        pass
        
    def move_selected_files(self):
        """Move selected files to target directory."""
        # Implement file moving
        pass
        
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

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