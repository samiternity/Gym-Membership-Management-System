from datetime import datetime, timedelta

class FreezeManager:
    """Handles membership freeze logic and calculations."""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def can_freeze(self, membership):
        """Checks if a membership is eligible for freezing.
        
        A membership can be frozen if:
        - It's currently Active
        - It has more than 1 month (30 days) remaining
        
        Args:
            membership: Membership dict
            
        Returns:
            tuple: (eligible: bool, message: str)
        """
        if membership['status'] != 'Active':
            return False, "Only active memberships can be frozen"
        
        # Check remaining duration
        today = datetime.now()
        end_date = datetime.fromisoformat(membership['end_date'])
        days_remaining = (end_date - today).days
        
        if days_remaining <= 30:
            return False, "Membership must have more than 30 days remaining to freeze"
        
        return True, "Membership is eligible for freezing"
    
    def calculate_new_end_date(self, membership, freeze_days):
        """Calculates the new end date after freeze.
        
        Args:
            membership: Membership dict
            freeze_days: Number of days to freeze
            
        Returns:
            str: New end date in ISO format
        """
        current_end_date = datetime.fromisoformat(membership['end_date'])
        new_end_date = current_end_date + timedelta(days=freeze_days)
        return new_end_date.strftime("%Y-%m-%d")
    
    def add_freeze(self, membership_id, freeze_start, freeze_end, reason, approved_by):
        """Records a freeze for a membership.
        
        Args:
            membership_id: ID of the membership
            freeze_start: Start date (ISO format)
            freeze_end: End date (ISO format)
            reason: Reason for freeze
            approved_by: Username who approved
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Find membership
        membership = None
        for ms in self.data_manager.membership_history:
            if ms['membership_id'] == membership_id:
                membership = ms
                break
        
        if not membership:
            return False, "Membership not found"
        
        # Check eligibility
        eligible, msg = self.can_freeze(membership)
        if not eligible:
            return False, msg
        
        # Calculate freeze duration
        start_date = datetime.fromisoformat(freeze_start)
        end_date = datetime.fromisoformat(freeze_end)
        freeze_days = (end_date - start_date).days
        
        if freeze_days <= 0:
            return False, "Invalid freeze period"
        
        # Initialize freeze_history if not exists
        if 'freeze_history' not in membership:
            membership['freeze_history'] = []
            membership['total_freeze_days'] = 0
        
        # Generate freeze ID
        freeze_id = f"F{len(membership['freeze_history']) + 1:03d}"
        
        # Create freeze record
        freeze_record = {
            "freeze_id": freeze_id,
            "freeze_start": freeze_start,
            "freeze_end": freeze_end,
            "reason": reason,
            "approved_by": approved_by,
            "freeze_days": freeze_days
        }
        
        # Add to history
        membership['freeze_history'].append(freeze_record)
        membership['total_freeze_days'] += freeze_days
        
        # Update end date
        new_end_date = self.calculate_new_end_date(membership, freeze_days)
        membership['end_date'] = new_end_date
        
        # Update status to Frozen if freeze is active now
        today = datetime.now()
        if start_date <= today <= end_date:
            membership['status'] = 'Frozen'
        
        # Save changes
        self.data_manager.save_data("membership_history.json")
        
        return True, f"Membership frozen successfully. New end date: {new_end_date}"
    
    def get_freeze_history(self, membership_id):
        """Gets all freezes for a membership.
        
        Args:
            membership_id: ID of the membership
            
        Returns:
            list: List of freeze records
        """
        for ms in self.data_manager.membership_history:
            if ms['membership_id'] == membership_id:
                return ms.get('freeze_history', [])
        return []
    
    def get_active_freeze(self, membership_id):
        """Checks if membership currently has an active freeze.
        
        Args:
            membership_id: ID of the membership
            
        Returns:
            dict or None: Active freeze record if exists
        """
        today = datetime.now()
        
        freeze_history = self.get_freeze_history(membership_id)
        
        for freeze in freeze_history:
            start = datetime.fromisoformat(freeze['freeze_start'])
            end = datetime.fromisoformat(freeze['freeze_end'])
            
            if start <= today <= end:
                return freeze
        
        return None
    
    def update_membership_statuses(self):
        """Updates all membership statuses based on freeze dates.
        
        This should be called periodically (e.g., on app start) to ensure
        statuses are current.
        """
        today = datetime.now()
        updated_count = 0
        
        for membership in self.data_manager.membership_history:
            if 'freeze_history' not in membership:
                continue
            
            # Check if currently in freeze period
            is_frozen = False
            for freeze in membership['freeze_history']:
                start = datetime.fromisoformat(freeze['freeze_start'])
                end = datetime.fromisoformat(freeze['freeze_end'])
                
                if start <= today <= end:
                    is_frozen = True
                    break
            
            # Update status
            if is_frozen and membership['status'] != 'Frozen':
                membership['status'] = 'Frozen'
                updated_count += 1
            elif not is_frozen and membership['status'] == 'Frozen':
                # Check if membership is still valid
                end_date = datetime.fromisoformat(membership['end_date'])
                if today <= end_date:
                    membership['status'] = 'Active'
                else:
                    membership['status'] = 'Expired'
                updated_count += 1
        
        if updated_count > 0:
            self.data_manager.save_data("membership_history.json")
        
        return updated_count
    
    def get_total_freeze_days(self, membership_id):
        """Gets total days a membership has been frozen.
        
        Args:
            membership_id: ID of the membership
            
        Returns:
            int: Total freeze days
        """
        for ms in self.data_manager.membership_history:
            if ms['membership_id'] == membership_id:
                return ms.get('total_freeze_days', 0)
        return 0
    def unfreeze_membership(self, membership_id):
        """Unfreezes a currently frozen membership.
        
        Args:
            membership_id: ID of the membership
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Find membership
        membership = None
        for ms in self.data_manager.membership_history:
            if ms['membership_id'] == membership_id:
                membership = ms
                break
        
        if not membership:
            return False, "Membership not found"
            
        if membership['status'] != 'Frozen':
            return False, "Membership is not currently frozen"
            
        # Find active freeze
        active_freeze = self.get_active_freeze(membership_id)
        if not active_freeze:
            # Inconsistent state, just set to Active
            membership['status'] = 'Active'
            self.data_manager.save_data("membership_history.json")
            return True, "Membership status corrected to Active"
            
        # Calculate actual freeze duration so far
        start_date = datetime.fromisoformat(active_freeze['freeze_start'])
        today = datetime.now()
        
        # Calculate actual freeze days (from start to yesterday)
        actual_freeze_days = (today - start_date).days
        if actual_freeze_days < 0:
            actual_freeze_days = 0
            
        original_freeze_days = active_freeze['freeze_days']
        diff_days = original_freeze_days - actual_freeze_days
        
        # Update freeze record
        # End date is yesterday (since today they are active)
        new_freeze_end = today - timedelta(days=1)
        # If freeze started today, end date is today (0 days freeze?)
        if new_freeze_end < start_date:
            new_freeze_end = start_date
            
        active_freeze['freeze_end'] = new_freeze_end.strftime("%Y-%m-%d")
        active_freeze['freeze_days'] = actual_freeze_days
        active_freeze['reason'] += " (Unfrozen early)"
        
        # Update total freeze days
        membership['total_freeze_days'] -= diff_days
        if membership['total_freeze_days'] < 0:
            membership['total_freeze_days'] = 0
        
        # Update membership end date (pull back by diff_days)
        # We extended the end date by original_freeze_days when freezing.
        # Now we realize we only needed actual_freeze_days.
        # So we subtract the difference.
        current_end = datetime.fromisoformat(membership['end_date'])
        new_end = current_end - timedelta(days=diff_days)
        membership['end_date'] = new_end.strftime("%Y-%m-%d")
        
        # Set status to Active
        membership['status'] = 'Active'
        
        self.data_manager.save_data("membership_history.json")
        return True, f"Membership unfrozen. New end date: {membership['end_date']}"
