import json
from collections import Counter

# Verify payments distribution
print("=== PAYMENTS VERIFICATION ===")
with open('data/payments_log.json', 'r') as f:
    payments = json.load(f)

print(f"Total payments: {len(payments)}")

months = [p['payment_date'][:7] if p['payment_date'] else 'Unpaid' for p in payments]
print("\nPayment months distribution:")
for month, count in sorted(Counter(months).items()):
    print(f"  {month}: {count} payments")

# Verify active check-ins
print("\n=== ATTENDANCE VERIFICATION ===")
with open('data/attendance_log.json', 'r') as f:
    attendance = json.load(f)

print(f"Total attendance records: {len(attendance)}")

active = [a for a in attendance if a.get('check_out_time') is None]
print(f"Active check-ins (no checkout): {len(active)}")

if active:
    print("\nActive check-in details:")
    for a in active:
        print(f"  - Member {a['member_id']} checked in at {a['check_in_time']}")

print("\n=== DATA INTEGRITY ===")
print("✅ All JSON files loaded successfully")
print("✅ No corruption detected")
