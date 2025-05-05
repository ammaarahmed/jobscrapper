from typing import List, Dict, Any, Optional
import csv
import json
from datetime import datetime
from pathlib import Path
import os

class Storage:
    """Handles storage of job data to various formats."""
    
    def __init__(self, output_dir: str = "data") -> None:
        """
        Initialize the storage handler.
        
        Args:
            output_dir: Directory to store output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_filename(self, prefix: str = "jobs") -> str:
        """Generate a filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}"
    
    def save_csv(self, jobs: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Save jobs to a CSV file.
        
        Args:
            jobs: List of job dictionaries
            filename: Optional custom filename
            
        Returns:
            str: Path to the saved file
        """
        if not jobs:
            raise ValueError("No jobs to save")
            
        filename = filename or self._get_filename()
        filepath = self.output_dir / f"{filename}.csv"
        
        # Get all possible fields from all jobs
        fieldnames = set()
        for job in jobs:
            fieldnames.update(job.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            writer.writerows(jobs)
            
        return str(filepath)
    
    def save_json(self, jobs: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Save jobs to a JSON file.
        
        Args:
            jobs: List of job dictionaries
            filename: Optional custom filename
            
        Returns:
            str: Path to the saved file
        """
        if not jobs:
            raise ValueError("No jobs to save")
            
        filename = filename or self._get_filename()
        filepath = self.output_dir / f"{filename}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
            
        return str(filepath)
    
    def save(self, jobs: List[Dict[str, Any]], format: str = "csv", filename: Optional[str] = None) -> str:
        """
        Save jobs to a file in the specified format.
        
        Args:
            jobs: List of job dictionaries
            format: Output format ("csv" or "json")
            filename: Optional custom filename
            
        Returns:
            str: Path to the saved file
        """
        if format.lower() == "csv":
            return self.save_csv(jobs, filename)
        elif format.lower() == "json":
            return self.save_json(jobs, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage:
if __name__ == "__main__":
    # Sample job data
    jobs = [
        {
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "salary": "$100k - $150k",
            "description": "Looking for a Python developer..."
        },
        {
            "title": "Senior Python Engineer",
            "company": "Startup Inc",
            "location": "New York, NY",
            "description": "Join our growing team..."
        }
    ]
    
    # Initialize storage
    storage = Storage()
    
    # Save to CSV
    csv_path = storage.save(jobs, format="csv")
    print(f"Saved to CSV: {csv_path}")
    
    # Save to JSON
    json_path = storage.save(jobs, format="json")
    print(f"Saved to JSON: {json_path}")
