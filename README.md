# CareerTrack (Job Application Tracker)

## Purpose
CareerTrack is a web application designed to help users effectively manage and track their job applications. It provides tools to organize application details, monitor progress, and receive AI-powered assistance for interview preparation and career coaching.

## Functionalities

### 1. User Authentication
*   **Sign Up**: Users can create a new account.
*   **Login/Logout**: Secure access to user accounts.

### 2. Job Application Management
*   **Add Applications**: Specify details such as company, role, location, status (Wishlist, Applied, Interview, Rejected, Offer), applied date, job URL, and notes.
*   **View & Organize**: View a personalized list of job applications.
*   **Search, Filter, and Sort**: Find applications by company, role, or location. Filter by status and sort by date or company name.
*   **Application Details**: Comprehensive view of each job application.
*   **Edit/Delete**: Update or remove existing job applications.

### 3. Dashboard and Analytics
*   Interactive dashboard providing an overview of application activity.
*   Visualizes total applications and status breakdowns.
*   Calculates key metrics (interview rate, offer rate, rejection rate).
*   Highlights recent job applications for quick access.

### 4. AI-Powered Assistance
*   **AI Interview Insight**: Generates tailored interview preparation questions and tactical advice using AI, based on the company, role, and your notes.
*   **AI Career Coach Chat**: A personalized AI assistant to provide guidance and support related to your job search.

## Tech Stack
*   **Backend**: Django (Python) 6.0.2
*   **Database**: SQLite3
*   **AI Integration**: Groq API (`llama-3.3-70b-versatile` model)
*   **Environment Management**: `python-dotenv`
*   **Frontend**: Django templates, standard HTML/CSS/JavaScript

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd tracker
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   * Create a `.env` file in the root directory.
   * Add your secrets (e.g., `SECRET_KEY`, `GROQ_API_KEY`).
5. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
6. Run the local development server:
   ```bash
   python manage.py runserver
   ```
