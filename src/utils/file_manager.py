# src/utils/file_manager.py
import os
import json
import csv
from typing import Dict, Any, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def _ensure_contract_dir(self, dao_name: str, contract_name: str) -> str:
        """Ensure the contract directory exists and return its path"""
        dir_path = os.path.join(self.base_dir, dao_name, contract_name)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def _get_all_fieldnames(self, data: List[Dict[str, Any]], existing_fieldnames: set = None) -> set:
        """Get all unique field names from the data"""
        fieldnames = existing_fieldnames or set()
        for item in data:
            fieldnames.update(item.keys())
        return fieldnames

    def save_contract_data(self, 
                          dao_name: str, 
                          contract_name: str, 
                          data_type: str, 
                          data: List[Dict[str, Any]],
                          append: bool = True) -> None:
        """
        Save contract data in both JSON and CSV formats
        Args:
            dao_name: Name of the DAO
            contract_name: Name of the contract
            data_type: Type of data being saved (e.g., 'events', 'abi')
            data: List of dictionaries containing the data
            append: Whether to append to existing files (True) or overwrite (False)
        """
        if not data:
            logger.warning(f"No data to save for {dao_name}/{contract_name}/{data_type}")
            return

        dir_path = self._ensure_contract_dir(dao_name, contract_name)
        
        # Handle JSON
        json_path = os.path.join(dir_path, f"{data_type}.json")
        try:
            existing_data = []
            if append and os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    try:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                    except json.JSONDecodeError:
                        logger.warning(f"Could not read existing JSON file: {json_path}")
                        existing_data = []
            
            final_data = existing_data + data
            
            with open(json_path, 'w') as f:
                json.dump(final_data, f, indent=2, default=str)
            logger.info(f"Saved JSON data to {json_path}")
            
        except Exception as e:
            logger.error(f"Error saving JSON data: {str(e)}")
            raise

        # Handle CSV
        csv_path = os.path.join(dir_path, f"{data_type}.csv")
        try:
            # Get existing fieldnames if file exists
            existing_fieldnames = set()
            if append and os.path.exists(csv_path):
                with open(csv_path, 'r', newline='') as f:
                    reader = csv.reader(f)
                    try:
                        existing_fieldnames = set(next(reader))
                    except StopIteration:
                        pass

            # Get all fieldnames (existing + new)
            all_fieldnames = sorted(self._get_all_fieldnames(data, existing_fieldnames))

            # Determine if we need to rewrite the whole file
            need_rewrite = append and existing_fieldnames and (set(all_fieldnames) != existing_fieldnames)

            if need_rewrite:
                # Read existing data
                existing_data = []
                with open(csv_path, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    existing_data = list(reader)
                
                # Write everything with new fieldnames
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=all_fieldnames)
                    writer.writeheader()
                    for row in existing_data:
                        writer.writerow({k: row.get(k, '') for k in all_fieldnames})
                    for row in data:
                        writer.writerow({k: str(row.get(k, '')) for k in all_fieldnames})
            else:
                # Simple append or new file
                mode = 'a' if append and os.path.exists(csv_path) else 'w'
                with open(csv_path, mode, newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=all_fieldnames)
                    if mode == 'w' or not append:
                        writer.writeheader()
                    for row in data:
                        writer.writerow({k: str(row.get(k, '')) for k in all_fieldnames})

            logger.info(f"{'Appended' if append else 'Saved'} CSV data to {csv_path}")

        except Exception as e:
            logger.error(f"Error saving CSV data: {str(e)}")
            raise