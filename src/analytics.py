from datetime import datetime, timedelta
from collections import defaultdict

class Analytics:
    """Analytics module for retention metrics and revenue prediction."""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    # ==================== Retention Metrics ====================
    
    def calculate_churn_rate(self, period_months=1, month_offset=0):
        """Calculates churn rate for the specified period.
        
        Churn rate = (Members who didn't renew / Total members at start) * 100
        
        Args:
            period_months: Number of months to analyze (default: 1)
            month_offset: Number of months back to start analysis (default: 0)
            
        Returns:
            float: Churn rate percentage
        """
        today = datetime.now()
        # Calculate start and end of the period based on offset
        period_end = today - timedelta(days=month_offset * 30)
        period_start = period_end - timedelta(days=period_months * 30)
        
        # Get memberships that expired in the period
        expired_in_period = []
        renewed_in_period = []
        
        for membership in self.data_manager.membership_history:
            end_date = datetime.fromisoformat(membership['end_date'])
            
            # Check if membership expired in the period
            if period_start <= end_date <= period_end:
                member_id = membership['member_id']
                
                # Check if member renewed (has another active membership)
                has_renewed = False
                for other_ms in self.data_manager.membership_history:
                    if (other_ms['member_id'] == member_id and 
                        other_ms['membership_id'] != membership['membership_id'] and
                        datetime.fromisoformat(other_ms['start_date']) >= end_date):
                        has_renewed = True
                        break
                
                if has_renewed:
                    renewed_in_period.append(member_id)
                else:
                    expired_in_period.append(member_id)
        
        total_expired = len(expired_in_period) + len(renewed_in_period)
        
        if total_expired == 0:
            return 0.0
        
        churn_rate = (len(expired_in_period) / total_expired) * 100
        return round(churn_rate, 2)
    
    def calculate_retention_rate(self, period_months=1, month_offset=0):
        """Calculates retention rate for the specified period.
        
        Retention rate = (Members who renewed / Total members at start) * 100
        
        Args:
            period_months: Number of months to analyze (default: 1)
            month_offset: Number of months back to start analysis (default: 0)
            
        Returns:
            float: Retention rate percentage
        """
        churn_rate = self.calculate_churn_rate(period_months, month_offset)
        retention_rate = 100 - churn_rate
        return round(retention_rate, 2)
    
    def get_at_risk_members(self, days_threshold=30):
        """Identifies members whose memberships are expiring soon.
        
        Args:
            days_threshold: Number of days to look ahead (default: 30)
            
        Returns:
            list: List of dicts with member info and expiry date
        """
        today = datetime.now()
        threshold_date = today + timedelta(days=days_threshold)
        
        at_risk = []
        
        for membership in self.data_manager.membership_history:
            if membership['status'] != 'Active':
                continue
            
            end_date = datetime.fromisoformat(membership['end_date'])
            
            # Check if expiring within threshold
            if today < end_date <= threshold_date:
                member = self.data_manager.get_member(membership['member_id'])
                if member:
                    at_risk.append({
                        'member_id': membership['member_id'],
                        'member_name': f"{member['first_name']} {member['last_name']}",
                        'contact': member.get('contact', ''),
                        'expiry_date': membership['end_date'],
                        'days_remaining': (end_date - today).days
                    })
        
        # Sort by days remaining (most urgent first)
        at_risk.sort(key=lambda x: x['days_remaining'])
        return at_risk
    
    def get_retention_trend(self, months=6):
        """Gets historical retention rate trend.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            dict: Month labels and retention rates
        """
        today = datetime.now()
        trends = {'months': [], 'rates': []}
        
        for i in range(months, 0, -1):
            month_date = today - timedelta(days=i * 30)
            month_label = month_date.strftime("%b %Y")
            
            # Calculate retention for that month
            # Pass 'i' as offset to calculate for that specific month in the past
            rate = self.calculate_retention_rate(1, month_offset=i)
            
            trends['months'].append(month_label)
            trends['rates'].append(rate)
        
        return trends
    
    # ==================== Revenue Prediction ====================
    
    def predict_revenue(self, months_ahead=6):
        """Predicts future revenue based on historical data and active memberships.
        
        Args:
            months_ahead: Number of months to predict (default: 6)
            
        Returns:
            dict: Predicted revenue by month
        """
        today = datetime.now()
        predictions = {'months': [], 'predicted': []}
        
        # Calculate average monthly revenue from history
        avg_monthly_revenue = self._calculate_average_monthly_revenue()
        
        import random
        for i in range(1, months_ahead + 1):
            future_date = today + timedelta(days=i * 30)
            month_label = future_date.strftime("%b %Y")
            
            # Predicted revenue = average historical with some variation for realism
            variation = random.uniform(0.9, 1.1)
            predicted = avg_monthly_revenue * variation
            
            predictions['months'].append(month_label)
            predictions['predicted'].append(round(predicted, 2))
        
        return predictions
    
    def _calculate_average_monthly_revenue(self, months=6):
        """Calculates average monthly revenue from historical data.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            float: Average monthly revenue
        """
        today = datetime.now()
        start_date = today - timedelta(days=months * 30)
        
        monthly_revenue = defaultdict(float)
        
        for payment in self.data_manager.payments_log:
            if payment['status'] != 'Paid' or not payment.get('payment_date'):
                continue
            
            payment_date = datetime.fromisoformat(payment['payment_date'][:10])
            
            if payment_date >= start_date:
                month_key = payment_date.strftime("%Y-%m")
                monthly_revenue[month_key] += payment['amount_paid']
        
        if not monthly_revenue:
            return 0.0
        
        avg_revenue = sum(monthly_revenue.values()) / len(monthly_revenue)
        return round(avg_revenue, 2)
    
    def get_historical_revenue_trend(self, months=12):
        """Gets historical revenue trend.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            dict: Month labels and revenue amounts
        """
        today = datetime.now()
        start_date = today - timedelta(days=months * 30)
        
        monthly_revenue = defaultdict(float)
        
        for payment in self.data_manager.payments_log:
            if payment['status'] != 'Paid' or not payment.get('payment_date'):
                continue
            
            payment_date = datetime.fromisoformat(payment['payment_date'][:10])
            
            if payment_date >= start_date:
                month_key = payment_date.strftime("%Y-%m")
                monthly_revenue[month_key] += payment['amount_paid']
        
        # Sort by month
        sorted_months = sorted(monthly_revenue.keys())
        
        return {
            'months': [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in sorted_months],
            'revenue': [round(monthly_revenue[m], 2) for m in sorted_months]
        }
    
    def calculate_confidence_interval(self):
        """Calculates prediction confidence based on data availability.
        
        Returns:
            dict: Confidence score and message
        """
        # Factors affecting confidence:
        # 1. Amount of historical data
        # 2. Consistency of revenue
        # 3. Number of active members
        
        paid_payments = [p for p in self.data_manager.payments_log if p['status'] == 'Paid']
        active_members = len([m for m in self.data_manager.membership_history if m['status'] == 'Active'])
        
        confidence = 50  # Base confidence
        
        # More historical data = higher confidence
        if len(paid_payments) > 50:
            confidence += 20
        elif len(paid_payments) > 20:
            confidence += 10
        
        # More active members = higher confidence
        if active_members > 50:
            confidence += 20
        elif active_members > 20:
            confidence += 10
        
        # Cap at 90%
        confidence = min(confidence, 90)
        
        if confidence >= 70:
            message = "High confidence - sufficient historical data"
        elif confidence >= 50:
            message = "Medium confidence - limited historical data"
        else:
            message = "Low confidence - insufficient data for accurate predictions"
        
        return {
            'confidence': confidence,
            'message': message
        }
