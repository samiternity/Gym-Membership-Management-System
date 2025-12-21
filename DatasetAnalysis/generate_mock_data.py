import json
import os
import random
from datetime import datetime, timedelta
import argparse

class MockDataGenerator:
    def __init__(self, output_dir="mock_data"):
        self.output_dir = output_dir
        self.members = {}
        self.membership_history = []
        self.payments_log = []
        self.plans = {}
        self.trainers = {}
        
        self.ensure_output_dir()

    def ensure_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_plans(self):
        self.plans = {
            "P001": {"plan_id": "P001", "name": "Standard", "duration_months": 1, "base_price": 50.0},
            "P002": {"plan_id": "P002", "name": "Premium", "duration_months": 3, "base_price": 135.0},
            "P003": {"plan_id": "P003", "name": "VIP", "duration_months": 12, "base_price": 500.0}
        }
        self.save_json("plans.json", self.plans)
        print(f"Generated {len(self.plans)} plans.")

    def generate_trainers(self):
        self.trainers = {
            "T001": {"trainer_id": "T001", "first_name": "John", "last_name": "Doe", "specialization": "Cardio", "contact": "+1234567890", "fee": 50.0, "status": "Active"},
            "T002": {"trainer_id": "T002", "first_name": "Jane", "last_name": "Smith", "specialization": "Strength", "contact": "+0987654321", "fee": 60.0, "status": "Active"}
        }
        self.save_json("trainers.json", self.trainers)

    def generate_members_and_history(self, count=100):
        first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

        start_date_base = datetime.now() - timedelta(days=730) # Start 2 years ago

        for i in range(1, count + 1):
            member_id = f"M{i:03d}"
            join_date = start_date_base + timedelta(days=random.randint(0, 600))
            
            member = {
                "member_id": member_id,
                "first_name": random.choice(first_names),
                "last_name": random.choice(last_names),
                "email": f"member{i}@example.com",
                "contact": f"+92300{i:07d}",
                "join_date": join_date.strftime("%Y-%m-%d"),
                "status": "Active" # Will update based on history
            }
            
            self.members[member_id] = member
            
            # Generate history for this member
            current_date = join_date
            is_active = False
            
            # Simulate a chain of memberships
            while current_date < datetime.now() + timedelta(days=30):
                plan_id = random.choice(list(self.plans.keys()))
                plan = self.plans[plan_id]
                
                # 80% chance to renew immediately, 10% gap, 10% churn (stop)
                rand_choice = random.random()
                if rand_choice > 0.9 and len(self.membership_history) > 0:
                    # Churn/Stop
                    break
                elif rand_choice > 0.8:
                    # Gap of 1-30 days
                    current_date += timedelta(days=random.randint(1, 30))
                
                start_date = current_date
                # Join trainer ID (20% chance)
                trainer_id = None
                if random.random() < 0.2:
                    trainer_id = random.choice(list(self.trainers.keys()))

                # Calculate total amount
                total_amount = plan['base_price']
                if trainer_id:
                    total_amount += self.trainers[trainer_id]['fee']

                start_date = current_date
                end_date = start_date + timedelta(days=plan['duration_months'] * 30)
                
                ms_id = f"MS{len(self.membership_history) + 1:04d}"
                
                # Determine Status
                status = "Active" if start_date <= datetime.now() <= end_date else "Expired"
                
                # Simulate Frozen Membership (5% chance if Active)
                freeze_history = []
                total_freeze_days = 0
                if status == "Active" and random.random() < 0.05:
                    status = "Frozen"
                    freeze_start = datetime.now() - timedelta(days=random.randint(1, 10))
                    freeze_days = 30
                    freeze_end = freeze_start + timedelta(days=freeze_days)
                    total_freeze_days = freeze_days
                    
                    freeze_history.append({
                        "freeze_id": f"F{random.randint(1000,9999)}",
                        "freeze_start": freeze_start.strftime("%Y-%m-%d"),
                        "freeze_end": freeze_end.strftime("%Y-%m-%d"),
                        "reason": "Vacation",
                        "approved_by": "admin",
                        "freeze_days": freeze_days
                    })
                    # Extend end date
                    end_date += timedelta(days=freeze_days)

                history_entry = {
                    "membership_id": ms_id,
                    "member_id": member_id,
                    "plan_id": plan_id,
                    "assigned_trainer_id": trainer_id,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "status": status,
                    "amount": total_amount,
                    "freeze_history": freeze_history,
                    "total_freeze_days": total_freeze_days
                }
                self.membership_history.append(history_entry)
                
                # Payment Generation
                payment_status = "Paid"
                amount_paid = total_amount
                
                # Randomized Payment Status
                rand_pay = random.random()
                if rand_pay > 0.95:
                    payment_status = "Unpaid"
                    amount_paid = 0.0
                elif rand_pay > 0.90:
                    payment_status = "Pending"
                    amount_paid = total_amount / 2
                
                self.payments_log.append({
                    "payment_id": f"PAY{len(self.payments_log) + 1:05d}",
                    "member_id": member_id,
                    "membership_id": ms_id,
                    "amount_due": total_amount,
                    "amount_paid": amount_paid,
                    "due_date": start_date.strftime("%Y-%m-%d"),
                    "payment_date": start_date.strftime("%Y-%m-%d %H:%M:%S") if payment_status != "Unpaid" else None,
                    "method": "Credit Card",
                    "status": payment_status
                })
                
                current_date = end_date
                if status in ["Active", "Frozen"]:
                    is_active = True
            
            self.members[member_id]["status"] = "Active" if is_active else "Inactive"

        self.save_json("members.json", self.members)
        self.save_json("membership_history.json", self.membership_history)
        self.save_json("payments_log.json", self.payments_log)
        
        # Generate Attendance Log
        self.attendance_log = []
        for member_id, member in self.members.items():
            if member['status'] == 'Active':
                # Generate 1-10 visits in the last 30 days
                num_visits = random.randint(1, 10)
                for _ in range(num_visits):
                    visit_date = datetime.now() - timedelta(days=random.randint(0, 30))
                    check_in = visit_date.replace(hour=random.randint(6, 20), minute=random.randint(0, 59))
                    
                    # 5% chance of currently active check-in (no checkout)
                    if random.random() < 0.05 and visit_date.date() == datetime.now().date():
                         self.attendance_log.append({
                            "log_id": f"A{len(self.attendance_log)+1:05d}",
                            "member_id": member_id,
                            "check_in_time": check_in.strftime("%Y-%m-%d %H:%M:%S"),
                            "check_out_time": None,
                            "duration_minutes": None
                        })
                    else:
                        duration = random.randint(30, 120)
                        check_out = check_in + timedelta(minutes=duration)
                        
                        self.attendance_log.append({
                            "log_id": f"A{len(self.attendance_log)+1:05d}",
                            "member_id": member_id,
                            "check_in_time": check_in.strftime("%Y-%m-%d %H:%M:%S"),
                            "check_out_time": check_out.strftime("%Y-%m-%d %H:%M:%S"),
                            "duration_minutes": duration
                        })
        # Guaranteed Active Check-ins (Today)
        active_members = [mid for mid, m in self.members.items() if m['status'] == 'Active']
        if active_members:
            # Pick 3-5 random active members to be currently in the gym
            current_visitors = random.sample(active_members, min(len(active_members), random.randint(3, 5)))
            
            for member_id in current_visitors:
                # Remove any existing checkout for today if generated above (to avoid duplicate/conflicting logs)
                # Simply append a new open session
                check_in = datetime.now() - timedelta(minutes=random.randint(10, 120))
                
                self.attendance_log.append({
                    "log_id": f"A{len(self.attendance_log)+1:05d}",
                    "member_id": member_id,
                    "check_in_time": check_in.strftime("%Y-%m-%d %H:%M:%S"),
                    "check_out_time": None,
                    "duration_minutes": None
                })
        
        self.save_json("attendance_log.json", self.attendance_log)

        # Generate Visitors Log
        self.visitors_log = []
        for i in range(1, 21): # 20 visitors
            self.visitors_log.append({
                "visitor_id": f"V{i:03d}",
                "first_name": f"Visitor{i}",
                "last_name": "Test",
                "contact": f"+92300{random.randint(1000000, 9999999)}",
                "visit_date": (datetime.now() - timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d"),
                "interested_in": random.choice(["Cardio", "Strength", "Yoga"]),
                "status": random.choice(["Follow-up", "Joined", "Not Interested"])
            })
        self.save_json("visitors_log.json", self.visitors_log)

        self.save_json("users.json", {})
        
        print(f"Generated {count} members, {len(self.membership_history)} membership records, {len(self.payments_log)} payments.")

    def save_json(self, filename, data):
        with open(os.path.join(self.output_dir, filename), 'w') as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate mock data for Gym Management System")
    parser.add_argument("--output", default="mock_data", help="Directory to save mock data")
    parser.add_argument("--count", type=int, default=100, help="Number of members to generate")
    args = parser.parse_args()
    
    generator = MockDataGenerator(args.output)
    generator.generate_plans()
    generator.generate_trainers()
    generator.generate_members_and_history(args.count)
