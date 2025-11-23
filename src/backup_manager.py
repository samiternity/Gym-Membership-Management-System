import os
import json
import shutil
from datetime import datetime

class BackupManager:
    """Handles data backups and restoration."""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.backup_dir = os.path.join(data_dir, "backups")
        self.max_backups = 7  # Keep last 7 backups
        
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Ensures the backup directory exists."""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self):
        """Creates a timestamped backup of all JSON files.
        
        Returns:
            tuple: (success: bool, backup_name: str, message: str)
        """
        try:
            # Generate backup folder name with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = f"backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Create backup folder
            os.makedirs(backup_path)
            
            # Copy all JSON files from data directory
            files_backed_up = 0
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    source = os.path.join(self.data_dir, filename)
                    destination = os.path.join(backup_path, filename)
                    
                    # Validate JSON before backing up
                    if self.validate_json_file(source):
                        shutil.copy2(source, destination)
                        files_backed_up += 1
                    else:
                        print(f"Warning: Skipping invalid JSON file: {filename}")
            
            # Clean up old backups
            self.auto_cleanup_old_backups()
            
            return True, backup_name, f"Backup created successfully: {files_backed_up} files backed up"
        
        except Exception as e:
            return False, "", f"Backup failed: {str(e)}"
    
    def validate_json_file(self, filepath):
        """Validates that a file contains valid JSON.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            bool: True if valid JSON, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            return False
    
    def list_backups(self):
        """Lists all available backups with metadata.
        
        Returns:
            list: List of dicts with backup info (name, date, size, file_count)
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for backup_name in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if os.path.isdir(backup_path):
                # Get backup metadata
                file_count = len([f for f in os.listdir(backup_path) if f.endswith('.json')])
                
                # Calculate total size
                total_size = 0
                for filename in os.listdir(backup_path):
                    filepath = os.path.join(backup_path, filename)
                    if os.path.isfile(filepath):
                        total_size += os.path.getsize(filepath)
                
                # Extract date from backup name
                try:
                    date_str = backup_name.replace("backup_", "")
                    backup_date = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
                    formatted_date = backup_date.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    formatted_date = "Unknown"
                
                backups.append({
                    "name": backup_name,
                    "date": formatted_date,
                    "size_kb": round(total_size / 1024, 2),
                    "file_count": file_count,
                    "path": backup_path
                })
        
        # Sort by date (newest first)
        backups.sort(key=lambda x: x['date'], reverse=True)
        return backups
    
    def restore_backup(self, backup_name):
        """Restores data from a backup folder.
        
        Args:
            backup_name: Name of the backup to restore
            
        Returns:
            tuple: (success: bool, message: str)
        """
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            return False, "Backup not found"
        
        if not os.path.isdir(backup_path):
            return False, "Invalid backup (not a directory)"
        
        try:
            # Validate all JSON files in backup before restoring
            for filename in os.listdir(backup_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(backup_path, filename)
                    if not self.validate_json_file(filepath):
                        return False, f"Backup contains invalid JSON: {filename}"
            
            # Restore files
            files_restored = 0
            for filename in os.listdir(backup_path):
                if filename.endswith('.json'):
                    source = os.path.join(backup_path, filename)
                    destination = os.path.join(self.data_dir, filename)
                    shutil.copy2(source, destination)
                    files_restored += 1
            
            return True, f"Backup restored successfully: {files_restored} files restored"
        
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
    
    def delete_backup(self, backup_name):
        """Deletes a backup folder.
        
        Args:
            backup_name: Name of the backup to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            return False, "Backup not found"
        
        try:
            shutil.rmtree(backup_path)
            return True, "Backup deleted successfully"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    def auto_cleanup_old_backups(self):
        """Automatically deletes old backups, keeping only the last N backups."""
        backups = self.list_backups()
        
        if len(backups) > self.max_backups:
            # Delete oldest backups
            backups_to_delete = backups[self.max_backups:]
            for backup in backups_to_delete:
                self.delete_backup(backup['name'])
                print(f"Auto-deleted old backup: {backup['name']}")
    
    def validate_backup(self, backup_name):
        """Validates that a backup contains valid JSON files.
        
        Args:
            backup_name: Name of the backup to validate
            
        Returns:
            tuple: (valid: bool, message: str)
        """
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            return False, "Backup not found"
        
        if not os.path.isdir(backup_path):
            return False, "Invalid backup (not a directory)"
        
        json_files = [f for f in os.listdir(backup_path) if f.endswith('.json')]
        
        if not json_files:
            return False, "Backup contains no JSON files"
        
        # Validate each JSON file
        for filename in json_files:
            filepath = os.path.join(backup_path, filename)
            if not self.validate_json_file(filepath):
                return False, f"Invalid JSON file: {filename}"
        
        return True, f"Backup is valid ({len(json_files)} files)"
