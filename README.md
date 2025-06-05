# Directory Tool V1

## Overview

The Directory Tool is a Python-based desktop application built with Tkinter and `ttkthemes` designed to help users define, create, manage, and organize directory structures and files. It provides a graphical user interface for several file and directory operations, including batch creation, quick file moving, smart organization based on a defined skeleton, and packaging into ZIP archives.

## Installation

1. **Install Python:**
   - Download Python 3.8 or higher from [python.org](https://python.org)
   - During installation, ensure "Add Python to PATH" is checked
   - Verify installation: `python --version`

2. **Set up Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Unix/macOS
   # OR
   venv\Scripts\activate     # On Windows
   ```

3. **Install Dependencies:**
   ```bash
   pip install .
   ```

## Features

### Define & Create Structure (Tab 1)
- Visually define complex directory and file structures using an indented text format
- Support for comments in structure definitions
- Preview the structure before creation
- Create the defined directory structure and empty placeholder files
- Load sample structures and clear definitions

### Quick Move Files (Tab 2)
- Select multiple files or entire folders (recursively) to be moved
- Display selected files with path, size, and type in a tree view
- Move selected files to a specified target directory
- Automatic conflict resolution with smart renaming

### Smart Organize & Package (Tab 3)
- **File Management:**
  - File Staging Area for individual files/folders
  - Source Pool for larger file collections
  - Target Structure Definition
  - Visual Skeleton Tree representation
- **File Assignment:**
  - Manual assignment to specific slots
  - Automatic matching using fuzzy logic
  - Status tracking (Missing, Auto-Matched, Assigned)
- **Output Options:**
  - Organize files into target structure
  - Create ZIP archives preserving structure

### Manage Templates (Tab 4)
- Save and load directory structure templates
- Import/Export templates as JSON
- Template management and organization

## Application Structure

```
directory_tool/
├── data/
│   ├── config.json       # User preferences
│   ├── history.json      # Operation history
│   ├── templates.json    # Structure templates
│   └── temp_pkg_*/       # Temporary packaging
├── logs/
│   └── directory_tool.log
```

## Configuration

### Theme Settings
- Light theme (default): "radiance"
- Dark theme: "equilux"
- Toggle: View menu or Ctrl+D
- Settings saved in data/config.json

### Directory Preferences
- Last used directory saved automatically
- Configurable default locations
- Per-template base paths

## Troubleshooting

### Common Issues

#### ModuleNotFoundError: No module named '_signal'
This error indicates a corrupted Python installation. To resolve:

1. **Create Fresh Virtual Environment:**
   ```bash
   python -m venv fresh_env
   source fresh_env/bin/activate  # Unix/macOS
   # OR
   fresh_env\Scripts\activate     # Windows
   ```

2. **If Error Persists:**
   - Uninstall current Python installation
   - Download fresh copy from [python.org](https://python.org)
   - Enable "Add Python to PATH" during installation
   - Verify: `python --version`

3. **Install Dependencies:**
   ```bash
   pip install .
   ```

#### Other Known Issues
- **PanedWindow Styling:** Some themes may not support all styling options
- **Undo Operations:** Basic implementation with some limitations
- **Large Operations:** May experience delays with extensive file sets
- **Special Characters:** Unusual characters in paths may cause issues

## Performance Optimization

### Large Directory Operations
- Use batch processing for multiple files
- Enable threading for responsive UI
- Monitor progress indicators
- Cancel long-running operations if needed

### Memory Management
- Regular cleanup of temporary files
- Efficient handling of large directory trees
- Smart caching of frequently used templates

## Security Considerations

- File permissions preserved during operations
- Secure handling of sensitive path information
- Protected template storage
- Logging of security-relevant operations

## Development Guidelines

### Contributing
1. Fork the repository
2. Create feature branch
3. Follow code style guidelines
4. Submit pull request

### Testing
- Run test suite: `python -m pytest tests/`
- Add tests for new features
- Ensure backward compatibility

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

- GitHub Issues: [Report bugs](https://github.com/jigar48949/directory-tool/issues)
- Documentation: [Wiki](https://github.com/jigar48949/directory-tool/wiki)
- Community: [Discussions](https://github.com/jigar48949/directory-tool/discussions)