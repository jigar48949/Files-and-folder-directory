import pytest
from pathlib import Path
from directory_tool.core import DirectoryManager

def test_create_directory_structure(tmp_path):
    manager = DirectoryManager()
    structure = """
    project/
        src/
            main.py
        tests/
            test_main.py
        README.md
    """
    
    manager.create_structure(structure, tmp_path)
    
    assert (tmp_path / "project").is_dir()
    assert (tmp_path / "project" / "src").is_dir()
    assert (tmp_path / "project" / "src" / "main.py").is_file()
    assert (tmp_path / "project" / "tests").is_dir()
    assert (tmp_path / "project" / "tests" / "test_main.py").is_file()
    assert (tmp_path / "project" / "README.md").is_file()