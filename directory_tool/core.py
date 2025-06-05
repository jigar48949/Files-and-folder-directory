from pathlib import Path
from typing import Union, List
import logging
import json
from dataclasses import dataclass

@dataclass
class FileInfo:
    path: Path
    size: int
    type: str

class DirectoryManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_structure(self, structure: str, base_path: Union[str, Path]) -> None:
        """Create directory structure from text definition."""
        base_path = Path(base_path)
        lines = [line.strip() for line in structure.split('\n') if line.strip()]
        
        for line in lines:
            indent = len(line) - len(line.lstrip())
            path_parts = line.strip().split('/')
            current_path = base_path
            
            for part in path_parts:
                if part:
                    current_path = current_path / part
                    if line.endswith('/'):
                        current_path.mkdir(parents=True, exist_ok=True)
                    else:
                        current_path.touch(exist_ok=True)
                        
    def get_file_info(self, path: Union[str, Path]) -> FileInfo:
        """Get information about a file."""
        path = Path(path)
        return FileInfo(
            path=path,
            size=path.stat().st_size if path.is_file() else 0,
            type='directory' if path.is_dir() else path.suffix[1:] or 'file'
        )
        
    def move_files(self, files: List[Union[str, Path]], target_dir: Union[str, Path]) -> None:
        """Move files to target directory."""
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            source = Path(file)
            if source.exists():
                target = target_dir / source.name
                if target.exists():
                    stem = target.stem
                    suffix = target.suffix
                    counter = 1
                    while target.exists():
                        target = target_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                source.rename(target)
                self.logger.info(f"Moved {source} to {target}")
            else:
                self.logger.warning(f"Source file {source} does not exist")