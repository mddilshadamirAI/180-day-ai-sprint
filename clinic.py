
import hashlib

# --- Data Structures ---

class User:
    """A user of the system, can be a patient or a doctor."""
    def __init__(self, username, password, role, full_name, address=None):
        self.username = username
        self.password_hash = self._hash_password(password)
        self.role = role
        self.full_name = full_name
        self.address = address

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        return self.password_hash == self._hash_password(password)

# In-memory database of users (patients and doctors)
users = {
    "patient1": User("patient1", "pass1", "patient", "John Doe"),
    "patient2": User("patient2", "pass2", "patient", "Jane Smith"),
    "davis": User("davis", "docpass1", "doctor", "Dr. Davis"),
    "chen": User("chen", "docpass2", "doctor", "Dr. Chen"),
    "patel": User("patel", "docpass3", "doctor", "Dr. Patel"),
    "lee": User("lee", "docpass4", "doctor", "Dr. Lee"),
}

# Expanded database for doctors including specialty and location
doctors_db = {
    "Dr. Davis": {"specialty": "Cardiologist", "location": "New York"},
    "Dr. Chen": {"specialty": "Dermatologist", "location": "Los Angeles"},
    "Dr. Patel": {"specialty": "General Physician", "location": "New York"},
    "Dr. Lee": {"specialty": "Cardiologist", "location": "Los Angeles"},
    "Dr. Garcia": {"specialty": "Dermatologist", "address": "212 Derm Drive, Chicago"},
    "Dr. Smith": {"specialty": "General Physician", "address": "333 Health Highway, Chicago"},
    "Dr. Jones": {"specialty": "Cardiologist", "address": "444 Pulse Place, Houston"},
    "Dr. Williams": {"specialty": "General Physician", "address": "555 Vitality Ville, Houston"},
}

# Mapping of symptoms to specialties
symptom_to_specialty = {
    "Chest Pain": "Cardiologist",
    "High Blood Pressure": "Cardiologist",
    "Skin Rash": "Dermatologist",
    "Acne": "Dermatologist",
    "Fever": "General Physician",
    "Headache": "General Physician",
}

# Home treatment suggestions for common symptoms
home_treatments = {
    "Fever": "Rest, drink plenty of fluids (like water and broth), and consider over-the-counter medications like acetaminophen.",
    "Headache": "Rest in a quiet, dark room. A cold compress on your forehead and staying hydrated can help. Avoid screens.",
    "Skin Rash": "Keep the area clean and dry. Avoid scratching. A cool compress or an over-the-counter hydrocortisone cream may soothe it.",
    "Default": "For this symptom, it is highly recommended to consult a doctor for an accurate diagnosis."
}


# --- Workflows ---

def patient_workflow(user):
    """Handles the entire workflow for a patient."""
    print(f"\nWelcome, {user.full_name}! Let's find the right help for you.")
    
    symptoms_list = list(symptom_to_specialty.keys())
    for i, symptom in enumerate(symptoms_list, 1):
        print(f"{i}. {symptom}")
    
    try:
        choice = int(input("\nEnter the number for your symptom: "))
        if 1 <= choice <= len(symptoms_list):
            chosen_symptom = symptoms_list[choice - 1]
            specialty_needed = symptom_to_specialty[chosen_symptom]
            
            print(f"\nFor a symptom of '{chosen_symptom}', you should consult a {specialty_needed}.")

            # --- Home Treatment ---
            home_treat_choice = input("Would you like some home treatment advice first? (yes/no): ").lower()
            if home_treat_choice == 'yes':
                treatment = home_treatments.get(chosen_symptom, home_treatments["Default"])
                print(f"\nADVICE: {treatment}")

            # --- Find Nearest Doctor ---
            user.address = input("\nTo find the nearest specialist, please enter your city (e.g., New York, Los Angeles, Chicago, Houston): ")
            print(f"Searching for a {specialty_needed} in {user.address}...")

            recommended_doctors = [doc_name for doc_name, details in doctors_db.items() if details["specialty"] == specialty_needed and user.address.lower() in details.get("location", "").lower()]

            if recommended_doctors:
                print("\nHere are the available specialists in your city:")
                for doc in recommended_doctors:
                    print(f"- {doc}")
            else:
                print(f"\nUnfortunately, we could not find a {specialty_needed} in {user.address}. You may need to check in a nearby city.")

        else:
            print("Invalid selection. Please choose a number from the list.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def doctor_workflow(user):
    """Handles the workflow for a doctor."""
    doctor_details = next((details for name, details in doctors_db.items() if name == user.full_name), None)
    specialty = doctor_details['specialty'] if doctor_details else "N/A"
    
    print(f"\nWelcome, {user.full_name}. Your specialty is: {specialty}")
    
    print("1. View Patient Feedback")
    choice = input("Enter your choice: ")
    if choice == "1":
        try:
            with open("feedback.txt", "r") as f:
                print("\n--- Patient Feedback ---")
                print(f.read() or "The feedback file is empty.")
        except FileNotFoundError:
            print("No feedback file found.")

# --- Main Application ---

if __name__ == "__main__":
    while True:
        print("\n--- Welcome to the Advanced Clinic System ---")
        username = input("Enter username: ")
        password = input("Enter password: ")
        
        active_user = None
        if username in users:
            if users[username].check_password(password):
                active_user = users[username]
            else:
                print("Invalid password.")
        else:
            print(f"User '{username}' not found. Let's create a new patient account.")
            full_name = input("Enter your full name: ")
            new_user = User(username, password, "patient", full_name)
            users[username] = new_user
            active_user = new_user
            print(f"Patient account for '{full_name}' created successfully.")

        if active_user:
            print(f"\nLogin successful as {active_user.role.title()}")
            if active_user.role == "patient":
                patient_workflow(active_user)
            elif active_user.role == "doctor":
                doctor_workflow(active_user)
        
        another_session = input("\nStart another session? (yes/no): ").lower()
        if another_session != 'yes':
            print("Thank you for using the clinic system. Goodbye!")
            break
