import os
import shutil
import json
import zipfile
import logging
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Listbox
from tkinter import ttk
from ttkthemes import ThemedTk
from thefuzz import fuzz
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import threading

# --- Constants ---
CONFIG_FILE_NAME = "config.json"
HISTORY_FILE_NAME = "history.json"
TEMPLATES_FILE_NAME = "templates.json"
LOG_FILE_NAME = "directory_tool.log"
DEFAULT_THEME = "radiance"
DARK_THEME = "equilux" # Example dark theme from ttkthemes

# Statuses for Smart Organize
STATUS_MISSING = "Missing"
STATUS_MATCHED = "Auto-Matched"  # From general pool auto-match
STATUS_ASSIGNED = "Assigned"     # Manually via stage, browse, or auto-assign from stage

# For conceptual TkinterDnD2 integration
# from TkinterDnD2 import DND_FILES, TkinterDnD

class DirectoryTool:
    def __init__(self, root_window: ThemedTk):
        self.root = root_window
        # If using TkinterDnD2, root_window might need to be TkinterDnD.Tk()
        # self.root = TkinterDnD.Tk() # Then apply theme
        self.root.title("Directory Tool v1.0")
        self.root.geometry("1250x900") # Adjusted size for better layout

        self.script_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()
        self.setup_logging()

        self.data_dir = self.script_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True) # Ensure parent dirs exist
        self.history_file = self.data_dir / HISTORY_FILE_NAME
        self.templates_file = self.data_dir / TEMPLATES_FILE_NAME
        self.config_file = self.data_dir / CONFIG_FILE_NAME

        self.config = self.load_json(self.config_file, {"theme": DEFAULT_THEME, "last_directory": ""})
        try:
            self.root.set_theme(self.config.get("theme", DEFAULT_THEME))
        except Exception as e:
            self.logger.warning(f"Failed to set theme from config: {e}. Using default '{DEFAULT_THEME}'.")
            self.root.set_theme(DEFAULT_THEME)

        self.history = self.load_json(self.history_file, [])
        self.templates = self.load_json(self.templates_file, {"templates": []})

        self.current_operation = None
        self.cancel_operation = False
        
        # Smart Organize specific state
        self.source_files_pool: List[Path] = [] # For "Load Source Pool" & "Auto-Match from Pool"
        self.staged_files: List[Path] = []      # For "File Staging Area"
        self.smart_organize_skeleton: List[Dict[str, Any]] = []

        # Tkinter variables
        self.base_dir_var = tk.StringVar() # Initialize here, used in create_common_directory_selection_frame
        self.source_pool_count_var = tk.StringVar(value="Pool: 0 files") # For Smart Organize tab
        self.smart_organize_completion_var = tk.StringVar(value="Completion: 0.00%")
        self.smart_organize_progress = tk.DoubleVar(value=0.0) # Added for the progress bar in smart organize
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar()


        self.create_menu()
        self.create_tabs()
        self.create_status_bar() # Defined progress_bar inside

        if self.config.get("last_directory") and Path(self.config["last_directory"]).exists():
            self.base_dir_var.set(self.config["last_directory"])

        self.refresh_templates_list()
        self._update_undo_menu_state()

    def setup_logging(self):
        log_dir = self.script_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / LOG_FILE_NAME, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Application started. CWD: {Path.cwd()}")

    def load_json(self, file_path: Path, default: Any) -> Any:
        try:
            with file_path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.info(f"File not found, using default: {file_path}")
            # Create the file with default content if it doesn't exist
            self.save_json(file_path, default)
            return default
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error in {file_path}: {e}")
            backup_path = file_path.with_suffix(f".corrupted.{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
            if file_path.exists(): 
                try: shutil.copy(file_path, backup_path); self.logger.info(f"Backed up corrupted file to {backup_path}")
                except Exception as e_copy: self.logger.error(f"Failed to backup corrupted file {file_path}: {e_copy}")
            self.save_json(file_path, default) # Save default to fix corruption for next run
            return default
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return default

    def save_json(self, file_path: Path, data: Any) -> bool:
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {e}")
            if hasattr(self, 'root') and self.root.winfo_exists(): # Check if GUI is up
                messagebox.showerror("Save Error", f"Failed to save {file_path.name}: {e}", parent=self.root)
            return False

    def log_operation(self, message: str, level: str = "info"):
        # getattr allows calling logger.info(), logger.error() etc. dynamically
        getattr(self.logger, level, self.logger.info)(message)

    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File Menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Load Structure Definition", command=self.load_structure_definition, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Structure Definition", command=self.save_structure_definition, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Import Template", command=self.import_template)
        file_menu.add_command(label="Export Template", command=self.export_template)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Edit Menu
        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo Last Operation", command=self.undo_last_operation, accelerator="Ctrl+Z", state=tk.DISABLED) 
        self.edit_menu.add_command(label="Clear History", command=self.clear_history)
        
        # View Menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode, accelerator="Ctrl+D")
        view_menu.add_command(label="Show History", command=self.show_history)
        view_menu.add_command(label="Show Templates", command=self.show_templates_tab)
        
        # Tools Menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Directory Statistics", command=self.show_directory_stats)
        tools_menu.add_command(label="Cleanup Empty Folders", command=self.cleanup_empty_folders)
        
        # Help Menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bindings (using lambda to pass command reference)
        for key, cmd_func in [
            ('<Control-n>', self.new_project), 
            ('<Control-o>', self.load_structure_definition),
            ('<Control-s>', self.save_structure_definition), 
            ('<Control-z>', self.undo_last_operation),
            ('<Control-d>', self.toggle_dark_mode), 
            ('<Control-q>', self.on_closing)
        ]:
            self.root.bind_all(key, lambda event, cmd=cmd_func: cmd())


    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.create_structure_tab(self.notebook)
        self.create_move_files_tab(self.notebook)
        self.create_smart_organize_tab(self.notebook)
        self.create_templates_tab(self.notebook)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

    def create_status_bar(self):
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill="x", side="bottom", pady=(0,5), padx=5)
        ttk.Label(self.status_frame, textvariable=self.status_var, relief="sunken", anchor="w").pack(side="left", fill="x", expand=True, padx=(5,0))
        # Define self.progress_bar here
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, mode='determinate', length=200)
        self.progress_bar.pack(side="right", padx=5)


    def update_status(self, message: str, progress: Optional[float] = None, clear_progress_on_ready=True):
        self.status_var.set(message)
        if progress is not None:
            self.progress_var.set(progress)
            if hasattr(self, 'progress_bar'): # Check if progress_bar exists
                 self.progress_bar.config(mode='determinate' if progress >= 0 else 'indeterminate')
        elif clear_progress_on_ready and message.lower() == "ready":
            self.progress_var.set(0)
        if hasattr(self, 'root') and self.root.winfo_exists(): # Check if GUI is still running
            self.root.update_idletasks()

    def _start_operation(self, op_name: str) -> bool:
        if self.current_operation:
            messagebox.showwarning("Operation in Progress", f"'{self.current_operation}' is running. Please wait.", parent=self.root)
            return False
        self.current_operation = op_name
        self.cancel_operation = False
        self.update_status(f"Starting {op_name}...", -1) # Indeterminate progress
        return True

    def _finish_operation(self, success_msg: Optional[str] = "Operation completed.", error_msg: Optional[str] = "Operation failed or was cancelled."):
        final_msg = ""
        if self.cancel_operation:
            final_msg = f"{self.current_operation or 'Operation'} was cancelled by the user."
            self.update_status(final_msg, 0)
            if hasattr(self, 'root') and self.root.winfo_exists(): # Check GUI
                messagebox.showinfo("Cancelled", final_msg, parent=self.root)
        elif success_msg: # Only if not cancelled
            final_msg = success_msg
            self.update_status(final_msg, 100)
        elif error_msg: # Only if not cancelled and no success_msg
            final_msg = error_msg
            self.update_status(final_msg, 0)
        
        self.logger.info(f"Finished operation '{self.current_operation}': {final_msg if final_msg else 'Completed silently'}")
        self.current_operation = None
        self.cancel_operation = False # Reset for next operation
        self._update_undo_menu_state()

    def _update_undo_menu_state(self):
        # Check if edit_menu attribute exists and the widget itself still exists
        if hasattr(self, 'edit_menu') and self.edit_menu.winfo_exists():
            try:
                # Assuming "Undo Last Operation" is the first item (index 0)
                state = tk.NORMAL if self.history else tk.DISABLED
                self.edit_menu.entryconfig(0, state=state)
            except tk.TclError as e: # Catch TclError if menu item doesn't exist by index
                self.logger.warning(f"Could not update undo menu state (TclError): {e}")
            except AttributeError as e: # Catch if edit_menu is not a Menu widget
                self.logger.warning(f"Could not update undo menu state (AttributeError): {e}")
        else:
            # This might happen if called too early or after menu destruction
            self.logger.debug("edit_menu not available for updating undo state.")
    
    def create_structure_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="1. Define & Create Structure")
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        structure_frame = ttk.LabelFrame(main_frame, text="Directory Structure Definition", padding=10)
        structure_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        text_widget_container = ttk.Frame(structure_frame)
        text_widget_container.pack(fill="both", expand=True)
        self.structure_text = TextWithScrollbars(text_widget_container, height=15, wrap="none")
        self.structure_text.pack(fill="both", expand=True)
        
        button_frame = ttk.Frame(structure_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(button_frame, text="Load Sample", command=self.load_sample_structure).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Clear Definition", command=self.clear_structure_definition).pack(side="left", padx=(0, 5))
        
        self.create_common_directory_selection_frame(main_frame, "Base Directory for Creation")
        
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=(10,0))
        ttk.Button(action_frame, text="Create Structure Now", command=self.create_structure_threaded, style="Accent.TButton").pack(side="left", padx=(0, 5))
        ttk.Button(action_frame, text="Preview Structure", command=self.preview_structure).pack(side="left")

    def create_move_files_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="2. Quick Move Files")
        main_frame = ttk.Frame(tab); main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        files_frame = ttk.LabelFrame(main_frame, text="Files to Move", padding=10)
        files_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        button_frame = ttk.Frame(files_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(button_frame, text="Select Files", command=self.select_files_for_move).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Select Folder of Files", command=self.select_folder_for_move).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Clear List", command=self.clear_move_files_list).pack(side="left", padx=(0, 5))
        
        self.files_tree = ttk.Treeview(files_frame, columns=("File", "Size", "Type"), show="headings", height=10)
        self.files_tree.heading("File", text="File Path"); self.files_tree.column("File", width=400, anchor="w")
        self.files_tree.heading("Size", text="Size"); self.files_tree.column("Size", width=100, anchor="e")
        self.files_tree.heading("Type", text="Type"); self.files_tree.column("Type", width=100, anchor="w")
        files_scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=files_scrollbar.set)
        self.files_tree.pack(side="left", fill="both", expand=True); files_scrollbar.pack(side="right", fill="y")
        
        self.create_common_directory_selection_frame(main_frame, "Target Directory for Moving Files")
        
        action_frame = ttk.Frame(main_frame); action_frame.pack(fill="x", pady=(10,0))
        ttk.Button(action_frame, text="Move Selected Files", command=self.move_files_threaded, style="Accent.TButton").pack(side="left")

    def create_smart_organize_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="3. Smart Organize & Package")
        
        # *** THIS IS THE CORRECTED LINE ***
        paned_window = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        # ***********************************
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)


        # Left Pane: Staging Area & Pool Load
        staging_pane = ttk.Frame(paned_window, width=380) # Initial width, can be adjusted
        paned_window.add(staging_pane, weight=2) # Proportional resizing

        staging_labelframe = ttk.LabelFrame(staging_pane, text="File Staging & Pool Area", padding=10)
        staging_labelframe.pack(fill="both", expand=True, padx=5, pady=5)

        stage_buttons_frame = ttk.Frame(staging_labelframe)
        stage_buttons_frame.pack(fill="x", pady=(0,5))
        ttk.Button(stage_buttons_frame, text="Add Files to Stage", command=self.add_files_to_stage).pack(side="left", padx=(0,2), expand=True, fill=tk.X)
        ttk.Button(stage_buttons_frame, text="Add Folder to Stage", command=self.add_folder_to_stage).pack(side="left", padx=(0,2), expand=True, fill=tk.X)
        ttk.Button(stage_buttons_frame, text="Clear Stage", command=self.clear_stage).pack(side="left", expand=True, fill=tk.X)

        # Frame for Listbox and its Scrollbars
        staged_scroll_frame = ttk.Frame(staging_labelframe)
        staged_scroll_frame.pack(fill="both", expand=True, pady=(0,5))
        self.staged_files_listbox = tk.Listbox(staged_scroll_frame, selectmode=tk.EXTENDED, height=10, exportselection=False) # exportselection=False important for multi-listbox interaction
        # For TkinterDnD2:
        # self.staged_files_listbox.drop_target_register(DND_FILES)
        # self.staged_files_listbox.dnd_bind('<<Drop>>', self.handle_os_drop_on_stage)
        staged_scrollbar_y = ttk.Scrollbar(staged_scroll_frame, orient="vertical", command=self.staged_files_listbox.yview)
        staged_scrollbar_x = ttk.Scrollbar(staged_scroll_frame, orient="horizontal", command=self.staged_files_listbox.xview)
        self.staged_files_listbox.configure(yscrollcommand=staged_scrollbar_y.set, xscrollcommand=staged_scrollbar_x.set)
        
        self.staged_files_listbox.pack(side="left", fill="both", expand=True)
        staged_scrollbar_y.pack(side="right", fill="y")
        staged_scrollbar_x.pack(side="bottom", fill="x") # Pack below listbox and y-scrollbar

        assign_button_frame = ttk.Frame(staging_labelframe)
        assign_button_frame.pack(fill="x", pady=(5,0))
        ttk.Button(assign_button_frame, text="Assign Staged to Target(s) →", command=self.assign_staged_to_target, style="Accent.TButton").pack(fill="x")
        ttk.Button(assign_button_frame, text="Auto-Assign from Stage", command=self.auto_assign_from_stage_threaded).pack(fill="x", pady=(5,0))
        
        ttk.Separator(staging_labelframe, orient=tk.HORIZONTAL).pack(fill="x", pady=10)

        pool_buttons_frame = ttk.Frame(staging_labelframe)
        pool_buttons_frame.pack(fill="x", pady=(0,5))
        ttk.Button(pool_buttons_frame, text="Load Source Pool", command=self.load_source_files_for_pool).pack(side="left", padx=(0,2), expand=True, fill=tk.X)
        ttk.Button(pool_buttons_frame, text="Clear Pool", command=self.clear_source_pool).pack(side="left", padx=(0,2), expand=True, fill=tk.X)
        ttk.Label(pool_buttons_frame, textvariable=self.source_pool_count_var).pack(side="left", padx=5)
        ttk.Button(staging_labelframe, text="Auto-Match from Pool", command=self.auto_match_from_pool_threaded).pack(fill="x", pady=(5,0)) # Moved to its own line

        # Right Pane: Main Smart Organize Controls
        main_organize_pane = ttk.Frame(paned_window)
        paned_window.add(main_organize_pane, weight=3)

        structure_def_frame = ttk.LabelFrame(main_organize_pane, text="Target Structure Definition", padding=5)
        structure_def_frame.pack(fill="x", expand=False, pady=(0,5))
        text_container_smart = ttk.Frame(structure_def_frame)
        text_container_smart.pack(fill="x", expand=True)
        self.smart_organize_structure_text = TextWithScrollbars(text_container_smart, height=5, wrap="none")
        self.smart_organize_structure_text.pack(fill="x", expand=True)
        struct_button_frame = ttk.Frame(structure_def_frame); struct_button_frame.pack(fill="x", pady=(5,0))
        ttk.Button(struct_button_frame, text="Use from Tab 1", command=self.copy_structure_to_smart_organize).pack(side="left", padx=(0,2))
        ttk.Button(struct_button_frame, text="Load Sample", command=self.load_sample_for_smart_organize).pack(side="left", padx=(0,2))
        ttk.Button(struct_button_frame, text="Build/Rebuild Skeleton Tree", command=self.build_smart_organize_skeleton_threaded).pack(side="left", padx=(0,2))

        mapping_frame = ttk.LabelFrame(main_organize_pane, text="File Mapping & Status", padding=5)
        mapping_frame.pack(fill="both", expand=True, pady=(0,5))
        ttk.Button(mapping_frame, text="Clear All Assignments in Tree", command=self.clear_all_smart_organize_matches).pack(anchor="nw", pady=(0,5))

        # Frame for Treeview and its Scrollbars
        map_scroll_frame = ttk.Frame(mapping_frame)
        map_scroll_frame.pack(fill="both", expand=True)
        self.mapping_tree = ttk.Treeview(map_scroll_frame, columns=("Target", "Type", "Source", "Status"), show="headings", height=10)
        self.mapping_tree.heading("Target", text="Target Path"); self.mapping_tree.column("Target", width=250, anchor="w")
        self.mapping_tree.heading("Type", text="Type"); self.mapping_tree.column("Type", width=50, anchor="w", stretch=tk.NO)
        self.mapping_tree.heading("Source", text="Assigned Source File"); self.mapping_tree.column("Source", width=250, anchor="w")
        self.mapping_tree.heading("Status", text="Status"); self.mapping_tree.column("Status", width=100, anchor="w")

        self.mapping_tree_menu = tk.Menu(self.mapping_tree, tearoff=0)
        self.mapping_tree_menu.add_command(label="Browse & Assign Source...", command=self.manually_assign_source_file_for_selected)
        self.mapping_tree_menu.add_command(label="Clear Assignment for Selected Target(s)", command=self.clear_assignment_for_selected)
        self.mapping_tree.bind("<Button-3>", self.show_mapping_tree_menu)
        # For TkinterDnD2:
        # self.mapping_tree.drop_target_register(DND_FILES)
        # self.mapping_tree.dnd_bind('<<Drop>>', self.handle_os_drop_on_mapping_tree)
        
        mapping_scrollbar_v = ttk.Scrollbar(map_scroll_frame, orient="vertical", command=self.mapping_tree.yview)
        mapping_scrollbar_h = ttk.Scrollbar(map_scroll_frame, orient="horizontal", command=self.mapping_tree.xview)
        self.mapping_tree.configure(yscrollcommand=mapping_scrollbar_v.set, xscrollcommand=mapping_scrollbar_h.set)
        
        self.mapping_tree.pack(side="left", fill="both", expand=True)
        mapping_scrollbar_v.pack(side="right", fill="y")
        mapping_scrollbar_h.pack(side="bottom", fill="x") # Pack below treeview and y-scrollbar

        ttk.Label(mapping_frame, textvariable=self.smart_organize_completion_var, font=("Segoe UI", 10, "bold")).pack(side="bottom", fill="x", pady=(5,0), anchor="sw")
        ttk.Progressbar(mapping_frame, variable=self.smart_organize_progress, mode='determinate', length=200).pack(side="bottom", fill="x", pady=(2,0), anchor="sw")

        self.create_common_directory_selection_frame(main_organize_pane, "Base Directory for Organizing/Packaging")
        action_frame = ttk.Frame(main_organize_pane)
        action_frame.pack(fill="x", pady=(5,0))
        ttk.Button(action_frame, text="Organize Assigned Files (Move/Copy)", command=self.organize_matched_files_threaded, style="Accent.TButton").pack(side="left", padx=(0,5))
        ttk.Button(action_frame, text="Download Package as Zip", command=self.download_package_as_zip_threaded).pack(side="left", padx=(0,5))

    def create_templates_tab(self, notebook):
        tab = ttk.Frame(notebook); notebook.add(tab, text="Manage Templates")
        main_frame = ttk.Frame(tab); main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        list_frame = ttk.LabelFrame(main_frame, text="Available Structure Templates", padding=10)
        list_frame.pack(fill="both", expand=True, pady=(0,10))
        
        self.templates_tree = ttk.Treeview(list_frame, columns=("Name", "Description", "Created"), show="headings")
        self.templates_tree.heading("Name", text="Template Name"); self.templates_tree.column("Name", width=200, anchor="w")
        self.templates_tree.heading("Description", text="Description"); self.templates_tree.column("Description", width=300, anchor="w")
        self.templates_tree.heading("Created", text="Created Date"); self.templates_tree.column("Created", width=150, anchor="w")
        templates_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.templates_tree.yview)
        self.templates_tree.configure(yscrollcommand=templates_scrollbar.set)
        self.templates_tree.pack(side="left", fill="both", expand=True); templates_scrollbar.pack(side="right", fill="y")
        
        template_actions = ttk.Frame(main_frame); template_actions.pack(fill="x")
        ttk.Button(template_actions, text="Load to Tab 1", command=self.load_selected_template_to_tab1).pack(side="left", padx=(0,5))
        ttk.Button(template_actions, text="Save Tab 1 Structure as Template", command=self.save_tab1_structure_as_template).pack(side="left", padx=(0,5))
        ttk.Button(template_actions, text="Delete Selected", command=self.delete_selected_template).pack(side="left", padx=(0,5))
        ttk.Button(template_actions, text="Refresh List", command=self.refresh_templates_list).pack(side="left", padx=(0,5))

    def create_common_directory_selection_frame(self, parent, label_text="Target Directory"):
        dir_frame = ttk.LabelFrame(parent, text=label_text, padding=10)
        dir_frame.pack(fill="x", pady=(5, 5))
        dir_entry_frame = ttk.Frame(dir_frame); dir_entry_frame.pack(fill="x")
        entry = ttk.Entry(dir_entry_frame, textvariable=self.base_dir_var, state="readonly")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(dir_entry_frame, text="Browse...", command=self.select_base_dir).pack(side="right")
        return dir_frame

    def _parse_structure_definition(self, structure_definition: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        items, errors, current_path_stack = [], [], []
        lines = [line.rstrip() for line in structure_definition.splitlines() if line.strip()]
        indent_char, indent_size, first_indented_line_found = ' ', 4, False

        for i, line_text in enumerate(lines):
            original_line_text = line_text
            line_text = line_text.split('#')[0].rstrip()
            if not line_text: continue

            leading_whitespace_str = line_text[:len(line_text) - len(line_text.lstrip())]
            name_part = line_text.lstrip()
            depth = 0
            
            is_tree_format = '├──' in name_part or '└──' in name_part
            base_depth_from_indent = 0

            if not first_indented_line_found and len(leading_whitespace_str) > 0:
                if leading_whitespace_str[0] == '\t': indent_char, indent_size = '\t', 1
                else: indent_char, indent_size = ' ', len(leading_whitespace_str) if len(leading_whitespace_str) > 0 else 4
                first_indented_line_found = True

            if indent_char == '\t': base_depth_from_indent = len(leading_whitespace_str)
            else: base_depth_from_indent = len(leading_whitespace_str) // indent_size if indent_size > 0 else 0
            depth = base_depth_from_indent

            if is_tree_format:
                tree_prefix_part = name_part.split('──')[0]
                # Count vertical bars, then add 1 if a connector is present (├ or └)
                # This is a more robust way to count tree depth levels.
                relative_tree_depth = tree_prefix_part.count('│') 
                if '├' in tree_prefix_part or '└' in tree_prefix_part:
                    relative_tree_depth += 1
                depth = base_depth_from_indent + relative_tree_depth
                name_part = name_part.split('──')[-1].strip()
            
            if not name_part: errors.append(f"L{i+1}: Empty name in: '{original_line_text}'"); continue
            if any(c in name_part for c in '<>:"|?*\\/.' if c == '.' and (name_part == "." or name_part == "..")): # More specific dot check
                if name_part == "." or name_part == "..":
                    errors.append(f"L{i+1}: Name '.' or '..' not allowed: '{name_part}' in '{original_line_text}'")
                else: # Handle other invalid chars
                    errors.append(f"L{i+1}: Invalid chars in name '{name_part}' in '{original_line_text}'")
                continue
            elif any(c in name_part for c in '<>:"|?*\\'):
                errors.append(f"L{i+1}: Invalid chars in name '{name_part}' in '{original_line_text}'")
                continue


            item_type = "directory" if name_part.endswith('/') else "file"
            name_clean = name_part.rstrip('/')
            if not name_clean: errors.append(f"L{i+1}: Resulting name is empty after stripping '/': '{original_line_text}'"); continue

            current_path_stack = current_path_stack[:depth]
            current_path_stack.append(name_clean)
            items.append({"relative_path": Path(*current_path_stack), "type": item_type, "name": name_clean, "depth": depth})
        return items, errors

    def create_structure_threaded(self):
        if not self._start_operation("Create Structure"): return
        threading.Thread(target=self._create_structure_worker, daemon=True).start()

    def _create_structure_worker(self):
        structure_definition = self.structure_text.get(1.0, "end").strip()
        base_dir_str = self.base_dir_var.get()
        if not base_dir_str: 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Error", "Select base directory.", parent=self.root)
            self._finish_operation(error_msg="Base directory not selected."); return
        base_dir = Path(base_dir_str)
        if not (base_dir.exists() and base_dir.is_dir()): 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Error", "Base directory invalid.", parent=self.root)
            self._finish_operation(error_msg="Invalid base directory."); return
        if not os.access(base_dir, os.W_OK): 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Error", "No write permission for base directory.", parent=self.root)
            self._finish_operation(error_msg="No write permission."); return
        if not structure_definition: 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Error", "Enter structure definition.", parent=self.root)
            self._finish_operation(error_msg="Structure definition empty."); return

        parsed_items, errors = self._parse_structure_definition(structure_definition)
        if errors:
            error_message_content = "\n".join(errors) 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Structure Error", f"Invalid definition:\n{error_message_content}", parent=self.root)
            self._finish_operation(error_msg="Invalid structure definition.")
            return

        actions_log, created_count, total_items = [], 0, len(parsed_items)
        try:
            for i, item in enumerate(parsed_items):
                if self.cancel_operation: break
                self.update_status(f"Creating item {i+1}/{total_items}: {item['relative_path']}", (i / total_items) * 100)
                full_path = base_dir / item["relative_path"]
                try:
                    if item["type"] == "directory": full_path.mkdir(parents=True, exist_ok=True); log_type = "create_dir"
                    else: full_path.parent.mkdir(parents=True, exist_ok=True); full_path.touch(exist_ok=True); log_type = "create_file"
                    self.log_operation(f"Created {item['type']}: {full_path}")
                    actions_log.append({"type": log_type, "path": str(full_path)})
                    created_count += 1
                except Exception as e: self.log_operation(f"Error creating {full_path}: {e}", "error")
            
            if actions_log and not self.cancel_operation:
                self.history.append({"timestamp": datetime.now().isoformat(), "operation": "create_structure", "actions": actions_log, "base_directory": str(base_dir)})
                self.save_json(self.history_file, self.history)
            
            msg = f"Structure created: {created_count}/{total_items} items in '{base_dir_str}'."
            self._finish_operation(success_msg=msg)
            if created_count > 0 and not self.cancel_operation and hasattr(self, 'root') and self.root.winfo_exists():
                 messagebox.showinfo("Success", msg, parent=self.root)
        except Exception as e:
            self.logger.error(f"Error in create_structure_worker: {e}", exc_info=True)
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Creation Error", f"An unexpected error: {e}", parent=self.root)
            self._finish_operation(error_msg="Structure creation failed.")

    def preview_structure(self):
        structure_definition = self.structure_text.get(1.0, "end").strip()
        base_dir_str = self.base_dir_var.get()
        if not base_dir_str: messagebox.showwarning("Preview", "Select base directory.", parent=self.root); return
        if not structure_definition: messagebox.showwarning("Preview", "Structure definition empty.", parent=self.root); return

        parsed_items, errors = self._parse_structure_definition(structure_definition)
        preview_content = f"Base Directory: {base_dir_str}\n\n--- Structure Preview ---\n"
        if errors:
            error_list_str = "\n".join(errors) 
            preview_content += f"Definition Errors:\n{error_list_str}\n\n---\n"
        if not parsed_items and not errors: preview_content += "(No valid items to preview)"
        for item in parsed_items: preview_content += f"{'    ' * item['depth']}{item['name']}{'/' if item['type'] == 'directory' else ''}\n"
        ShowTextDialog(self.root, "Structure Preview", preview_content, geometry="700x500")

    def load_sample_structure(self):
        sample = "my_project/\n    src/\n        main.py\n        utils/\n            __init__.py\n            helpers.py\n    tests/\n        test_main.py\n    docs/\n        README.md\n    requirements.txt\n.gitignore"
        self.structure_text.delete(1.0, "end"); self.structure_text.insert("1.0", sample)

    def clear_structure_definition(self):
        if messagebox.askyesno("Confirm", "Clear structure definition in Tab 1?", parent=self.root): self.structure_text.delete(1.0, "end")

    def select_files_for_move(self):
        files = filedialog.askopenfilenames(title="Select Files to Move", parent=self.root)
        if files:
            for f_str in files:
                f_path = Path(f_str)
                self.files_tree.insert("", "end", values=(str(f_path), self.get_file_size_str(f_path), f_path.suffix.lower() or "File"))

    def select_folder_for_move(self):
        folder = filedialog.askdirectory(title="Select Folder of Files to Move", parent=self.root)
        if folder:
            try:
                for item in Path(folder).rglob('*'): # Consider adding a progress update for large folders
                    if item.is_file(): self.files_tree.insert("", "end", values=(str(item), self.get_file_size_str(item), item.suffix.lower() or "File"))
            except Exception as e: messagebox.showerror("Error", f"Failed to load files from folder: {e}", parent=self.root); self.logger.error(f"Error loading folder for move: {e}")

    def clear_move_files_list(self): self.files_tree.delete(*self.files_tree.get_children())

    def move_files_threaded(self):
        if not self._start_operation("Move Files"): return
        threading.Thread(target=self._move_files_worker, daemon=True).start()

    def _move_files_worker(self):
        base_dir_str = self.base_dir_var.get()
        if not base_dir_str: 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Error", "Select target directory.", parent=self.root)
            self._finish_operation(error_msg="Target directory not selected."); return
        target_dir = Path(base_dir_str)
        if not target_dir.is_dir(): 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Error", "Target directory invalid.", parent=self.root)
            self._finish_operation(error_msg="Invalid target directory."); return

        item_ids = self.files_tree.get_children()
        if not item_ids: 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Error", "No files selected to move.", parent=self.root)
            self._finish_operation(error_msg="No files to move."); return

        actions_log, moved_count, total_files = [], 0, len(item_ids)
        try:
            for i, item_id in enumerate(item_ids):
                if self.cancel_operation: break
                source_path = Path(self.files_tree.item(item_id)['values'][0])
                self.update_status(f"Moving {i+1}/{total_files}: {source_path.name}", (i / total_files) * 100)
                if not source_path.exists(): self.log_operation(f"Skipping {source_path}, non-existent.", "warning"); continue
                
                dest_path, counter = target_dir / source_path.name, 1
                original_stem = dest_path.stem
                original_suffix = dest_path.suffix
                while dest_path.exists(): 
                    dest_path = target_dir / f"{original_stem}_{counter}{original_suffix}"
                    counter += 1
                try:
                    shutil.move(str(source_path), str(dest_path))
                    actions_log.append({"type": "move", "source": str(source_path), "target": str(dest_path)})
                    moved_count += 1; self.log_operation(f"Moved {source_path} to {dest_path}")
                except Exception as e: self.log_operation(f"Error moving {source_path}: {e}", "error")
            
            if actions_log and not self.cancel_operation:
                self.history.append({"timestamp": datetime.now().isoformat(), "operation": "move_files", "actions": actions_log, "base_directory": str(target_dir)})
                self.save_json(self.history_file, self.history)
            msg = f"Moved {moved_count}/{total_files} files to '{target_dir}'."
            self._finish_operation(success_msg=msg)
            if moved_count > 0 and not self.cancel_operation and hasattr(self, 'root') and self.root.winfo_exists():
                 messagebox.showinfo("Success", msg, parent=self.root)
            self.clear_move_files_list()
        except Exception as e:
            self.logger.error(f"Error in move_files_worker: {e}", exc_info=True)
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Move Error", f"Unexpected error: {e}", parent=self.root)
            self._finish_operation(error_msg="File moving failed.")

    def copy_structure_to_smart_organize(self):
        self.smart_organize_structure_text.delete(1.0, "end")
        self.smart_organize_structure_text.insert("1.0", self.structure_text.get(1.0, "end"))
        self.update_status("Structure definition copied. Click 'Build/Rebuild Skeleton Tree'.")

    def load_sample_for_smart_organize(self):
        sample = "project_beta/\n  src/\n    app.py\n    utils.py\n  data/\n    input.csv\n    output/\n  tests/\n    test_app.py\n  docs/\n    manual.pdf\n  config.json\n  README.md"
        self.smart_organize_structure_text.delete(1.0, "end"); self.smart_organize_structure_text.insert("1.0", sample)
        self.update_status("Sample structure loaded. Click 'Build/Rebuild Skeleton Tree'.")

    def build_smart_organize_skeleton_threaded(self):
        if not self._start_operation("Build Skeleton"): return
        threading.Thread(target=self._build_smart_organize_skeleton_worker, daemon=True).start()

    def _build_smart_organize_skeleton_worker(self):
        structure_def = self.smart_organize_structure_text.get(1.0, "end").strip()
        if not structure_def: 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Error", "Structure definition empty.", parent=self.root)
            self._finish_operation(error_msg="Structure definition empty."); return

        parsed_items, errors = self._parse_structure_definition(structure_def)
        if errors:
            error_list_str = "\n".join(errors) 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Structure Error", f"Invalid definition:\n{error_list_str}", parent=self.root)
            self._finish_operation(error_msg="Invalid structure definition.")
            return
        
        self.smart_organize_skeleton.clear(); self.mapping_tree.delete(*self.mapping_tree.get_children())
        for i, item in enumerate(parsed_items):
            if self.cancel_operation: break
            self.update_status(f"Building skeleton item {i+1}/{len(parsed_items)}", (i / len(parsed_items)) * 100)
            rel_path_str = str(item["relative_path"])
            self.smart_organize_skeleton.append({"target_path_relative": rel_path_str, "type": item["type"], "name": item["name"], "source_file_actual": None, "status": STATUS_MISSING, "confidence": 0})
            self.mapping_tree.insert("", "end", iid=rel_path_str, values=(rel_path_str, item["type"], "", STATUS_MISSING))
        
        self._update_smart_organize_completion()
        self._finish_operation(success_msg=f"Skeleton built with {len(self.smart_organize_skeleton)} items.")

    def add_files_to_stage(self):
        files = filedialog.askopenfilenames(title="Select Files to Stage", parent=self.root)
        if files:
            added_count = 0
            for f_str in files:
                f_path = Path(f_str)
                if not any(staged_f == f_path for staged_f in self.staged_files):
                    self.staged_files.append(f_path)
                    parent_context = f_path.parent.name
                    if f_path.parent.parent != f_path.parent: 
                        parent_context = f"{f_path.parent.parent.name}/{f_path.parent.name}"
                    self.staged_files_listbox.insert(tk.END, f"{f_path.name}  ({parent_context})")
                    added_count += 1
            if added_count > 0: self.update_status(f"{added_count} file(s) added to stage. Total: {len(self.staged_files)}.")

    def add_folder_to_stage(self):
        folder = filedialog.askdirectory(title="Select Folder to Stage Files From", parent=self.root)
        if folder:
            folder_path = Path(folder)
            recursive = messagebox.askyesno("Recursive Scan", "Scan subfolders recursively?", parent=self.root)
            glob_pattern = '**/*' if recursive else '*'
            added_count = 0
            try:
                self.update_status("Scanning folder for staging...", -1)
                all_files_in_folder = list(folder_path.glob(glob_pattern)) # Get all first to show progress
                total_files_to_scan = len(all_files_in_folder)
                for i, item in enumerate(all_files_in_folder):
                    if self.cancel_operation: break
                    self.update_status(f"Scanning folder {i+1}/{total_files_to_scan}", (i/total_files_to_scan)*100 if total_files_to_scan > 0 else 0)
                    if item.is_file():
                        if not any(staged_f == item for staged_f in self.staged_files):
                            self.staged_files.append(item)
                            parent_context = item.parent.name
                            if item.parent.parent != item.parent: parent_context = f"{item.parent.parent.name}/{item.parent.name}"
                            self.staged_files_listbox.insert(tk.END, f"{item.name}  ({parent_context})")
                            added_count += 1
                if self.cancel_operation:
                     self._finish_operation() # Handles cancel message
                     return
                self.update_status(f"{added_count} file(s) from folder added to stage. Total: {len(self.staged_files)}.")
            except Exception as e: 
                if hasattr(self, 'root') and self.root.winfo_exists():
                    messagebox.showerror("Error", f"Error staging folder: {e}", parent=self.root)
                self.logger.error(f"Error staging folder: {e}"); self.update_status("Error staging.",0)

    def clear_stage(self):
        if messagebox.askyesno("Confirm", "Clear all files from staging area?", parent=self.root):
            self.staged_files.clear(); self.staged_files_listbox.delete(0, tk.END)
            self.update_status("Staging area cleared.")

    def assign_staged_to_target(self):
        selected_staged_indices = self.staged_files_listbox.curselection()
        selected_target_iids = self.mapping_tree.selection()

        if not selected_staged_indices: messagebox.showwarning("Assign Error", "Select file(s) from Staging Area.", parent=self.root); return
        if not selected_target_iids: messagebox.showwarning("Assign Error", "Select target item(s) in Skeleton Tree.", parent=self.root); return
        
        staged_files_to_assign = [self.staged_files[i] for i in selected_staged_indices]
        assigned_from_this_action = [] 

        if len(staged_files_to_assign) == 1:
            staged_file = staged_files_to_assign[0]
            for target_iid in selected_target_iids:
                if not messagebox.askyesno("Confirm Assignment", f"Assign '{staged_file.name}' to target '{target_iid}'?", parent=self.root): continue
                if self._perform_assignment(staged_file, target_iid):
                    assigned_from_this_action.append(staged_file) 
        elif len(staged_files_to_assign) > 1 and len(staged_files_to_assign) == len(selected_target_iids):
            # Confirm batch assignment
            if not messagebox.askyesno("Confirm Batch Assignment", f"Assign {len(staged_files_to_assign)} staged files to {len(selected_target_iids)} selected targets in order?", parent=self.root):
                return
            for i, staged_file in enumerate(staged_files_to_assign):
                if self._perform_assignment(staged_file, selected_target_iids[i]):
                    assigned_from_this_action.append(staged_file)
        else:
            messagebox.showwarning("Assign Error", "Unsupported selection. Select one staged file for one/multiple targets, OR an equal number of staged files and targets for 1-to-1 assignment.", parent=self.root)
            return
        
        if assigned_from_this_action:
            for f_assigned in set(assigned_from_this_action): 
                if f_assigned in self.staged_files: self.staged_files.remove(f_assigned)
            self._refresh_staged_files_listbox()
    
    def _perform_assignment(self, source_file_path: Path, target_iid: str) -> bool:
        skeleton_item = next((si for si in self.smart_organize_skeleton if si["target_path_relative"] == target_iid), None)
        if not skeleton_item: self.logger.error(f"Assign: Skeleton item for IID {target_iid} not found"); return False
        if skeleton_item["type"] == "directory": messagebox.showinfo("Assign Info", f"Cannot assign to directory target '{target_iid}'.", parent=self.root); return False

        if skeleton_item["status"] != STATUS_MISSING and skeleton_item["source_file_actual"]:
            current_source = Path(skeleton_item["source_file_actual"]).name
            if not messagebox.askyesno("Replace Assignment?", f"Target '{target_iid}' is assigned to '{current_source}'.\nReplace with '{source_file_path.name}'?", parent=self.root):
                return False

        skeleton_item["source_file_actual"] = str(source_file_path)
        skeleton_item["status"], skeleton_item["confidence"] = STATUS_ASSIGNED, 100
        self.mapping_tree.item(target_iid, values=(skeleton_item["target_path_relative"], skeleton_item["type"], str(source_file_path), f"{STATUS_ASSIGNED}"))
        self._update_smart_organize_completion()
        self.update_status(f"Assigned '{source_file_path.name}' to '{target_iid}'.", 0)
        return True
    
    def _refresh_staged_files_listbox(self):
        self.staged_files_listbox.delete(0, tk.END)
        for f_path in self.staged_files:
            parent_context = f_path.parent.name
            if f_path.parent.parent != f_path.parent: parent_context = f"{f_path.parent.parent.name}/{f_path.parent.name}"
            self.staged_files_listbox.insert(tk.END, f"{f_path.name}  ({parent_context})")

    def auto_assign_from_stage_threaded(self):
        if not self.smart_organize_skeleton: messagebox.showwarning("Auto-Assign", "Build skeleton first.", parent=self.root); return
        if not self.staged_files: messagebox.showwarning("Auto-Assign", "No files in staging area.", parent=self.root); return
        if not self._start_operation("Auto-Assigning from Stage"): return
        threading.Thread(target=self._auto_assign_from_stage_worker, daemon=True).start()

    def _auto_assign_from_stage_worker(self):
        assigned_count = 0
        available_staged_files = list(self.staged_files) 
        successfully_assigned_this_run = []

        total_skeleton_items = len(self.smart_organize_skeleton)
        for i, skeleton_item in enumerate(self.smart_organize_skeleton):
            if self.cancel_operation: break
            self.update_status(f"Auto-Assigning item {i+1}/{total_skeleton_items}", (i / total_skeleton_items) * 100)

            if skeleton_item["type"] == "directory" or skeleton_item["status"] != STATUS_MISSING: continue

            target_name = skeleton_item["name"]
            best_staged_file, best_score, best_staged_idx = None, 0, -1
            for idx, staged_file in enumerate(available_staged_files):
                score = fuzz.ratio(target_name.lower(), staged_file.name.lower())
                if Path(target_name).suffix.lower() == staged_file.suffix.lower() and Path(target_name).suffix: score += 15 # Bonus for same extension
                if score > best_score: best_score, best_staged_file, best_staged_idx = score, staged_file, idx
            
            if best_staged_file and best_score >= 75: # Threshold for auto-assignment
                skeleton_item["source_file_actual"], skeleton_item["status"], skeleton_item["confidence"] = str(best_staged_file), STATUS_ASSIGNED, best_score
                self.mapping_tree.item(skeleton_item["target_path_relative"], values=(skeleton_item["target_path_relative"], skeleton_item["type"], str(best_staged_file), f"{STATUS_ASSIGNED} ({best_score}%)"))
                assigned_count += 1
                successfully_assigned_this_run.append(best_staged_file)
                available_staged_files.pop(best_staged_idx) # Remove from consideration for this run
        
        if self.cancel_operation:
            self._finish_operation()
            return

        for f_assigned in successfully_assigned_this_run:
            if f_assigned in self.staged_files: self.staged_files.remove(f_assigned)
        self._refresh_staged_files_listbox()

        self._update_smart_organize_completion()
        self._finish_operation(success_msg=f"Auto-assign from stage: {assigned_count} items assigned.")

    def load_source_files_for_pool(self):
        choice = simpledialog.askstring("Load Source Pool", "Load 'files' or 'folder' into pool?", parent=self.root)
        if not choice: return
        new_files_for_pool: List[Path] = []
        if choice.lower() == 'files':
            selected_files = filedialog.askopenfilenames(title="Select Files for Pool", parent=self.root)
            if selected_files: new_files_for_pool = [Path(f) for f in selected_files]
        elif choice.lower() == 'folder':
            folder = filedialog.askdirectory(title="Select Folder for Pool", parent=self.root)
            if folder:
                folder_path, recursive = Path(folder), messagebox.askyesno("Recursive Scan", "Scan subfolders recursively?", parent=self.root)
                try:
                    self.update_status("Scanning for pool...", -1)
                    all_items = list(folder_path.glob('**/*' if recursive else '*'))
                    total_items_to_scan = len(all_items)
                    for i, item in enumerate(all_items):
                        if self.cancel_operation: break
                        self.update_status(f"Scanning pool {i+1}/{total_items_to_scan}", (i/total_items_to_scan)*100 if total_items_to_scan > 0 else 0)
                        if item.is_file(): new_files_for_pool.append(item)
                    
                    if self.cancel_operation:
                        self._finish_operation()
                        return
                    self.update_status(f"Found {len(new_files_for_pool)} files for pool.", 0)
                except Exception as e: 
                    if hasattr(self, 'root') and self.root.winfo_exists():
                        messagebox.showerror("Error", f"Error scanning: {e}", parent=self.root)
                    self.logger.error(f"Pool scan error: {e}"); self.update_status("Error.",0); return
        else: messagebox.showwarning("Invalid Choice", "Type 'files' or 'folder'.", parent=self.root); return

        added_count = 0
        for f_path in new_files_for_pool:
            if f_path not in self.source_files_pool:
                self.source_files_pool.append(f_path)
                added_count +=1
        
        self.source_pool_count_var.set(f"Pool: {len(self.source_files_pool)} files")
        if added_count > 0: self.update_status(f"Added {added_count} new files to pool. Total: {len(self.source_files_pool)}.")
        else: self.update_status(f"No new files added to pool. Total: {len(self.source_files_pool)}.")


    def clear_source_pool(self):
        if messagebox.askyesno("Confirm", "Clear general source pool?", parent=self.root):
            self.source_files_pool.clear(); self.source_pool_count_var.set("Pool: 0 files")
            self.update_status("General source pool cleared.")

    def auto_match_from_pool_threaded(self):
        if not self.smart_organize_skeleton: messagebox.showwarning("Auto-Match", "Build skeleton first.", parent=self.root); return
        if not self.source_files_pool: messagebox.showwarning("Auto-Match", "Source pool empty.", parent=self.root); return
        if not self._start_operation("Auto-Matching from Pool"): return
        threading.Thread(target=self._auto_match_from_pool_worker, daemon=True).start()

    def _auto_match_from_pool_worker(self):
        matched_count = 0
        # Create a copy of the pool that can be modified (files removed as they are matched)
        # to prevent a single pool file from matching multiple targets if that's not desired.
        # If a pool file CAN match multiple targets, then iterate over self.source_files_pool directly.
        available_pool_files = list(self.source_files_pool) 
        
        for i, skeleton_item in enumerate(self.smart_organize_skeleton):
            if self.cancel_operation: break
            self.update_status(f"Matching Pool item {i+1}/{len(self.smart_organize_skeleton)}", (i / len(self.smart_organize_skeleton)) * 100)
            if skeleton_item["type"] == "directory" or skeleton_item["status"] != STATUS_MISSING: continue

            target_name = skeleton_item["name"]
            best_pool_file, best_score, best_pool_idx = None, 0, -1
            for idx, pool_file in enumerate(available_pool_files): # Iterate over the copy
                score = fuzz.ratio(target_name.lower(), pool_file.name.lower())
                if Path(target_name).suffix.lower() == pool_file.suffix.lower() and Path(target_name).suffix: score += 15
                if score > best_score: best_score, best_pool_file, best_pool_idx = score, pool_file, idx
            
            if best_pool_file and best_score >= 70: # Threshold for pool matching
                skeleton_item["source_file_actual"], skeleton_item["status"], skeleton_item["confidence"] = str(best_pool_file), STATUS_MATCHED, best_score
                self.mapping_tree.item(skeleton_item["target_path_relative"], values=(skeleton_item["target_path_relative"], skeleton_item["type"], str(best_pool_file), f"{STATUS_MATCHED} ({best_score}%)"))
                matched_count += 1
                available_pool_files.pop(best_pool_idx) # Consume from temp list to prevent re-matching
        
        if self.cancel_operation:
            self._finish_operation()
            return

        self._update_smart_organize_completion()
        self._finish_operation(success_msg=f"Auto-match from pool: {matched_count} items matched.")

    def clear_all_smart_organize_matches(self):
        if not self.smart_organize_skeleton: return
        if not messagebox.askyesno("Confirm", "Clear all assignments in Skeleton Tree?", parent=self.root): return
        for item in self.smart_organize_skeleton:
            if item["type"] == "file": # Only clear for files, directories don't have assignments
                item["source_file_actual"], item["status"], item["confidence"] = None, STATUS_MISSING, 0
                try: 
                    if self.mapping_tree.exists(item["target_path_relative"]): # Check if item exists in tree
                        self.mapping_tree.item(item["target_path_relative"], values=(item["target_path_relative"], item["type"], "", STATUS_MISSING))
                except tk.TclError: 
                    self.logger.warning(f"TclError clearing item {item['target_path_relative']} in tree, might have been removed.")
                    pass # Item might not be in tree if skeleton was rebuilt
        self._update_smart_organize_completion(); self.update_status("All tree assignments cleared.")
        
    def show_mapping_tree_menu(self, event):
        iid = self.mapping_tree.identify_row(event.y)
        if iid: 
            self.mapping_tree.selection_set(iid) # Ensure the clicked item is selected
            self.mapping_tree_menu.post(event.x_root, event.y_root)

    def manually_assign_source_file_for_selected(self):
        selected_iids = self.mapping_tree.selection()
        if not selected_iids: messagebox.showwarning("Manual Assign", "Select target item(s) from the Skeleton Tree.", parent=self.root); return
        
        target_iid = selected_iids[0] # Process first selected for simplicity if multiple are somehow selected for browse
        if len(selected_iids) > 1: 
            messagebox.showinfo("Manual Assign", "Multiple targets selected. Processing the first one for file browse: " + target_iid, parent=self.root)

        # Check if the target is a directory
        skeleton_item = next((si for si in self.smart_organize_skeleton if si["target_path_relative"] == target_iid), None)
        if skeleton_item and skeleton_item["type"] == "directory":
            messagebox.showinfo("Manual Assign", f"Target '{target_iid}' is a directory. Cannot assign a source file to a directory.", parent=self.root)
            return

        source_file_path_str = filedialog.askopenfilename(title=f"Browse Source File for: {target_iid}", parent=self.root)
        if source_file_path_str: self._perform_assignment(Path(source_file_path_str), target_iid)

    def clear_assignment_for_selected(self):
        selected_iids = self.mapping_tree.selection()
        if not selected_iids: messagebox.showwarning("Clear Assignment", "Select target item(s) from the Skeleton Tree to clear.", parent=self.root); return
        cleared_count = 0
        for target_iid in selected_iids:
            item = next((si for si in self.smart_organize_skeleton if si["target_path_relative"] == target_iid), None)
            if item and item["type"] == "file": # Only clear for files
                item["source_file_actual"], item["status"], item["confidence"] = None, STATUS_MISSING, 0
                if self.mapping_tree.exists(target_iid):
                    self.mapping_tree.item(target_iid, values=(target_iid, item["type"], "", STATUS_MISSING))
                cleared_count +=1
        if cleared_count > 0: self._update_smart_organize_completion(); self.update_status(f"Cleared assignments for {cleared_count} target(s).")

    def _update_smart_organize_completion(self):
        if not self.smart_organize_skeleton: 
            self.smart_organize_completion_var.set("Completion: N/A")
            self.smart_organize_progress.set(0.0) 
            return
        total_f = sum(1 for item in self.smart_organize_skeleton if item["type"] == "file")
        matched_f = sum(1 for item in self.smart_organize_skeleton if item["type"] == "file" and item["status"] != STATUS_MISSING and item["source_file_actual"] is not None)
        perc = (matched_f / total_f) * 100 if total_f > 0 else 0.0
        self.smart_organize_completion_var.set(f"Completion: {perc:.2f}% ({matched_f}/{total_f} files)")
        self.smart_organize_progress.set(perc) 


    def organize_matched_files_threaded(self):
        base_dir_str = self.base_dir_var.get()
        if not base_dir_str: messagebox.showerror("Error", "Select Base Directory for organizing.", parent=self.root); return
        if not self.smart_organize_skeleton: messagebox.showerror("Error", "No target skeleton built.", parent=self.root); return
        if not any(i["status"]!=STATUS_MISSING and i["source_file_actual"] for i in self.smart_organize_skeleton if i["type"] == "file"): 
            messagebox.showinfo("Organize", "No files assigned to organize.", parent=self.root); return
        
        op = simpledialog.askstring("Operation Type", "Enter 'copy' or 'move' files:", parent=self.root, initialvalue="copy")
        if not op or op.lower() not in ['copy', 'move']: 
            messagebox.showwarning("Invalid Operation", "Operation must be 'copy' or 'move'.", parent=self.root); return
        
        if not self._start_operation(f"Organize Files ({op.lower()})"): return
        threading.Thread(target=self._organize_matched_files_worker, args=(Path(base_dir_str), op.lower()), daemon=True).start()

    def _organize_matched_files_worker(self, base_dir: Path, operation_type: str):
        actions, processed_count = [], 0
        # Filter for items that are files and have a source assigned
        items_to_process = [i for i in self.smart_organize_skeleton if i["type"] == "file" and i["status"]!=STATUS_MISSING and i["source_file_actual"]]
        
        if not items_to_process: 
            self._finish_operation(success_msg="No assigned files to organize."); return
        
        try:
            for i_idx, item in enumerate(items_to_process):
                if self.cancel_operation: break
                src_f_path, tgt_rel_path_str = Path(item["source_file_actual"]), item["target_path_relative"]
                # target_path_relative should already be a string from skeleton build, but ensure Path for joining
                dst_full_path = base_dir / Path(tgt_rel_path_str) 
                
                self.update_status(f"{operation_type.capitalize()}ing {i_idx+1}/{len(items_to_process)}: {src_f_path.name}", (i_idx/len(items_to_process))*100)
                
                if not src_f_path.exists() or not src_f_path.is_file(): 
                    self.log_operation(f"Source file {src_f_path} not found or is not a file, skipping.", "warning"); continue
                
                try:
                    dst_full_path.parent.mkdir(parents=True, exist_ok=True) # Ensure target directory exists
                    
                    if dst_full_path.exists():
                        if not messagebox.askyesno("File Conflict", f"Destination file '{dst_full_path}' already exists.\nOverwrite?", parent=self.root): 
                            self.log_operation(f"Skipped overwrite for {dst_full_path}", "info"); continue
                    
                    action_verb = "Copied" if operation_type == "copy" else "Moved"
                    if operation_type == "copy": 
                        shutil.copy2(str(src_f_path), str(dst_full_path))
                    else: # move
                        shutil.move(str(src_f_path), str(dst_full_path))
                        # Update status in skeleton and tree if moved
                        item["status"]=f"Organized ({action_verb})" 
                        if self.mapping_tree.exists(item["target_path_relative"]):
                            self.mapping_tree.item(item["target_path_relative"],values=(item["target_path_relative"],item["type"],item["source_file_actual"],item["status"]))
                    
                    actions.append({"type":operation_type,"source":str(src_f_path),"target":str(dst_full_path)})
                    processed_count+=1
                    self.log_operation(f"{action_verb} {src_f_path} to {dst_full_path}")
                
                except Exception as e_file_op: 
                    self.log_operation(f"Error {operation_type}ing file {src_f_path} to {dst_full_path}: {e_file_op}", "error")
            
            if self.cancel_operation:
                self._finish_operation() # Handles cancel message
                return

            if actions: # Log only if actions were performed
                self.history.append({"timestamp":datetime.now().isoformat(),"operation":f"smart_organize_{operation_type}","actions":actions,"base_directory":str(base_dir)})
                self.save_json(self.history_file,self.history)
            
            msg = f"{operation_type.capitalize()} {processed_count}/{len(items_to_process)} files to '{base_dir}'."
            self._finish_operation(success_msg=msg)
            if processed_count > 0 and not self.cancel_operation and hasattr(self, 'root') and self.root.winfo_exists():
                 messagebox.showinfo("Success", msg, parent=self.root)
            self._update_smart_organize_completion() # Update completion % if files were moved (status changed)

        except Exception as e_worker: 
            self.logger.error(f"Organize worker main error: {e_worker}",exc_info=True)
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("Organize Error",f"An unexpected error occurred: {e_worker}",parent=self.root)
            self._finish_operation(error_msg="Organization process failed.")


    def download_package_as_zip_threaded(self):
        if not self.smart_organize_skeleton: messagebox.showerror("Error", "No target skeleton built.", parent=self.root); return
        if not any(i["type"] == "file" and i["status"]!=STATUS_MISSING and i["source_file_actual"] for i in self.smart_organize_skeleton): 
            messagebox.showinfo("Package", "No files assigned to package.", parent=self.root); return
        
        default_zip_name = f"package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path_str = filedialog.asksaveasfilename(defaultextension=".zip", initialfile=default_zip_name, filetypes=[("Zip files", "*.zip")], title="Save Package as ZIP", parent=self.root)
        if not zip_path_str: return # User cancelled save dialog
        
        if not self._start_operation("Create ZIP Package"): return
        threading.Thread(target=self._download_package_as_zip_worker, args=(Path(zip_path_str),), daemon=True).start()

    def _download_package_as_zip_worker(self, output_zip_path: Path):
        # Create a unique temporary directory for staging the package contents
        tmp_package_dir = self.data_dir / f"temp_pkg_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        try:
            tmp_package_dir.mkdir(parents=True, exist_ok=True)
            
            items_to_package = [i for i in self.smart_organize_skeleton if i["type"] == "file" and i["status"]!=STATUS_MISSING and i["source_file_actual"]]
            packed_files_count = 0
            
            # First, create all necessary directories within the temp package structure
            # This ensures that even if a directory is defined but has no files assigned to it, it still gets created in the zip.
            # This uses the *target* structure definition.
            # structure_def_text = self.smart_organize_structure_text.get(1.0,"end").strip()
            # parsed_structure_items, _ = self._parse_structure_definition(structure_def_text) # Assuming no errors here as skeleton was built
            # for struct_item in parsed_structure_items:
            #     if struct_item["type"] == "directory":
            #         (tmp_package_dir / struct_item["relative_path"]).mkdir(parents=True, exist_ok=True)

            # More direct way: iterate through skeleton items to create parent dirs for files
            # And also create any explicitly defined empty directories from the skeleton
            for skel_item in self.smart_organize_skeleton:
                target_relative_path = Path(skel_item["target_path_relative"])
                full_temp_target_path = tmp_package_dir / target_relative_path
                if skel_item["type"] == "directory":
                    full_temp_target_path.mkdir(parents=True, exist_ok=True)
                elif skel_item["type"] == "file" and skel_item["source_file_actual"]: # Ensure parent dir for files exists
                    full_temp_target_path.parent.mkdir(parents=True, exist_ok=True)


            # Copy assigned source files to their target locations within the temp directory
            for i_idx, item_data in enumerate(items_to_package):
                if self.cancel_operation: raise OperationCancelledError("Packaging cancelled by user during file copy.")
                
                source_file = Path(item_data["source_file_actual"])
                target_rel_path = Path(item_data["target_path_relative"]) # Already a string from skeleton
                destination_in_temp = tmp_package_dir / target_rel_path
                
                self.update_status(f"Preparing file {i_idx+1}/{len(items_to_package)}: {source_file.name}", (i_idx/len(items_to_package))*100)
                
                if not source_file.exists() or not source_file.is_file(): 
                    self.log_operation(f"Source file {source_file} for packaging not found or is not a file, skipping.","warning"); continue
                
                try:
                    # destination_in_temp.parent.mkdir(parents=True, exist_ok=True) # Ensure parent dir
                    shutil.copy2(str(source_file), str(destination_in_temp))
                    packed_files_count += 1
                except Exception as e_copy: 
                    self.log_operation(f"Error copying file {source_file} to temporary package location {destination_in_temp}: {e_copy}","error")
            
            if self.cancel_operation: raise OperationCancelledError("Packaging cancelled by user after file copy, before zipping.")

            self.update_status("Compressing package...",-1) # Indeterminate progress for zipping
            
            with zipfile.ZipFile(output_zip_path,'w',zipfile.ZIP_DEFLATED, compresslevel=6) as zf: # Added compresslevel
                # Walk through the temporary package directory and add files to zip
                # Correctly calculate total files for zipping progress if desired, or keep indeterminate
                files_to_zip = list(tmp_package_dir.rglob("*")) # Get all items for potential progress
                num_files_for_zip_progress = sum(1 for f in files_to_zip if f.is_file())
                zipped_count_progress = 0

                for item_path in tmp_package_dir.rglob("*"): # rglob to get all files and dirs
                    if self.cancel_operation: raise OperationCancelledError("Packaging cancelled by user during zipping.")
                    
                    # Arcname is the path inside the zip file
                    arcname = item_path.relative_to(tmp_package_dir)
                    if item_path.is_file():
                        zf.write(item_path, arcname)
                        zipped_count_progress += 1
                        if num_files_for_zip_progress > 0:
                             self.update_status(f"Zipping: {arcname}", (zipped_count_progress/num_files_for_zip_progress)*100)
                    elif item_path.is_dir():
                        # Add directory entry to zip if it's empty and wouldn't be created by a file path
                        # This is often handled implicitly if files are in the dir, but explicit for empty ones.
                        if not any(item_path.iterdir()): # If it's an empty directory
                             zf.write(item_path, arcname)


            success_msg = f"Package '{output_zip_path.name}' created successfully with {packed_files_count} file(s)."
            self._finish_operation(success_msg=success_msg) 
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showinfo("Success",success_msg,parent=self.root)

        except OperationCancelledError as oce: 
            self.logger.info(f"ZIP Package creation cancelled: {oce}")
            self._finish_operation() # Handles cancel message
        except Exception as e_zip: 
            self.logger.error(f"Error creating ZIP package: {e_zip}",exc_info=True)
            if hasattr(self, 'root') and self.root.winfo_exists():
                messagebox.showerror("ZIP Error",f"Failed to create package: {e_zip}",parent=self.root)
            self._finish_operation(error_msg="Package creation failed.")
        finally:
            if tmp_package_dir.exists():
                try:
                    shutil.rmtree(tmp_package_dir)
                    self.logger.info(f"Successfully cleaned up temporary package directory: {tmp_package_dir}")
                except Exception as e_cleanup:
                    self.logger.error(f"Error cleaning up temporary package directory {tmp_package_dir}: {e_cleanup}")


    def handle_os_drop_on_stage(self,event): 
        # This is a placeholder for TkinterDnD2, which is not fully integrated.
        self.logger.info(f"OS Drop on Stage (TkinterDnD2 - Conceptual): {event.data} - Not Implemented")
        messagebox.showinfo("Drag & Drop NI","OS Drag & Drop to Staging Area is not implemented with TkinterDnD2 in this version.",parent=self.root)
    
    def handle_os_drop_on_mapping_tree(self,event): 
        # This is a placeholder for TkinterDnD2.
        self.logger.info(f"OS Drop on Mapping Tree (TkinterDnD2 - Conceptual): {event.data} - Not Implemented")
        messagebox.showinfo("Drag & Drop NI","OS Drag & Drop to Mapping Tree is not implemented with TkinterDnD2 in this version.",parent=self.root)


    def load_selected_template_to_tab1(self):
        sel = self.templates_tree.selection()
        if not sel: messagebox.showwarning("Warning", "No template selected from the list.", parent=self.root); return
        template_name = self.templates_tree.item(sel[0])['values'][0]
        
        template_data = next((t for t in self.templates.get("templates", []) if t["name"] == template_name), None)
        
        if template_data and "structure" in template_data: 
            self.structure_text.delete(1.0,"end")
            self.structure_text.insert(1.0,template_data["structure"])
            self.notebook.select(0) # Switch to the first tab
            self.update_status(f"Template '{template_name}' loaded into Tab 1.")
        else: 
            messagebox.showerror("Error", f"Template '{template_name}' is invalid or structure is missing.", parent=self.root)
            self.logger.error(f"Failed to load template '{template_name}': Data or structure missing. Data: {template_data}")


    def save_tab1_structure_as_template(self):
        current_structure = self.structure_text.get(1.0,"end").strip()
        if not current_structure: 
            messagebox.showwarning("Empty Structure", "The structure definition in Tab 1 is empty. Nothing to save as template.", parent=self.root); return
        
        template_name = simpledialog.askstring("Save Template", "Enter a name for this template:", parent=self.root)
        if not template_name: return # User cancelled or entered empty name
        
        # Check for existing template with the same name
        existing_template = next((t for t in self.templates.get("templates", []) if t["name"] == template_name), None)
        if existing_template:
            if not messagebox.askyesno("Overwrite Template", f"A template named '{template_name}' already exists.\nDo you want to overwrite it?", parent=self.root): 
                return # User chose not to overwrite
            # Remove existing to replace it
            self.templates["templates"] = [t for t in self.templates["templates"] if t["name"] != template_name]
        
        template_description = simpledialog.askstring("Template Description", "Enter an optional description for the template:", parent=self.root)
        if template_description is None: template_description = "" # Handle cancel as empty string
            
        new_template = {
            "name": template_name,
            "description": template_description,
            "structure": current_structure,
            "created": datetime.now().isoformat()
        }
        
        self.templates.setdefault("templates", []).append(new_template) # Ensure "templates" list exists
        
        if self.save_json(self.templates_file,self.templates): 
            messagebox.showinfo("Success",f"Template '{template_name}' saved successfully!",parent=self.root)
            self.refresh_templates_list() # Update the list in the Templates tab
        else:
            # save_json already shows an error, but good to log here too
            self.logger.error(f"Failed to save template '{template_name}' to file.")


    def delete_selected_template(self):
        sel = self.templates_tree.selection()
        if not sel: messagebox.showwarning("Warning", "No template selected from the list to delete.", parent=self.root); return
        template_name = self.templates_tree.item(sel[0])['values'][0]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the template '{template_name}'?\nThis action cannot be undone.", parent=self.root): 
            return
            
        # Filter out the template to be deleted
        original_count = len(self.templates.get("templates", []))
        self.templates["templates"] = [t for t in self.templates.get("templates", []) if t["name"] != template_name]
        
        if len(self.templates.get("templates", [])) < original_count: # Check if deletion actually happened
            if self.save_json(self.templates_file,self.templates): 
                messagebox.showinfo("Success",f"Template '{template_name}' deleted.",parent=self.root)
                self.refresh_templates_list()
            else:
                # Attempt to revert if save failed (though this is tricky)
                self.logger.error(f"Failed to save templates file after deleting '{template_name}'. State might be inconsistent.")
                # Reloading templates might be an option here, or notifying user of save failure.
        else:
            messagebox.showerror("Error", f"Could not find template '{template_name}' to delete (it might have been removed already).", parent=self.root)
            self.logger.warning(f"Attempted to delete non-existent template '{template_name}'.")


    def refresh_templates_list(self):
        # Clear existing items in the tree
        for item in self.templates_tree.get_children():
            self.templates_tree.delete(item)
        
        # Load templates, sort by name (case-insensitive)
        loaded_templates = self.templates.get("templates",[])
        for tmpl in sorted(loaded_templates, key=lambda t: t.get("name","").lower()):
            name = tmpl.get("name", "Unnamed Template")
            description = tmpl.get("description","")
            created_iso = tmpl.get("created")
            if created_iso:
                try:
                    created_dt = datetime.fromisoformat(created_iso)
                    created_str = created_dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    created_str = "Invalid Date" # Handle malformed date string
            else:
                created_str = "N/A" # No creation date stored
            self.templates_tree.insert("","end",values=(name, description, created_str))


    def select_base_dir(self):
        # Suggest last used directory or script directory as initial
        initial_dir_to_show = self.base_dir_var.get() or str(self.script_dir)
        if not Path(initial_dir_to_show).is_dir(): # Fallback if last_directory is invalid
            initial_dir_to_show = str(self.script_dir)

        path_s = filedialog.askdirectory(initialdir=initial_dir_to_show, title="Select Base Directory", parent=self.root)
        if path_s: # If a path was selected (not cancelled)
            selected_path = Path(path_s)
            if not os.access(selected_path, os.W_OK | os.X_OK): # Check for write and execute (list) permissions
                 messagebox.showwarning("Permissions Issue",f"The selected directory '{selected_path}' may not be writable or accessible. Please check permissions.",parent=self.root)
            self.base_dir_var.set(str(selected_path))
            self.config["last_directory"] = str(selected_path) # Save for next session
            self.update_status(f"Base directory set to: {selected_path}")


    def get_file_size_str(self,file_path:Path) -> str:
        try: 
            size_bytes = file_path.stat().st_size
        except OSError: 
            return "N/A"
        
        if size_bytes == 0: return "0 B" # Handle zero byte files explicitly
        
        units = ['B','KB','MB','GB','TB','PB']
        size = float(size_bytes)
        unit_idx = 0
        while size >= 1024.0 and unit_idx < len(units) - 1:
            size /= 1024.0
            unit_idx += 1
        return f"{size:.1f} {units[unit_idx]}"


    def new_project(self):
        if messagebox.askyesno("New Project","This will clear the current workspace (definitions, staged files, pool, etc.).\nAre you sure you want to start a new project?",parent=self.root):
            # Clear structure definitions
            self.structure_text.delete(1.0,"end")
            self.smart_organize_structure_text.delete(1.0,"end")
            
            # Clear base directory (optional, user might want to keep it)
            # self.base_dir_var.set("") 
            
            # Clear Quick Move tab
            self.clear_move_files_list()
            
            # Clear Smart Organize state
            self.smart_organize_skeleton.clear()
            if hasattr(self, 'mapping_tree'): # Ensure tree exists
                self.mapping_tree.delete(*self.mapping_tree.get_children())
            
            self.source_files_pool.clear()
            self.source_pool_count_var.set("Pool: 0 files")
            
            self.staged_files.clear()
            if hasattr(self, 'staged_files_listbox'): # Ensure listbox exists
                self.staged_files_listbox.delete(0,tk.END)
            
            self._update_smart_organize_completion()
            self.update_status("New project initialized. Workspace cleared.",0)
            self.logger.info("New project started, workspace cleared.")


    def load_structure_definition(self):
        # Suggest last directory or script directory for opening files
        initial_dir_path = Path(self.config.get("last_directory", str(self.script_dir)))
        if not initial_dir_path.is_dir(): initial_dir_path = self.script_dir

        path_s = filedialog.askopenfilename(
            initialdir=str(initial_dir_path),
            filetypes=[("Text Files","*.txt"),("All Files","*.*")],
            title="Load Structure Definition from File",
            parent=self.root
        )
        if path_s: # If a file was selected
            try: 
                loaded_text = Path(path_s).read_text(encoding='utf-8')
                self.structure_text.delete(1.0,"end")
                self.structure_text.insert(1.0, loaded_text)
                self.update_status(f"Structure definition loaded from: {Path(path_s).name}",0)
                self.logger.info(f"Loaded structure definition from {path_s}")
            except Exception as e: 
                messagebox.showerror("Load Error",f"Failed to load structure definition from '{path_s}':\n{e}",parent=self.root)
                self.logger.error(f"Error loading structure definition from {path_s}: {e}", exc_info=True)


    def save_structure_definition(self):
        current_structure = self.structure_text.get(1.0,"end").strip()
        if not current_structure: 
            messagebox.showwarning("Save Warning","The structure definition is empty. Nothing to save.",parent=self.root); return
        
        initial_dir_path = Path(self.config.get("last_directory", str(self.script_dir)))
        if not initial_dir_path.is_dir(): initial_dir_path = self.script_dir
        
        path_s = filedialog.asksaveasfilename(
            initialdir=str(initial_dir_path),
            defaultextension=".txt",
            filetypes=[("Text Files","*.txt"),("All Files","*.*")],
            title="Save Structure Definition As",
            parent=self.root
        )
        if path_s: # If a path was chosen (not cancelled)
            try: 
                Path(path_s).write_text(current_structure,encoding='utf-8')
                self.update_status(f"Structure definition saved to: {Path(path_s).name}",0)
                messagebox.showinfo("Success","Structure definition saved successfully.",parent=self.root)
                self.logger.info(f"Saved structure definition to {path_s}")
            except Exception as e: 
                messagebox.showerror("Save Error",f"Failed to save structure definition to '{path_s}':\n{e}",parent=self.root)
                self.logger.error(f"Error saving structure definition to {path_s}: {e}", exc_info=True)


    def import_template(self):
        initial_dir_path = self.data_dir # Default to data_dir for templates
        if not initial_dir_path.is_dir(): initial_dir_path = self.script_dir

        path_s = filedialog.askopenfilename(
            initialdir=str(initial_dir_path),
            filetypes=[("JSON Files","*.json")],
            title="Import Template from JSON File",
            parent=self.root
        )
        if path_s:
            try:
                imported_data = self.load_json(Path(path_s), None) # load_json handles file reading and basic JSON errors
                
                if not (imported_data and isinstance(imported_data, dict) and 
                        "name" in imported_data and "structure" in imported_data): 
                    raise ValueError("Invalid template file format. Must be a JSON object with 'name' and 'structure' keys.")
                
                template_name = imported_data["name"]
                
                # Check for existing template and confirm overwrite
                current_templates = self.templates.get("templates", [])
                existing_template_idx = next((idx for idx, t in enumerate(current_templates) if t["name"] == template_name), -1)
                
                if existing_template_idx != -1:
                    if not messagebox.askyesno("Overwrite Template",f"A template named '{template_name}' already exists.\nDo you want to overwrite it?",parent=self.root): 
                        return # User chose not to overwrite
                    current_templates.pop(existing_template_idx) # Remove the old one
                
                # Ensure 'created' and 'description' fields exist, defaulting if missing from imported file
                imported_data.setdefault("created", datetime.now().isoformat())
                imported_data.setdefault("description", "")

                current_templates.append(imported_data)
                self.templates["templates"] = current_templates # Update the main templates structure
                
                if self.save_json(self.templates_file, self.templates): 
                    self.refresh_templates_list()
                    messagebox.showinfo("Success",f"Template '{template_name}' imported successfully.",parent=self.root)
                    self.logger.info(f"Imported template '{template_name}' from {path_s}")
                # else: save_json would have shown an error

            except ValueError as ve: # Specific error for invalid template format
                 messagebox.showerror("Import Error",f"Failed to import template: {ve}",parent=self.root)
                 self.logger.error(f"Import template format error from {path_s}: {ve}")
            except Exception as e: 
                messagebox.showerror("Import Error",f"An unexpected error occurred while importing template from '{path_s}':\n{e}",parent=self.root)
                self.logger.error(f"Unexpected import template error from {path_s}: {e}", exc_info=True)


    def export_template(self):
        sel = self.templates_tree.selection()
        if not sel: 
            messagebox.showwarning("Export Warning","No template selected from the list to export.",parent=self.root); return
        
        template_name_from_tree = self.templates_tree.item(sel[0])['values'][0]
        template_to_export = next((t for t in self.templates.get("templates", []) if t["name"] == template_name_from_tree), None)
        
        if not template_to_export: 
            messagebox.showerror("Export Error",f"Could not find the selected template '{template_name_from_tree}' in the internal data. Please refresh the list.",parent=self.root)
            self.logger.error(f"Template '{template_name_from_tree}' selected in tree but not found in self.templates.")
            return
        
        # Sanitize name for use as a default filename
        safe_filename = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in template_to_export["name"]).rstrip()
        initial_filename_suggestion = f"{safe_filename}.json"
        
        initial_dir_path = self.data_dir # Default to data_dir for templates
        if not initial_dir_path.is_dir(): initial_dir_path = self.script_dir

        path_s = filedialog.asksaveasfilename(
            initialdir=str(initial_dir_path),
            initialfile=initial_filename_suggestion,
            defaultextension=".json",
            filetypes=[("JSON Files","*.json")],
            title="Export Selected Template As",
            parent=self.root
        )
        if path_s: # If a path was chosen
            if self.save_json(Path(path_s), template_to_export): 
                messagebox.showinfo("Success",f"Template '{template_to_export['name']}' exported successfully to '{Path(path_s).name}'.",parent=self.root)
                self.logger.info(f"Exported template '{template_to_export['name']}' to {path_s}")
            # else: save_json would have shown its own error message


    def undo_last_operation(self):
        if not self.history: 
            messagebox.showinfo("Undo","Operation history is empty. Nothing to undo.",parent=self.root); return
        
        last_op_details = self.history[-1] # Get the last operation
        op_type = last_op_details.get("operation","unknown operation")
        num_actions = len(last_op_details.get("actions",[]))
        
        confirm_msg = f"Are you sure you want to attempt to undo the last operation:\n'{op_type}' ({num_actions} recorded actions)?\n\nBasic undo functionality. May not be perfect or fully reversible."
        if not messagebox.askyesno("Confirm Undo",confirm_msg,parent=self.root): return
        
        self.logger.warning(f"Attempting to undo operation: {op_type} with {num_actions} actions.")
        undone_action_count = 0
        
        try:
            actions_to_undo = last_op_details.get("actions",[])
            
            if op_type == "create_structure":
                # For creation, delete created files/folders in reverse order of creation
                for act in reversed(actions_to_undo):
                    path_to_remove = Path(act.get("path"))
                    item_type = act.get("type")
                    try:
                        if item_type == "create_file" and path_to_remove.is_file(): 
                            path_to_remove.unlink(); undone_action_count+=1
                            self.log_operation(f"Undo: Deleted file {path_to_remove}")
                        elif item_type == "create_dir" and path_to_remove.is_dir():
                            if not any(path_to_remove.iterdir()): # Only remove if empty
                                path_to_remove.rmdir(); undone_action_count+=1
                                self.log_operation(f"Undo: Removed empty directory {path_to_remove}")
                            else:
                                self.log_operation(f"Undo: Skipped non-empty directory {path_to_remove}", "warning")
                    except Exception as e_undo_item: 
                        self.log_operation(f"Undo error for item {path_to_remove}: {e_undo_item}","error")
            
            elif op_type.startswith("move_files") or op_type.startswith("smart_organize_move"):
                # For move, move files back from target to original source
                for act in reversed(actions_to_undo):
                    original_source = Path(act.get("source"))
                    moved_to_target = Path(act.get("target"))
                    try:
                        if moved_to_target.exists() and moved_to_target.is_file(): 
                            original_source.parent.mkdir(parents=True,exist_ok=True) 
                            shutil.move(str(moved_to_target),str(original_source))
                            undone_action_count+=1
                            self.log_operation(f"Undo: Moved {moved_to_target} back to {original_source}")
                        else:
                            self.log_operation(f"Undo: Target {moved_to_target} for move-back not found or not a file.", "warning")
                    except Exception as e_undo_move: 
                        self.log_operation(f"Undo move error for {moved_to_target} to {original_source}: {e_undo_move}","error")

            elif op_type.startswith("smart_organize_copy"):
                # For copy, delete the copied files at the target location
                 for act in reversed(actions_to_undo):
                    copied_to_target = Path(act.get("target"))
                    try:
                        if copied_to_target.exists() and copied_to_target.is_file():
                            copied_to_target.unlink(); undone_action_count+=1
                            self.log_operation(f"Undo: Deleted copied file {copied_to_target}")
                        else:
                            self.log_operation(f"Undo: Copied file {copied_to_target} not found for deletion.", "warning")
                    except Exception as e_undo_copy_del: 
                        self.log_operation(f"Undo delete copied file error for {copied_to_target}: {e_undo_copy_del}", "error")
            else: 
                messagebox.showinfo("Undo Not Implemented",f"Undo functionality for operation type '{op_type}' is not specifically implemented yet.",parent=self.root)
                return # Do not pop from history if undo is not implemented for this type
            
            # If undo was attempted (even if not all actions were reversible)
            self.history.pop() # Remove the operation from history
            self.save_json(self.history_file,self.history) # Save the updated history
            
            final_undo_msg=f"Undo attempt for '{op_type}' complete."
            if undone_action_count > 0:
                final_undo_msg += f" Approximately {undone_action_count} actions were reversed."
            else:
                final_undo_msg += " No specific file/folder actions were reversed (possibly due to errors or items already changed)."
            messagebox.showinfo("Undo Status",final_undo_msg,parent=self.root)
            self.logger.info(final_undo_msg)

        except Exception as e_general_undo: 
            self.logger.error(f"A general error occurred during the undo process: {e_general_undo}",exc_info=True)
            messagebox.showerror("Undo Error",f"An unexpected error occurred during undo: {e_general_undo}",parent=self.root)
        finally: 
            self._update_undo_menu_state() # Update menu regardless of outcome


    def clear_history(self):
        if not self.history:
            messagebox.showinfo("Clear History", "Operation history is already empty.", parent=self.root)
            return
        if messagebox.askyesno("Confirm Clear History","Are you sure you want to clear all operation history?\nThis action cannot be undone.",parent=self.root):
            self.history=[]; self.save_json(self.history_file,self.history)
            messagebox.showinfo("Success","Operation history has been cleared.",parent=self.root)
            self.logger.info("Operation history cleared by user.")
            self._update_undo_menu_state()


    def show_history(self):
        if not self.history: 
            messagebox.showinfo("Operation History","The operation history is empty.",parent=self.root); return
        
        history_display_entries = []
        for entry_data in reversed(self.history): # Show newest first
            timestamp_str = datetime.fromisoformat(entry_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            operation_name = entry_data.get('operation','Unknown Operation')
            base_dir_info = entry_data.get('base_directory','N/A')
            actions_list = entry_data.get('actions',[])
            num_actions = len(actions_list)
            
            entry_summary = f"[{timestamp_str}] Operation: {operation_name}\n  Base Directory: {base_dir_info}\n  Recorded Actions: {num_actions}"
            
            # Optionally, list a few actions if not too many
            if 0 < num_actions <= 5: # Show details for a small number of actions
                 actions_details_str = "\n    Actions Taken:"
                 for act_detail in actions_list:
                     act_type = act_detail.get('type', '?')
                     act_path = act_detail.get('path', act_detail.get('target', act_detail.get('source', 'N/A')))
                     actions_details_str += f"\n      - {act_type}: ...{str(Path(act_path).name)}" # Show only filename for brevity
                 entry_summary += actions_details_str
            elif num_actions > 5:
                entry_summary += "\n    (Too many actions to list details here)"

            history_display_entries.append(entry_summary)

        full_history_content = "Operation History (Newest First):\n\n" + \
                               "\n\n" + ("-"*50 + "\n\n").join(history_display_entries)
        ShowTextDialog(self.root,"Operation History",full_history_content,geometry="850x650")


    def show_templates_tab(self): 
        # Assumes templates tab is the 4th tab (index 3)
        try:
            self.notebook.select(3) 
            self.refresh_templates_list() 
        except tk.TclError:
            self.logger.error("Failed to select templates tab, it might not exist or index is wrong.")
            messagebox.showerror("Error", "Could not switch to Templates tab.", parent=self.root)


    def toggle_dark_mode(self):
        try:
            current_theme = self.root.tk.call("ttk::style", "theme", "use") # Get current theme directly
        except tk.TclError:
            self.logger.warning("Could not determine current theme. Applying default light theme.")
            current_theme = DEFAULT_THEME # Fallback

        new_theme_to_set = DARK_THEME if current_theme != DARK_THEME else DEFAULT_THEME
        
        try: 
            self.root.set_theme(new_theme_to_set)
            self.config["theme"] = new_theme_to_set # Save preference
            self.update_status(f"Theme changed to: {new_theme_to_set}.",0)
            self.logger.info(f"Theme set to {new_theme_to_set}")
        except Exception as e_theme: 
            # Attempt to revert to the original theme if setting the new one failed
            self.logger.error(f"Failed to set theme '{new_theme_to_set}': {e_theme}. Attempting to revert.")
            messagebox.showerror("Theme Error",f"Failed to apply theme '{new_theme_to_set}': {e_theme}\nAttempting to restore previous theme.",parent=self.root)
            try:
                self.root.set_theme(current_theme) # Revert to the theme that was active
                self.config["theme"] = current_theme # Also revert in config
            except Exception as e_revert:
                self.logger.error(f"Failed to revert to theme '{current_theme}': {e_revert}. Applying failsafe default.")
                # Failsafe: apply a known default if revert also fails
                self.root.set_theme(DEFAULT_THEME) 
                self.config["theme"] = DEFAULT_THEME


    def show_directory_stats(self):
        path_s_for_stats = self.base_dir_var.get()
        if not (path_s_for_stats and Path(path_s_for_stats).is_dir()): 
            messagebox.showerror("Directory Not Selected","Please select a valid base directory for which to calculate statistics.",parent=self.root)
            return
        
        target_path_obj = Path(path_s_for_stats)
        self.update_status(f"Calculating statistics for '{target_path_obj.name}'...",-1) # Indeterminate progress
        
        num_files, num_folders, total_size_bytes = 0, 0, 0
        
        try:
            # os.walk is generally efficient for this
            for dirpath, dirnames, filenames in os.walk(target_path_obj):
                if self.cancel_operation: # Check for cancellation during a potentially long walk
                    self._finish_operation() # Handles cancel message
                    return

                num_folders += len(dirnames)
                num_files += len(filenames)
                for f_name_stat in filenames:
                    try:
                        full_f_path = Path(dirpath) / f_name_stat
                        total_size_bytes += full_f_path.stat().st_size
                    except (FileNotFoundError, OSError): 
                        # File might have been deleted during the walk, or inaccessible
                        self.logger.warning(f"Could not stat file {full_f_path} during stats calculation, skipping.")
                        pass 
            
            if self.cancel_operation: # Final check after loop
                self._finish_operation()
                return

            # Format total size into human-readable string
            formatted_size_val, size_unit_str = float(total_size_bytes), "B" 
            for test_unit in ['KB','MB','GB','TB','PB']:
                if formatted_size_val < 1024.0: break
                formatted_size_val /= 1024.0
                size_unit_str = test_unit
                
            stats_message = f"Statistics for Directory: {target_path_obj}\n\n" \
                            f"Total Folders: {num_folders:,}\n" \
                            f"Total Files: {num_files:,}\n" \
                            f"Total Size: {formatted_size_val:.2f} {size_unit_str}"
            
            messagebox.showinfo("Directory Statistics",stats_message,parent=self.root)
            self.update_status("Directory statistics displayed.",0)
            self.logger.info(f"Calculated stats for {target_path_obj}: {num_folders} folders, {num_files} files, {total_size_bytes} bytes.")

        except Exception as e_stats: 
            messagebox.showerror("Statistics Error",f"An error occurred while calculating statistics for '{target_path_obj}':\n{e_stats}",parent=self.root)
            self.logger.error(f"Error calculating directory statistics for {target_path_obj}: {e_stats}", exc_info=True)
            self.update_status("Error calculating statistics.",0)


    def cleanup_empty_folders(self):
        path_s_to_cleanup = self.base_dir_var.get()
        if not (path_s_to_cleanup and Path(path_s_to_cleanup).is_dir()): 
             messagebox.showerror("Directory Not Selected","Please select a valid base directory in which to clean up empty folders.",parent=self.root); return
        
        target_path_to_cleanup = Path(path_s_to_cleanup)
        confirm_cleanup = messagebox.askyesno(
            "Confirm Empty Folder Cleanup",
            f"Are you sure you want to remove ALL empty subfolders within:\n'{target_path_to_cleanup}'?\n\nThis action cannot be easily undone.",
            parent=self.root, icon='warning'
        )
        if not confirm_cleanup: return
        
        if not self._start_operation("Cleanup Empty Folders"): return
        threading.Thread(target=self._cleanup_empty_folders_worker,args=(target_path_to_cleanup,),daemon=True).start()

    def _cleanup_empty_folders_worker(self, base_dir_to_scan: Path):
        removed_folders_count = 0
        try:
            # Iterate from bottom-up to correctly remove nested empty folders
            for dirpath_str, dirnames_list, filenames_list in os.walk(base_dir_to_scan, topdown=False):
                if self.cancel_operation:
                    self.logger.info("Cleanup empty folders operation cancelled by user.")
                    break 
                
                current_scanned_dir = Path(dirpath_str)
                # Update status with a truncated relative path for readability
                relative_display_path = str(current_scanned_dir.relative_to(base_dir_to_scan))
                if len(relative_display_path) > 60: relative_display_path = "..." + relative_display_path[-57:]
                self.update_status(f"Scanning: {relative_display_path}", -1) 

                # A directory is empty if it contains no subdirectories and no files
                if not dirnames_list and not filenames_list: 
                    # For safety, double-check with iterdir() before removing
                    # This handles cases where os.walk might list a dir as empty but it has hidden files not caught by default
                    # or if files were created after os.walk listed its contents but before this check.
                    is_truly_empty = True # Assume true
                    try:
                        if any(current_scanned_dir.iterdir()): # If iterdir finds anything, it's not empty
                            is_truly_empty = False
                            self.logger.debug(f"Directory {current_scanned_dir} initially seemed empty via os.walk, but iterdir found items.")
                    except OSError as e_iter: # Permission error accessing directory
                        self.logger.warning(f"OSError checking if {current_scanned_dir} is truly empty: {e_iter}. Skipping removal.")
                        is_truly_empty = False # Don't attempt removal if we can't verify

                    if is_truly_empty:
                        try:
                            current_scanned_dir.rmdir() # Attempt to remove the empty directory
                            self.log_operation(f"Removed empty directory: {current_scanned_dir}")
                            removed_folders_count += 1
                        except OSError as e_rmdir: # e.g., permission error, or dir not actually empty (race condition)
                            self.log_operation(f"Could not remove directory {current_scanned_dir} (OSError): {e_rmdir}", "warning")
                        except Exception as e_rmdir_general: # Catch any other potential errors during rmdir
                            self.log_operation(f"Unexpected error removing directory {current_scanned_dir}: {e_rmdir_general}", "error")
            
            if self.cancel_operation:
                self._finish_operation() # Handles cancel message and resets state
            else:
                final_cleanup_msg = f"Empty folder cleanup complete. Removed {removed_folders_count} empty folder(s) from '{base_dir_to_scan}'."
                self._finish_operation(success_msg=final_cleanup_msg)
                if hasattr(self, 'root') and self.root.winfo_exists():
                    messagebox.showinfo("Cleanup Complete", final_cleanup_msg, parent=self.root)

        except Exception as e_worker_main: # Catch errors from os.walk itself or other parts of the try block
            self.logger.error(f"Error during the main cleanup process for empty folders: {e_worker_main}", exc_info=True)
            if hasattr(self, 'root') and self.root.winfo_exists(): 
                messagebox.showerror("Cleanup Process Error", f"An unexpected error occurred during cleanup: {e_worker_main}", parent=self.root)
            self._finish_operation(error_msg="Cleanup of empty folders failed.")

    # --- Help Menu Methods ---
    def show_user_guide(self):
        self.logger.info("User Guide menu item clicked.")
        guide_text = """
Directory Tool v2.2 - User Guide

1. Define & Create Structure (Tab 1):
   - Define a directory structure using text.
     - Indent with spaces (default 4) or tabs to create subdirectories.
     - End a line with '/' to mark it as a directory (e.g., 'folder/').
     - Lines without '/' are treated as files (e.g., 'file.txt').
     - Example:
       project_root/
           src/
               main.py
           data/
               input.csv
           README.md
   - 'Load Sample': Loads a sample structure.
   - 'Clear Definition': Clears the text area.
   - 'Base Directory': Select where the structure will be created.
   - 'Create Structure Now': Creates the defined folders and empty files.
   - 'Preview Structure': Shows what will be created without making changes.

2. Quick Move Files (Tab 2):
   - Select individual files or all files from a folder.
   - 'Target Directory': Choose the destination for the selected files.
   - 'Move Selected Files': Moves the files. Handles name conflicts by appending '_<number>'.

3. Smart Organize & Package (Tab 3):
   This tab helps you gather files from various sources and organize them into a predefined structure, then optionally package them as a ZIP.

   Left Pane (File Staging & Pool Area):
     - 'Add Files/Folder to Stage': Add files you intend to assign to specific target slots in the skeleton. Staged files are removed from stage once assigned.
     - 'Clear Stage': Empties the staging area.
     - 'Assign Staged to Target(s) →': Manually assign selected staged file(s) to selected target(s) in the Skeleton Tree.
       - One staged file to one or more targets (copies reference).
       - Multiple staged files to an equal number of targets (1-to-1).
     - 'Auto-Assign from Stage': Tries to match files in stage to MISSING file slots in the skeleton based on name similarity.
     - 'Load Source Pool': Load a general collection of files (e.g., an entire project folder). These files are NOT removed when matched.
     - 'Clear Pool': Empties the general source pool.
     - 'Auto-Match from Pool': Tries to match files from the pool to MISSING file slots in the skeleton.

   Right Pane (Target Structure & Actions):
     - 'Target Structure Definition': Define the desired output structure here (same format as Tab 1).
     - 'Use from Tab 1': Copies the structure from Tab 1.
     - 'Load Sample': Loads a sample package structure.
     - 'Build/Rebuild Skeleton Tree': Parses the definition and creates a list of target paths (the "skeleton").
     - 'File Mapping & Status Tree':
       - Shows target paths, their type (file/directory), assigned source file, and status (Missing, Auto-Matched, Assigned).
       - Right-click a target file for options: 'Browse & Assign Source...' or 'Clear Assignment...'.
       - 'Clear All Assignments': Resets all file assignments in the tree.
     - 'Completion %': Shows how many file slots in the skeleton have been assigned a source.
     - 'Base Directory': The root directory where the organized files will be placed or where the ZIP package will be created (conceptually).
     - 'Organize Assigned Files (Move/Copy)':
       - Prompts for 'copy' or 'move'.
       - Creates the defined directory structure under the selected Base Directory.
       - Copies/moves the assigned source files to their respective target locations within this new structure.
     - 'Download Package as Zip':
       - Creates a temporary structure with the assigned files.
       - Zips this temporary structure and prompts for where to save the .zip file.

4. Manage Templates (Tab 4):
   - Save and load frequently used directory structure definitions.
   - 'Load to Tab 1': Loads the selected template's structure into Tab 1.
   - 'Save Tab 1 Structure as Template': Saves the current definition from Tab 1.
   - 'Delete Selected': Removes the template.
   - 'Refresh List': Updates the list of templates.

Menu Bar:
  - File: New project, Load/Save definition, Import/Export template, Exit.
  - Edit: Undo last major operation (basic undo), Clear History.
  - View: Toggle Dark Mode, Show History, Show Templates tab.
  - Tools: Directory Statistics, Cleanup Empty Folders in selected Base Directory.
  - Help: This User Guide, Keyboard Shortcuts, About.

General:
  - Configuration (theme, last directory) is saved in 'data/config.json'.
  - Operation history is saved in 'data/history.json'.
  - Templates are saved in 'data/templates.json'.
  - Logs are in 'logs/directory_tool.log'.
  - Long operations run in threads and can often be cancelled via a prompt or by closing the app.
"""
        ShowTextDialog(self.root, "User Guide - Directory Tool", guide_text, geometry="800x700")

    def show_shortcuts(self):
        self.logger.info("Keyboard Shortcuts menu item clicked.")
        shortcuts_text = """
Keyboard Shortcuts:

- Ctrl + N:      New Project (clears workspace)
- Ctrl + O:      Load Structure Definition (to Tab 1)
- Ctrl + S:      Save Structure Definition (from Tab 1)
- Ctrl + Z:      Undo Last Operation (if available)
- Ctrl + D:      Toggle Dark/Light Mode
- Ctrl + Q:      Exit Application

Note: Focus must be on the main window or a non-text-input widget for some shortcuts to register globally.
"""
        ShowTextDialog(self.root, "Keyboard Shortcuts", shortcuts_text, geometry="500x300")

    def show_about(self):
        self.logger.info("About menu item clicked.")
        about_text = f"""
Directory Tool v2.2 (Corrected)

A utility for defining, creating, and managing directory
structures and organizing files.

Features:
- Visual directory structure definition.
- Batch creation of directories and placeholder files.
- Quick file moving.
- Smart file organization into a target structure.
- ZIP packaging of organized files.
- Template management for structures.
- Undo for some operations.
- Light and Dark themes.

Script Directory: {self.script_dir}
Data Directory: {self.data_dir}

Developed with Python and Tkinter.
© 2024-2025 [Your Name/Organization Here]
"""
        ShowTextDialog(self.root, "About Directory Tool", about_text, geometry="550x450")
    # --- End Help Menu Methods ---

    def on_closing(self):
        if self.current_operation:
            if not messagebox.askokcancel("Operation in Progress",f"'{self.current_operation}' is running. Quit anyway?\nThis may leave tasks incomplete.",parent=self.root): return
            self.cancel_operation=True; self.logger.info(f"User initiated cancel for '{self.current_operation}' during app close.")
            self.update_status(f"Cancelling {self.current_operation}...", 0) # Update status
            self.root.after(750,self._perform_destroy) # Give a bit more time for thread to see cancel
            return
        
        # Save config before asking to quit, in case of unexpected shutdown later
        self.save_json(self.config_file, self.config) 
        
        if messagebox.askokcancel("Quit","Are you sure you want to quit Directory Tool?",parent=self.root): 
            self._perform_destroy()
            
    def _perform_destroy(self):
        self.logger.info("Application closing process initiated.")
        # Final attempt to save critical data if not done by on_closing
        # or if an operation was cancelled and didn't save.
        if not self.current_operation or self.cancel_operation: 
            self.save_json(self.config_file,self.config) 
            # self.save_json(self.history_file, self.history) # History is usually saved per operation
            # self.save_json(self.templates_file, self.templates) # Templates saved on change
        
        self.logger.info("Root destroy called.")
        if hasattr(self, 'root') and self.root.winfo_exists():
            try:
                self.root.destroy()
            except tk.TclError as e:
                self.logger.error(f"TclError during root.destroy(): {e}. May already be destroying.")
        logging.shutdown()


class TextWithScrollbars(ttk.Frame):
    def __init__(self,master,**kwargs):
        super().__init__(master)
        # Sensible defaults for Text widget if not provided
        text_defaults = {"undo": True, "maxundo": 50, "wrap": "none", "font": ("Segoe UI", 10)}
        text_defaults.update(kwargs) # Allow kwargs to override defaults

        self.text_widget=tk.Text(self,**text_defaults)
        v_scroll=ttk.Scrollbar(self,orient="vertical",command=self.text_widget.yview)
        h_scroll=ttk.Scrollbar(self,orient="horizontal",command=self.text_widget.xview)
        self.text_widget.configure(yscrollcommand=v_scroll.set,xscrollcommand=h_scroll.set)
        
        self.text_widget.grid(row=0,column=0,sticky="nsew")
        v_scroll.grid(row=0,column=1,sticky="ns")
        h_scroll.grid(row=1,column=0,sticky="ew")
        
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)

    def get(self,start,end): return self.text_widget.get(start,end)
    def insert(self,index,chars,*args): self.text_widget.insert(index,chars,*args)
    def delete(self,start,end=None): self.text_widget.delete(start,end)

class ShowTextDialog(tk.Toplevel):
    def __init__(self,parent,title,content,geometry="600x400"):
        super().__init__(parent)
        self.title(title)
        
        # Attempt to apply parent's theme background if possible
        try: 
            bg_color = ttk.Style(parent).lookup("TFrame", "background", default="SystemButtonFace")
            self.configure(bg=bg_color)
        except (tk.TclError, AttributeError): 
            self.logger.warning("Could not get themed background for ShowTextDialog.") if hasattr(self, 'logger') else None
            pass # Fallback to default Toplevel background

        main_dialog_frame=ttk.Frame(self, padding=10)
        main_dialog_frame.pack(fill="both",expand=True)
        
        text_widget_area=TextWithScrollbars(main_dialog_frame,wrap="word",relief="solid",borderwidth=1, font=("Segoe UI", 9), height=15, width=70)
        text_widget_area.pack(fill="both",expand=True, pady=(0,10))
        text_widget_area.insert("1.0",content)
        text_widget_area.text_widget.config(state="disabled") # Make text read-only
        
        button_frame_dialog=ttk.Frame(main_dialog_frame)
        button_frame_dialog.pack(pady=(5,0)) # Add some padding above button
        ok_button=ttk.Button(button_frame_dialog,text="OK",command=self.destroy,style="Accent.TButton")
        ok_button.pack()
        
        self.transient(parent) # Keep dialog on top of parent
        self.grab_set() # Modal behavior: block interaction with parent
        
        self.bind('<Escape>',lambda e:self.destroy()) # Close on Escape key
        self.protocol("WM_DELETE_WINDOW",self.destroy) # Handle window close button
        
        self.update_idletasks() # Ensure dimensions are calculated for centering

        # Centering logic (improved)
        parent.update_idletasks() # Ensure parent dimensions are current
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        # Calculate position to center on parent, ensuring it's within screen bounds (basic check)
        pos_x = parent_x + (parent_width // 2) - (dialog_width // 2)
        pos_y = parent_y + (parent_height // 2) - (dialog_height // 2)

        # Basic screen boundary adjustment (can be more sophisticated)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        if pos_x + dialog_width > screen_width: pos_x = screen_width - dialog_width - 10
        if pos_y + dialog_height > screen_height: pos_y = screen_height - dialog_height - 30 # Account for title bar
        if pos_x < 0: pos_x = 10
        if pos_y < 0: pos_y = 10
        
        self.geometry(f'{dialog_width}x{dialog_height}+{pos_x}+{pos_y}') # Set size and position
        
        self.focus_set() # Set focus to this dialog
        ok_button.focus_set() # Set focus to OK button for easy Enter key press
        self.wait_window() # Wait until this dialog is closed

class OperationCancelledError(Exception): pass

if __name__ == "__main__":
    try:
        script_location = Path(__file__).resolve().parent
        os.chdir(script_location)
    except NameError: 
        print(f"INFO: Running from CWD: {Path.cwd()} (__file__ not defined)")
    except Exception as e_chdir:
        print(f"WARNING: Could not change CWD to script location: {e_chdir}. CWD: {Path.cwd()}")

    root = ThemedTk() 
    
    app = DirectoryTool(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
