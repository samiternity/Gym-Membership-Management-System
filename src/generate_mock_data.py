import random
import datetime
from .data_manager import DataManager
from .utils import generate_unique_id, calculate_end_date, get_current_date_iso

def generate_mock_data():
    dm = DataManager()
    
    print("Generating mock data...")

    # 1. Trainers
    trainers = [
        {"first_name": "Alex", "last_name": "Johnson", "specialization": "Yoga", "fee": 50.0},
        {"first_name": "Sam", "last_name": "Smith", "specialization": "HIIT", "fee": 75.0},
        {"first_name": "Jordan", "last_name": "Lee", "specialization": "Strength", "fee": 60.0},
    ]
    
    dm.trainers_db = {}
    trainer_ids = []
    for t in trainers:
        tid = generate_unique_id("T")
        t["contact"] = f"555-01{random.randint(10, 99)}"
        t["status"] = "Active"
        dm.trainers_db[tid] = t
        trainer_ids.append(tid)
    print(f"Created {len(trainers)} trainers.")

    # 2. Members & Memberships
    first_names = ["John", "Jane", "Mike", "Emily", "Chris", "Sarah", "David", "Laura"]
    last_names = ["Doe", "Smith", "Brown", "Wilson", "Taylor", "Anderson", "Thomas", "Martinez"]
    
    dm.members_db = {}
    dm.membership_history = []
    dm.payments_log = []
    
    member_ids = []
    
    for i in range(50): # 50 Members
        mid = generate_unique_id("M")
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        
        member = {
            "first_name": fname,
            "last_name": lname,
            "contact": f"555-02{random.randint(10, 99)}",
            "join_date": get_current_date_iso()
        }
        dm.members_db[mid] = member
        member_ids.append(mid)
        
        # Membership
        plan_id = random.choice(list(dm.plans_db.keys()))
        plan = dm.plans_db[plan_id]
        
        has_trainer = random.choice([True, False])
        trainer_id = random.choice(trainer_ids) if has_trainer else None
        trainer_fee = dm.trainers_db[trainer_id]['fee'] if has_trainer else 0
        
        start_date = get_current_date_iso()
        end_date = calculate_end_date(start_date, plan['duration_days'])
        
        ms_id = generate_unique_id("MS")
        membership = {
            "membership_id": ms_id,
            "member_id": mid,
            "plan_id": plan_id,
            "assigned_trainer_id": trainer_id,
            "start_date": start_date,
            "end_date": end_date,
            "status": "Active"
        }
        dm.membership_history.append(membership)

        # Create historical memberships for this member to simulate retention/churn
        # Go back 6 months
        current_start = datetime.date.fromisoformat(start_date)
        
        # 80% chance to have a previous membership
        if random.random() < 0.8:
            # Previous membership ended just before current one (Renewal)
            prev_end = current_start - datetime.timedelta(days=1)
            prev_start = prev_end - datetime.timedelta(days=30) # 1 month duration
            
            prev_ms_id = generate_unique_id("MS")
            prev_membership = {
                "membership_id": prev_ms_id,
                "member_id": mid,
                "plan_id": plan_id,
                "assigned_trainer_id": trainer_id,
                "start_date": prev_start.isoformat(),
                "end_date": prev_end.isoformat(),
                "status": "Expired"
            }
            dm.membership_history.append(prev_membership)
            
            # 50% chance to have another one before that (Long term retention)
            if random.random() < 0.5:
                prev_end_2 = prev_start - datetime.timedelta(days=1)
                prev_start_2 = prev_end_2 - datetime.timedelta(days=30)
                
                prev_ms_id_2 = generate_unique_id("MS")
                prev_membership_2 = {
                    "membership_id": prev_ms_id_2,
                    "member_id": mid,
                    "plan_id": plan_id,
                    "assigned_trainer_id": trainer_id,
                    "start_date": prev_start_2.isoformat(),
                    "end_date": prev_end_2.isoformat(),
                    "status": "Expired"
                }
                dm.membership_history.append(prev_membership_2)
        
        # Create some churned members (members with expired membership but no active one)
        # We'll add extra members for this who are NOT in the active list above
    
    # Create Churned Members
    for i in range(15): # 15 Churned members
        mid = generate_unique_id("M")
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        
        member = {
            "first_name": fname,
            "last_name": lname,
            "contact": f"555-04{random.randint(10, 99)}",
            "join_date": (datetime.date.today() - datetime.timedelta(days=100)).isoformat()
        }
        dm.members_db[mid] = member
        
        # Expired membership 2 months ago
        end_date = datetime.date.today() - datetime.timedelta(days=random.randint(30, 90))
        start_date = end_date - datetime.timedelta(days=30)
        
        ms_id = generate_unique_id("MS")
        membership = {
            "membership_id": ms_id,
            "member_id": mid,
            "plan_id": random.choice(list(dm.plans_db.keys())),
            "assigned_trainer_id": None,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status": "Expired"
        }
        dm.membership_history.append(membership)
        amount = plan['base_price'] + trainer_fee
        is_paid = random.choice([True, True, False]) # Mostly paid
        
        pay_id = generate_unique_id("PAY")
        payment = {
            "payment_id": pay_id,
            "member_id": mid,
            "membership_id": ms_id,
            "amount_due": amount,
            "amount_paid": amount if is_paid else 0.0,
            "due_date": start_date.isoformat(),
            "payment_date": start_date.isoformat() if is_paid else None,
            "status": "Paid" if is_paid else "Unpaid"
        }
        dm.payments_log.append(payment)

    print(f"Created {len(dm.members_db)} members.")

    # 2b. Create historical payments (spread over last 6 months)
    today = datetime.date.today()
    for month_offset in range(1, 7):
        # Go back month by month
        payment_date = today - datetime.timedelta(days=30 * month_offset)
        payment_date_str = payment_date.isoformat()
        
        # Create 3-5 payments per month
        num_payments = random.randint(3, 5)
        for _ in range(num_payments):
            mid = random.choice(member_ids)
            plan_id = random.choice(list(dm.plans_db.keys()))
            plan = dm.plans_db[plan_id]
            
            has_trainer = random.choice([True, False])
            trainer_id = random.choice(trainer_ids) if has_trainer else None
            trainer_fee = dm.trainers_db[trainer_id]['fee'] if has_trainer else 0
            
            amount = plan['base_price'] + trainer_fee
            
            pay_id = generate_unique_id("PAY")
            payment = {
                "payment_id": pay_id,
                "member_id": mid,
                "membership_id": generate_unique_id("MS"),
                "amount_due": amount,
                "amount_paid": amount,
                "due_date": payment_date_str,
                "payment_date": payment_date_str,
                "status": "Paid"
            }
            dm.payments_log.append(payment)
    
    print(f"Created {len(dm.payments_log)} payment records.")

    # 3. Attendance
    dm.attendance_log = []
    
    # First, ensure we have some active check-ins (5-10 people currently in gym)
    num_active = random.randint(5, 10)
    for i in range(num_active):
        mid = random.choice(member_ids)
        # Check in sometime today
        hour_in = random.randint(6, 20)
        min_in = random.randint(0, 59)
        check_in = datetime.datetime(today.year, today.month, today.day, hour_in, min_in)
        
        log = {
            "log_id": generate_unique_id("A"),
            "member_id": mid,
            "check_in_time": check_in.isoformat(),
            "check_out_time": None,
            "duration_minutes": None
        }
        dm.attendance_log.append(log)
    
    # Then add historical attendance records
    for i in range(500): # 500 historical visits
        mid = random.choice(member_ids)
        # Random date in last 30 days
        days_ago = random.randint(0, 30)
        date = today - datetime.timedelta(days=days_ago)
        
        hour_in = random.randint(6, 20)
        min_in = random.randint(0, 59)
        check_in = datetime.datetime(date.year, date.month, date.day, hour_in, min_in)
        
        duration = random.randint(30, 120)
        check_out = check_in + datetime.timedelta(minutes=duration)
        
        log = {
            "log_id": generate_unique_id("A"),
            "member_id": mid,
            "check_in_time": check_in.isoformat(),
            "check_out_time": check_out.isoformat(),
            "duration_minutes": duration
        }
        dm.attendance_log.append(log)
        
    print(f"Created {len(dm.attendance_log)} attendance records ({num_active} currently active).")

    # 4. Visitors
    dm.visitors_log = []
    for i in range(10):
        vid = generate_unique_id("V")
        visitor = {
            "visitor_id": vid,
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "contact": f"555-03{random.randint(10, 99)}",
            "visit_date": get_current_date_iso(),
            "interested_in": random.choice(["Yoga", "Gym", "Cardio"]),
            "status": random.choice(["Follow-up", "Not Interested", "Joined"])
        }
        dm.visitors_log.append(visitor)
    print(f"Created {len(dm.visitors_log)} visitors.")

    dm.save_all_data()
    print("Mock data generation complete.")

if __name__ == "__main__":
    generate_mock_data()
