from pathlib import Path
from typing import Union, List, Dict, Optional
import logging
import json
import shutil
import hashlib
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileInfo:
    path: Path
    size: int
    type: str
    modified: datetime
    hash: Optional[str] = None
    
    @property
    def formatted_size(self) -> str:
        """Return human-readable file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024:
                return f"{self.size:.1f}{unit}"
            self.size /= 1024
        return f"{self.size:.1f}TB"

class DirectoryManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._operation_history: List[Dict] = []
        
    def create_structure(self, structure: str, base_path: Union[str, Path]) -> None:
        """Create directory structure from text definition with improved error handling."""
        try:
            base_path = Path(base_path)
            lines = [line.strip() for line in structure.split('\n') if line.strip()]
            
            # Track created items for rollback
            created_items = []
            
            for line in lines:
                if line.startswith('#'):  # Support comments
                    continue
                    
                indent = len(line) - len(line.lstrip())
                path_parts = line.strip().split('/')
                current_path = base_path
                
                for part in path_parts:
                    if not part:
                        continue
                        
                    current_path = current_path / part
                    try:
                        if line.endswith('/'):
                            current_path.mkdir(parents=True, exist_ok=True)
                        else:
                            current_path.touch(exist_ok=True)
                        created_items.append(current_path)
                    except Exception as e:
                        self.logger.error(f"Failed to create {current_path}: {e}")
                        self._rollback_creation(created_items)
                        raise
            
            # Log successful operation
            self._operation_history.append({
                'operation': 'create_structure',
                'timestamp': datetime.now().isoformat(),
                'base_path': str(base_path),
                'items_created': len(created_items)
            })
            
        except Exception as e:
            self.logger.error(f"Structure creation failed: {e}")
            raise
            
    def _rollback_creation(self, items: List[Path]) -> None:
        """Rollback created items in case of failure."""
        for item in reversed(items):
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
            except Exception as e:
                self.logger.error(f"Rollback failed for {item}: {e}")
                
    def get_file_info(self, path: Union[str, Path], calculate_hash: bool = False) -> FileInfo:
        """Get detailed information about a file."""
        path = Path(path)
        stat = path.stat()
        
        file_hash = None
        if calculate_hash and path.is_file():
            try:
                file_hash = self._calculate_file_hash(path)
            except Exception as e:
                self.logger.warning(f"Failed to calculate hash for {path}: {e}")
        
        return FileInfo(
            path=path,
            size=stat.st_size if path.is_file() else 0,
            type='directory' if path.is_dir() else path.suffix[1:] or 'file',
            modified=datetime.fromtimestamp(stat.st_mtime),
            hash=file_hash
        )
        
    def _calculate_file_hash(self, path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
        
    def move_files(self, files: List[Union[str, Path]], target_dir: Union[str, Path], 
                   conflict_strategy: str = 'rename') -> Dict[str, str]:
        """Move files to target directory with enhanced conflict handling."""
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        moved_files = []
        
        try:
            for file in files:
                source = Path(file)
                if not source.exists():
                    self.logger.warning(f"Source file {source} does not exist")
                    results[str(source)] = 'not_found'
                    continue
                    
                target = target_dir / source.name
                final_path = self._handle_conflict(target, conflict_strategy)
                
                try:
                    source.rename(final_path)
                    moved_files.append((source, final_path))
                    results[str(source)] = str(final_path)
                    self.logger.info(f"Moved {source} to {final_path}")
                except Exception as e:
                    self.logger.error(f"Failed to move {source}: {e}")
                    results[str(source)] = 'failed'
                    self._rollback_moves(moved_files)
                    raise
                    
            # Log successful operation
            self._operation_history.append({
                'operation': 'move_files',
                'timestamp': datetime.now().isoformat(),
                'target_dir': str(target_dir),
                'files_moved': len(moved_files)
            })
            
            return results
            
        except Exception as e:
            self.logger.error(f"File move operation failed: {e}")
            raise
            
    def _handle_conflict(self, target: Path, strategy: str) -> Path:
        """Handle file naming conflicts based on strategy."""
        if not target.exists():
            return target
            
        if strategy == 'rename':
            stem = target.stem
            suffix = target.suffix
            counter = 1
            while target.exists():
                target = target.parent / f"{stem}_{counter}{suffix}"
                counter += 1
            return target
        elif strategy == 'overwrite':
            return target
        else:
            raise ValueError(f"Unknown conflict strategy: {strategy}")
            
    def _rollback_moves(self, moved_files: List[tuple[Path, Path]]) -> None:
        """Rollback moved files in case of failure."""
        for source, target in reversed(moved_files):
            try:
                target.rename(source)
            except Exception as e:
                self.logger.error(f"Rollback failed for {target} -> {source}: {e}")
                
    def get_directory_stats(self, path: Union[str, Path]) -> Dict:
        """Get statistics about a directory."""
        path = Path(path)
        total_size = 0
        file_count = 0
        dir_count = 0
        
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
                elif item.is_dir():
                    dir_count += 1
                    
            return {
                'total_size': total_size,
                'file_count': file_count,
                'dir_count': dir_count,
                'last_modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get directory stats for {path}: {e}")
            raise
            
    def cleanup_empty_dirs(self, path: Union[str, Path]) -> int:
        """Remove empty directories recursively."""
        path = Path(path)
        removed_count = 0
        
        try:
            for item in sorted(path.rglob('*'), reverse=True):
                if item.is_dir() and not any(item.iterdir()):
                    item.rmdir()
                    removed_count += 1
                    self.logger.info(f"Removed empty directory: {item}")
                    
            return removed_count
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            raise
            
    def create_archive(self, source_dir: Union[str, Path], archive_path: Union[str, Path]) -> None:
        """Create a ZIP archive of a directory."""
        source_dir = Path(source_dir)
        archive_path = Path(archive_path)
        
        try:
            shutil.make_archive(
                str(archive_path.with_suffix('')),
                'zip',
                str(source_dir)
            )
            self.logger.info(f"Created archive: {archive_path}")
        except Exception as e:
            self.logger.error(f"Archive creation failed: {e}")
            raise