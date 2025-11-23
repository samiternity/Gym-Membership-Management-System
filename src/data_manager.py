import json
import os
from typing import Dict, List, Any

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.members_db: Dict[str, Dict] = {}
        self.trainers_db: Dict[str, Dict] = {}
        self.plans_db: Dict[str, Dict] = {}
        self.membership_history: List[Dict] = []
        self.payments_log: List[Dict] = []
        self.attendance_log: List[Dict] = []
        self.visitors_log: List[Dict] = []
        
        self.files = {
            "members.json": "members_db",
            "trainers.json": "trainers_db",
            "plans.json": "plans_db",
            "membership_history.json": "membership_history",
            "payments_log.json": "payments_log",
            "attendance_log.json": "attendance_log",
            "visitors_log.json": "visitors_log"
        }
        
        self.ensure_data_dir()
        self.load_all_data()

    def ensure_data_dir(self):
        """Ensures the data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def load_all_data(self):
        """Loads all data from JSON files."""
        for filename, attr_name in self.files.items():
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        setattr(self, attr_name, json.load(f))
                except json.JSONDecodeError:
                    print(f"Error decoding {filename}, initializing empty.")
                    self._initialize_empty(attr_name)
            else:
                self._initialize_empty(attr_name)
                self.save_data(filename) # Create the file

    def _initialize_empty(self, attr_name):
        """Initializes the attribute with an empty list or dict based on type."""
        if attr_name in ["members_db", "trainers_db", "plans_db"]:
            setattr(self, attr_name, {})
        else:
            setattr(self, attr_name, [])

    def save_all_data(self):
        """Saves all data to JSON files."""
        for filename in self.files.keys():
            self.save_data(filename)

    def save_data(self, filename):
        """Saves a specific data structure to its JSON file."""
        attr_name = self.files[filename]
        data = getattr(self, attr_name)
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def get_member(self, member_id):
        return self.members_db.get(member_id)

    def add_member(self, member_id, member_data):
        self.members_db[member_id] = member_data
        self.save_data("members.json")
    
    def get_plan(self, plan_id):
        return self.plans_db.get(plan_id)

    def get_trainer(self, trainer_id):
        return self.trainers_db.get(trainer_id)
