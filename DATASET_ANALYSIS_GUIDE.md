# Gym Membership System - Dataset & Analytics Guide

This guide explains how to generate a mock dataset, understanding its structure, and using it to verify the analytics module.

## 1. Generating Mock Data

We provide a script to generate realistic synthetic data for testing. All data is saved to a `mock_data` folder by default to avoid overwriting your actual production data.

### Command
```bash
python -m src.generate_mock_data
```

### Options
- `--output [dir]`: Specify output directory (default: `mock_data`).
- `--count [N]`: Number of members to generate (default: 100).

Example to overwrite real data (WARNING: IRREVERSIBLE):
```bash
python -m src.generate_mock_data --output data
```

## 2. Running Verification Analysis

The verification script runs the core analytics functions against the dataset and prints a report.

### Command
```bash
python -m src.verify_analytics --data-dir mock_data
```

## 3. Dataset Structure

The dataset consists of several JSON files linked by IDs.

### `members.json`
- **Key**: `member_id`
- **Fields**: Personal info, join date, current status.

### `plans.json`
- **Key**: `plan_id`
- **Fields**: Name, duration (months), price.

### `membership_history.json`
- List of all memberships (past and present).
- **Critical Fields**:
  - `member_id`: Link to member.
  - `start_date`, `end_date`: Defines the duration.
  - `status`: Active or Expired.

### `payments_log.json`
- List of all transactions.
- Used for calculating LTV and Revenue Trends.

## 4. Key Metrics Explained

- **churn_rate**: Percentage of members who expired in the period and did NOT renew.
- **retention_rate**: 100 - churn_rate.
- **ltv (Lifetime Value)**: Total Revenue / Total Members.
- **at_risk**: Active members expiring within 30 days.
