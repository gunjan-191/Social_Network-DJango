# Social Networking API

This project is a Django-based social networking API with functionalities for user registration, friend requests, friend request management, and rate limiting.

## Features

- User Registration
- User Login
- Send, Accept, and Reject Friend Requests
- List Friends
- List Pending Friend Requests
- Rate Limiting: Send up to 3 friend requests per minute

## Prerequisites

- Python 3.12 or later
- Django 4.x or later
- Django REST Framework 3.14 or later
- MySQL or SQLite (based on your preference)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/social-networking-api.git
   cd social-networking-api

Install requirements:- 
pip install -r requirements.txt

Apply Migrations:-
python manage.py migrate

Create a Superuser (optional, for accessing the admin interface):-
python manage.py createsuperuser

Run the Development Server:-
python manage.py runserver

Access the API

Send Friend Request: POST /users/friend-request/send/
Accept Friend Request: PATCH /users/friend-request/accept/{request_id}/
Reject Friend Request: PATCH /users/friend-request/reject/{request_id}/
List Friends: GET /users/{user_id}/friends/
List Pending Friend Requests: GET /users/{user_id}/pending-requests/
