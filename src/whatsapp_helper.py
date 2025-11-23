import re
import webbrowser
import urllib.parse

def validate_phone_number(contact):
    """Validates phone number format.
    
    Valid formats:
    - +923001234567 (international with +)
    - 923001234567 (international without +)
    - 03001234567 (local Pakistani format)
    
    Args:
        contact: Phone number string
        
    Returns:
        tuple: (valid: bool, message: str)
    """
    if not contact:
        return False, "Phone number is required"
    
    # Remove spaces and dashes
    cleaned = contact.replace(" ", "").replace("-", "")
    
    # Check if it contains only digits and optional leading +
    if not re.match(r'^\+?\d+$', cleaned):
        return False, "Phone number must contain only digits (and optional + prefix)"
    
    # Remove + for length check
    digits_only = cleaned.replace("+", "")
    
    # Check minimum length (10 digits)
    if len(digits_only) < 10:
        return False, "Phone number must be at least 10 digits"
    
    # Check maximum length (15 digits - international standard)
    if len(digits_only) > 15:
        return False, "Phone number is too long (max 15 digits)"
    
    return True, "Valid phone number"


def format_phone_number_for_whatsapp(contact):
    """Formats phone number for WhatsApp Web.
    
    Args:
        contact: Phone number string
        
    Returns:
        str: Formatted phone number (international format without +)
    """
    if not contact:
        return ""
    
    # Remove spaces, dashes, and parentheses
    cleaned = contact.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Remove + if present
    cleaned = cleaned.replace("+", "")
    
    # If starts with 0 (local Pakistani format), replace with 92
    if cleaned.startswith("0"):
        cleaned = "92" + cleaned[1:]
    
    # If doesn't start with country code, assume Pakistan (92)
    if not cleaned.startswith("92"):
        cleaned = "92" + cleaned
    
    return cleaned


def open_whatsapp_chat(phone_number, message=""):
    """Opens WhatsApp Web chat in browser.
    
    Args:
        phone_number: Phone number to chat with
        message: Optional pre-filled message
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Validate phone number
        valid, validation_msg = validate_phone_number(phone_number)
        if not valid:
            return False, validation_msg
        
        # Format phone number for WhatsApp
        formatted_number = format_phone_number_for_whatsapp(phone_number)
        
        # URL encode the message
        encoded_message = urllib.parse.quote(message) if message else ""
        
        # Construct WhatsApp Web URL
        # Pattern: https://api.whatsapp.com/send/?phone={phone}&text={text}&type=phone_number&app_absent=0
        url = f"https://api.whatsapp.com/send/?phone={formatted_number}&text={encoded_message}&type=phone_number&app_absent=0"
        
        # Open in browser
        webbrowser.open(url)
        
        return True, "WhatsApp Web opened successfully"
    
    except Exception as e:
        return False, f"Failed to open WhatsApp: {str(e)}"


def get_payment_reminder_message(member_name, amount, due_date):
    """Generates payment reminder message template.
    
    Args:
        member_name: Name of the member
        amount: Amount due
        due_date: Due date string
        
    Returns:
        str: Formatted message
    """
    return (f"Hello {member_name}, this is a reminder that your payment of "
            f"PKR {amount} is due on {due_date}. Please clear your dues at "
            f"your earliest convenience. Thank you!")


def get_membership_expiry_message(member_name, expiry_date):
    """Generates membership expiry reminder message.
    
    Args:
        member_name: Name of the member
        expiry_date: Expiry date string
        
    Returns:
        str: Formatted message
    """
    return (f"Hi {member_name}, your gym membership expires on {expiry_date}. "
            f"Please renew to continue enjoying our services. Contact us for "
            f"renewal options!")
