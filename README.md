# Donation and Volunteer Management Platform

This project is a Flask-based web application designed to handle donations, volunteer signups, admin task assignments, and includes payment gateway options for bKash and Nagad.

## Features

- **Donation Form:** Users can donate using multiple payment methods (Visa, bKash, Nagad).
- **Volunteer Signup/Login:** Volunteers can sign up with their skills and log in to view assigned tasks.
- **Admin Login:** Admin (username: `sowadrahman`, password: `projectlaal`) can log in, view volunteers, and assign tasks.
- **Task Management:** Admins can assign tasks to volunteers, which volunteers can view in their dashboard after login.
- **Payment Gateways:** Integration with bKash and Nagad for easy donation transactions.

## Technologies Used

- **Flask:** Backend framework
- **SQLite:** Database for storing donations, volunteers, admin, and tasks.
- **HTML/CSS/Bootstrap:** Frontend UI components
- **bKash & Nagad Gateway Integration:** For handling donations

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
Admin Access
Admin Username: sowadrahman
Admin Password: projectlaal
The admin can log in to the admin dashboard to manage volunteers and assign tasks.

Volunteer Access
Volunteers can sign up through the signup page, providing their skills.
After login, they can see their assigned tasks.
Donation Process
Users can donate through Visa, bKash, or Nagad.
Future improvements may include fully integrating the bKash and Nagad payment gateways.
Future Enhancements
Payment gateway integration for bKash and Nagad: Full integration with these services for seamless payments.
Enhanced task management: Assigning multiple tasks or setting deadlines for volunteers.

License
