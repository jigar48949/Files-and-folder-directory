# Directory Tool V1

## Overview

The Directory Tool is a Python-based desktop application built with Tkinter and `ttkthemes` designed to help users define, create, manage, and organize directory structures and files. It provides a graphical user interface for several file and directory operations, including batch creation, quick file moving, smart organization based on a defined skeleton, and packaging into ZIP archives.

## Features

* **Define & Create Structure (Tab 1):**
    * Visually define complex directory and file structures using an indented text format.
    * Support for comments in structure definitions.
    * Preview the structure before creation.
    * Create the defined directory structure and empty placeholder files in a chosen base directory.
    * Load sample structures and clear definitions.
* **Quick Move Files (Tab 2):**
    * Select multiple files or entire folders (recursively) to be moved.
    * Display selected files with path, size, and type in a tree view.
    * Move selected files to a specified target directory, with automatic renaming for conflicts.
* **Smart Organize & Package (Tab 3):**
    * **File Staging Area:** Add individual files or folders to a temporary staging list.
    * **Source Pool:** Load a larger collection of source files for matching.
    * **Target Structure Definition:** Define the desired output structure (similar to Tab 1).
    * **Skeleton Tree:** Build a visual representation of the target structure.
    * **Manual Assignment:** Assign files from the staging area to specific file slots in the skeleton tree.
    * **Auto-Assignment:**
        * Automatically match files from the staging area to empty slots in the skeleton based on name similarity (using fuzzy matching).
        * Automatically match files from the general source pool to empty slots.
    * **File Mapping View:** Displays target paths, assigned source files, and their status (Missing, Auto-Matched, Assigned).
    * **Organize Files:** Copy or move assigned source files into the defined target structure within a chosen base directory.
    * **Download Package as Zip:** Create a ZIP archive of the organized files, maintaining the defined structure.
* **Manage Templates (Tab 4):**
    * Save frequently used directory structure definitions as named templates.
    * Load saved templates into Tab 1 for creation or Tab 3 for organization.
    * Delete and refresh templates.
    * Import/Export templates as JSON files.
* **General Features:**
    * **Undo Last Operation:** Basic undo functionality for some operations like structure creation and file moves (experimental).
    * **Operation History:** View a log of performed operations.
    * **Theming:** Toggle between light (default "radiance") and dark ("equilux") themes.
    * **Directory Statistics:** Calculate and display the number of files, folders, and total size for a selected directory.
    * **Cleanup Empty Folders:** Recursively remove empty subfolders within a selected directory.
    * **Persistent Configuration:** Saves theme preference and last used directory.
    * **Logging:** Detailed logging of operations and errors to `logs/directory_tool.log`.
    * **Threaded Operations:** Long-running tasks (creation, moving, zipping, etc.) are performed in separate threads to keep the UI responsive, with progress updates and cancellation support.

## Requirements

* Python 3.x
* Tkinter (usually included with standard Python installations)
* `ttkthemes`: For enhanced Tkinter widget styling. Install using pip:
    ```bash
    pip install ttkthemes
    ```
* `thefuzz` (and `python-Levenshtein` for better performance, optional but recommended): For fuzzy string matching. Install using pip:
    ```bash
    pip install thefuzz python-Levenshtein
    ```

## How to Run

1.  **Ensure Dependencies:** Make sure Python 3 is installed and the required libraries (`ttkthemes`, `thefuzz`) are installed in your Python environment.
2.  **Save the Script:** Save the Python code as a `.py` file (e.g., `directory_tool.py`).
3.  **Run from Terminal/IDE:** Execute the script from your terminal or IDE:
    ```bash
    python directory_tool.py
    ```
    The application window should appear.

## Application Directory Structure

When you run the script, it will create the following subdirectories in the same location as the script file if they don't already exist:

* `data/`: Stores application data.
    * `config.json`: Stores user preferences like theme and last opened directory.
    * `history.json`: Logs major operations for the undo feature and history view.
    * `templates.json`: Stores user-defined structure templates.
    * `temp_pkg_<timestamp>/` (Temporary): Created during the "Download Package as Zip" operation and deleted afterwards.
* `logs/`:
    * `directory_tool.log`: Contains detailed logs of application activity and errors.

## Configuration

* **Theme:** The application supports a light (default "radiance") and a dark ("equilux") theme, which can be toggled via the "View" menu or `Ctrl+D`. The selected theme is saved in `data/config.json`.
* **Last Directory:** The last successfully selected base directory is saved and reloaded on the next launch.

## Basic Usage

The application is organized into tabs for different functionalities:

1.  **Tab 1: Define & Create Structure**
    * Type or paste your desired directory structure into the text area. Use indentation for sub-items and a trailing `/` for directories.
    * Select a "Base Directory for Creation".
    * Click "Create Structure Now" or "Preview Structure".

2.  **Tab 2: Quick Move Files**
    * Use "Select Files" or "Select Folder of Files" to populate the list.
    * Select a "Target Directory for Moving Files".
    * Click "Move Selected Files".

3.  **Tab 3: Smart Organize & Package**
    * **Define Target Structure:** Enter the desired final structure in the "Target Structure Definition" text area (or load from Tab 1/Sample).
    * **Build Skeleton:** Click "Build/Rebuild Skeleton Tree". This populates the "File Mapping & Status" tree.
    * **Load Files:**
        * Use "Add Files/Folder to Stage" for files you want to specifically assign.
        * Use "Load Source Pool" for a general collection of files to be auto-matched.
    * **Assign Files:**
        * Manually: Select a file in "Staging Area" and a target in "File Mapping" tree, then click "Assign Staged to Target(s) →". Or right-click a target in the mapping tree to browse.
        * Automatically: Use "Auto-Assign from Stage" or "Auto-Match from Pool".
    * **Organize/Package:**
        * Select a "Base Directory for Organizing/Packaging".
        * Click "Organize Assigned Files" (choose copy/move) or "Download Package as Zip".

4.  **Tab 4: Manage Templates**
    * View, load, save, and delete structure templates.
    * Import/Export templates to share or back them up.

## Known Issues / Troubleshooting

* **PanedWindow Options:** Some Tkinter/ttk versions or themes might not support all `PanedWindow` styling options like `sashrelief` or `sashwidth`. The script has been adjusted to use only common options. If you encounter TclErrors related to PanedWindow options, these might need to be removed from the `ttk.PanedWindow(...)` call in the `create_smart_organize_tab` method.
* **Undo Limitations:** The undo feature is basic and might not perfectly reverse all operations, especially if files or directories have been modified externally after the operation.
* **Performance:** Operations on very large numbers of files or deep directory structures might take time. The UI should remain responsive due to threading, and progress is usually indicated.
* **File Paths with Special Characters:** While `pathlib` handles many cases, extremely unusual characters in file or directory names might cause issues with parsing or file operations.

## Potential Future Enhancements

* Full Drag & Drop support for files into Staging Area and Mapping Tree (requires `TkinterDnD2` integration).
* More advanced conflict resolution options (e.g., skip, rename all, overwrite all).
* More robust undo for all operations.
* Ability to define file content for placeholder files during structure creation.
* Filtering options for file selection and staging.
* Direct editing of the skeleton tree (e.g., renaming targets).

## License

This software is provided "as is". You are free to use, modify, and distribute it. (Consider adding a specific open-source license like MIT or GPL if desired).
