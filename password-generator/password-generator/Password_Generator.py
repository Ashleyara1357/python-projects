import secrets
import string
import random
import math
import datetime
import os
import sys

# Check if pyperclip is available
try:
    import pyperclip  # type: ignore # For copying to clipboard
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("Note: Clipboard functionality is unavailable. Install 'pyperclip' to enable it.")

# Minimum recommended password length
MIN_LENGTH = 8

def generate_password(length, use_uppercase=True, use_numbers=True, use_symbols=True):
    """
    Generates a secure password with at least one character from each selected set.
    :param length: Length of the password (int)
    :param use_uppercase: Include uppercase letters (bool)
    :param use_numbers: Include numbers (bool)
    :param use_symbols: Include symbols (bool)
    :return: Generated password (str)
    :raises ValueError: If no character sets are selected.
    """
    # Ensure minimum password length
    if length < MIN_LENGTH:
        print(f"Password length must be at least {MIN_LENGTH}. Setting length to {MIN_LENGTH}.")
        length = MIN_LENGTH
    
    # Define character sets
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase if use_uppercase else ''
    digits = string.digits if use_numbers else ''
    symbols = string.punctuation if use_symbols else ''
    
    # Combine character sets based on user preferences
    all_characters = lowercase_letters + uppercase_letters + digits + symbols
    
    # Ensure at least one character set is selected
    if not all_characters:
        raise ValueError("At least one character set (lowercase, uppercase, digits, symbols) must be selected.")
    
    # Ensure the password includes at least one character from each selected set
    password = []
    # Always include one lowercase letter
    password.append(secrets.choice(lowercase_letters))
    
    if use_uppercase:
        password.append(secrets.choice(uppercase_letters))
    if use_numbers:
        password.append(secrets.choice(digits))
    if use_symbols:
        password.append(secrets.choice(symbols))
    
    # Fill the rest of the password with random characters
    remaining_length = length - len(password)
    password.extend(secrets.choice(all_characters) for _ in range(remaining_length))
    
    # Shuffle the password to mix the required characters
    secrets.SystemRandom().shuffle(password)
    
    # Convert list to string
    return ''.join(password)

def evaluate_password_strength(password):
    """
    Evaluates the strength of a password based on various criteria.
    :param password: The password to evaluate (str)
    :return: Dictionary with strength score and feedback
    """
    score = 0
    feedback = []
    
    # Length-based score (up to 5 points)
    if len(password) >= 20:
        score += 5
        feedback.append("Excellent length")
    elif len(password) >= 16:
        score += 4
        feedback.append("Very good length")
    elif len(password) >= 12:
        score += 3
        feedback.append("Good length")
    elif len(password) >= 10:
        score += 2
        feedback.append("Moderate length")
    elif len(password) >= 8:
        score += 1
        feedback.append("Minimum acceptable length")
    else:
        feedback.append("Password too short")
    
    # Character set diversity (up to 4 points)
    if any(c in string.ascii_lowercase for c in password):
        score += 1
    else:
        feedback.append("Missing lowercase letters")
    
    if any(c in string.ascii_uppercase for c in password):
        score += 1
    else:
        feedback.append("Missing uppercase letters")
    
    if any(c in string.digits for c in password):
        score += 1
    else:
        feedback.append("Missing numbers")
    
    if any(c in string.punctuation for c in password):
        score += 1
    else:
        feedback.append("Missing special characters")
    
    # Calculate entropy (bits of entropy per character)
    char_set_size = 0
    if any(c in string.ascii_lowercase for c in password):
        char_set_size += 26
    if any(c in string.ascii_uppercase for c in password):
        char_set_size += 26
    if any(c in string.digits for c in password):
        char_set_size += 10
    if any(c in string.punctuation for c in password):
        char_set_size += len(string.punctuation)
    
    entropy = len(password) * math.log2(char_set_size) if char_set_size > 0 else 0
    
    # Entropy-based score (up to 5 points)
    if entropy >= 100:
        score += 5
        feedback.append(f"Very high entropy ({entropy:.1f} bits)")
    elif entropy >= 80:
        score += 4
        feedback.append(f"High entropy ({entropy:.1f} bits)")
    elif entropy >= 60:
        score += 3
        feedback.append(f"Good entropy ({entropy:.1f} bits)")
    elif entropy >= 40:
        score += 2
        feedback.append(f"Moderate entropy ({entropy:.1f} bits)")
    elif entropy > 0:
        score += 1
        feedback.append(f"Low entropy ({entropy:.1f} bits)")
    
    # Convert score to a descriptive rating
    max_score = 14  # Maximum possible score
    percentage = (score / max_score) * 100
    
    if percentage >= 90:
        strength = "Excellent"
        color = "\033[92m"  # Green
    elif percentage >= 70:
        strength = "Strong"
        color = "\033[92m"  # Green
    elif percentage >= 50:
        strength = "Moderate"
        color = "\033[93m"  # Yellow
    elif percentage >= 30:
        strength = "Weak"
        color = "\033[91m"  # Red
    else:
        strength = "Very Weak"
        color = "\033[91m"  # Red
    
    reset = "\033[0m"  # Reset color
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": percentage,
        "strength": strength,
        "color": color,
        "reset": reset,
        "feedback": feedback,
        "entropy": entropy
    }

def get_user_input():
    """
    Prompts the user for password criteria and validates input.
    :return: Dictionary containing user preferences
    """
    try:
        length = int(input("Enter the desired password length (minimum 8): "))
        use_uppercase = input("Include uppercase letters? (y/n): ").strip().lower() == 'y'
        use_numbers = input("Include numbers? (y/n): ").strip().lower() == 'y'
        use_symbols = input("Include symbols? (y/n): ").strip().lower() == 'y'
        num_passwords = int(input("How many passwords would you like to generate? "))
        
        return {
            'length': length,
            'use_uppercase': use_uppercase,
            'use_numbers': use_numbers,
            'use_symbols': use_symbols,
            'num_passwords': max(1, num_passwords)  # Ensure at least 1 password
        }
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return get_user_input()

def save_passwords_to_file(passwords, file_path=None):
    """
    Saves generated passwords to a file.
    :param passwords: List of passwords to save
    :param file_path: Optional file path. If None, creates a default name
    :return: Path to the saved file
    """
    if file_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"generated_passwords_{timestamp}.txt"
    
    # Create passwords directory if it doesn't exist
    passwords_dir = "passwords"
    if not os.path.exists(passwords_dir):
        os.makedirs(passwords_dir)
    
    full_path = os.path.join(passwords_dir, file_path)
    
    with open(full_path, "w") as file:
        file.write("===== SECURE PASSWORDS =====\n")
        file.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, password in enumerate(passwords, 1):
            file.write(f"Password {i}: {password}\n")
    
    return full_path

def display_strength_meter(strength):
    """
    Displays a visual strength meter based on password strength.
    :param strength: Dictionary containing strength information
    """
    meter_width = 30
    filled_width = int((strength["percentage"] / 100) * meter_width)
    empty_width = meter_width - filled_width
    
    meter = f"{strength['color']}{'█' * filled_width}{strength['reset']}{'░' * empty_width}"
    print(f"\nPassword Strength: {strength['color']}{strength['strength']}{strength['reset']} ({strength['score']}/{strength['max_score']})")
    print(f"[{meter}] {strength['percentage']:.1f}%")
    
    if strength["feedback"]:
        print("\nFeedback:")
        for item in strength["feedback"]:
            print(f"• {item}")

def main():
    """
    Main function to run the password generator.
    """
    print("🔒 Welcome to the Enhanced Secure Password Generator! 🔒")
    print("=======================================================")
    
    preferences = get_user_input()
    
    try:
        # Generate the requested number of passwords
        passwords = []
        for i in range(preferences['num_passwords']):
            password = generate_password(
                length=preferences['length'],
                use_uppercase=preferences['use_uppercase'],
                use_numbers=preferences['use_numbers'],
                use_symbols=preferences['use_symbols']
            )
            passwords.append(password)
        
        print("\n✅ Generated Passwords:")
        print("======================")
        
        for i, password in enumerate(passwords, 1):
            print(f"\nPassword {i}: {password}")
            
            # Evaluate and display password strength
            strength = evaluate_password_strength(password)
            display_strength_meter(strength)
            
            # Copy the first password to clipboard
            if i == 1 and CLIPBOARD_AVAILABLE:
                try:
                    pyperclip.copy(password)
                    print("\n📋 First password copied to clipboard!")
                except Exception:
                    print("\nNote: Could not copy to clipboard.")
        
        # Ask if user wants to save passwords to a file
        save_option = input("\nWould you like to save these passwords to a file? (y/n): ").strip().lower()
        if save_option == 'y':
            file_path = save_passwords_to_file(passwords)
            print(f"\n💾 Passwords saved to: {file_path}")
            
    except ValueError as e:
        print(f"❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n\nPassword generation cancelled.")

if __name__ == "__main__":
    main()