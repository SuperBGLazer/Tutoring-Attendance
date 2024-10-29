# Tutoring Session Tracking Web Application
This project is a Flask-based web application to track tutoring sessions and student attendance. The application supports multiple courses (formerly referred to as "classes") and allows the tutor to manage students, track session times, and mark attendance. The application uses MySQL as the database, is containerized with Docker, and uses Flask-Migrate for database migrations.

## Features
Course Management: Create, edit, and delete courses.
Student Management: Add, edit, import students via CSV, and manage their course enrollments.
Session Management: Create tutoring sessions with start and end times, descriptions, and manage session details.
Attendance Tracking: Mark students present for each session and copy their names to the clipboard in a formatted list.
MySQL Database: The application stores data in a MySQL database.
Dockerized: The app and MySQL database run in Docker containers, managed by Docker Compose.
Database Migrations: Flask-Migrate is used for database migrations to keep the database schema updated.

## Prerequisites
Docker and Docker Compose
Python 3.9+ installed locally (for local development)

## Installation and Setup
1. Clone the repository
```bash
git clone https://github.com/your-username/tutoring-tracker.git
cd tutoring-tracker
```
2. Set up environment variables
Create a .env file in the project root and set the following variables:

```
SECRET_KEY=your_secret_key
DATABASE_URL=mysql+pymysql://user:password@db/attendance_db
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_DATABASE=attendance_db
```

3. Docker Setup
The project is Dockerized, so you need to have Docker and Docker Compose installed.

4. Build and Run the Application
To build the Docker images and run the containers:

```bash
docker-compose up --build
```

This will:

Build the Flask web application container.
Set up the MySQL database container.
Start the services and expose the Flask app on http://localhost:5000.
5. Run Database Migrations
Once the containers are up and running, apply the database migrations to create the necessary tables.

```bash
docker compose exec web flask db init
docker compose exec web flask db migrate -m "Initial migration"
docker compose exec web flask db upgrade
```

6. Access the Application
Open your web browser and navigate to:

`http://localhost:5000`
You will see the web interface where you can manage courses, students, and sessions.

## Usage

**Course Management**
Navigate to the Courses page from the navigation menu.
Click Add Course to create a new course.
You can also edit or delete existing courses from the course list.

**Student Management**
Navigate to the Students page from the navigation menu.
Click Add Student to manually add a new student. You can assign the student to multiple courses during this process.
You can also import students using a CSV file in the format:
```csv
John Doe,johndoe@example.com
Jane Smith,janesmith@example.com
```

From the students list, you can edit or delete individual students.

**Session Management**
Navigate to a course's View page to see the sessions associated with that course.
Click Create Session to create a new session. You can define the start and end times, as well as an optional description.
After creating a session, you will be able to mark the attendance of students enrolled in that course.

**Attendance Tracking**
From a session's View page, you can mark the attendance of students.
You can also copy the list of students who attended a session to the clipboard in a formatted list like:
`John Doe, Jane Smith, and Mark Brown`

## Development

**Running Locally**
If you want to run the application locally without Docker, follow these steps:

**Create a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set up a local MySQL instance (optional, if you're not using Docker).

**Run the application:**

```bash
export FLASK_APP=app.py
flask run
```

## Database Migrations
Anytime you make changes to the models, you need to generate and apply migrations.

**Generate migration scripts:**

```bash
flask db migrate -m "Describe your migration here"
```

**Apply the migrations:**

```bash
flask db upgrade
```

**Deployment**
For production deployment, you would want to:

Set `FLASK_ENV=production`
Disable debug mode in app.py.

## Troubleshooting

**Common Issues**
"Table doesn't exist" error: Make sure you have applied the database migrations using Flask-Migrate.
MySQL connection issues: Ensure your DATABASE_URL environment variable is correctly configured, and that the MySQL service is running properly.

## Contributions
Feel free to submit a pull request or open an issue if you have suggestions or encounter any bugs.

## License
This project is licensed under the MIT License.

