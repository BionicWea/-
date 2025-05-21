import os
import sys
import random
from datetime import datetime, timedelta

# Add the project root to the sys.path to allow importing project modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.append(project_root)

from pymongo import MongoClient
from models.student import Student
from models.classroom import Classroom
from models.course import Course
from models.score import Score

# Placeholder for MongoDB connection string (replace with your actual connection string)
MONGO_URI = "mongodb://localhost:27017/student_management" # Replace 'student_management' with your database name

def get_standalone_db():
    """Gets a standalone MongoDB database connection."""
    client = MongoClient(MONGO_URI)
    # Assuming the database name is part of the MONGO_URI or use client.get_database('your_db_name')
    # For MONGO_URI like mongodb://host:port/dbname, get_default_database() works.
    # Adjust if your MONGO_URI doesn't specify a database.
    return client.get_default_database()


# Configuration (adjust as needed)
NUM_CLASSROOMS = 5
NUM_COURSES_PER_CLASSROOM = 4
NUM_STUDENTS_PER_CLASSROOM = 20
MIN_SCORE = 60
MAX_SCORE = 100

def generate_classrooms():
    """Generates mock classroom data as dictionaries."""
    classrooms = []
    for i in range(NUM_CLASSROOMS):
        classroom = {
            'classroom_id': f"C{i+1:03d}",
            'classroom_name': f"Class {i+1}",
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'is_deleted': False
        }
        classrooms.append(classroom)
    return classrooms

def generate_courses(classrooms):
    """Generates mock course data for given classrooms as dictionaries."""
    courses = []
    for classroom in classrooms:
        # Assuming classrooms is now a list of dictionaries
        classroom_id = classroom['classroom_id']
        classroom_name = classroom['classroom_name']
        for i in range(NUM_COURSES_PER_CLASSROOM):
            course = {
                'course_id': f"{classroom_id}-CRS{i+1:02d}",
                'course_name': f"{classroom_name} - Course {i+1}",
                'classroom_id': classroom_id,
                'teacher_name': f"Teacher {random.randint(1, 10)}",
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_deleted': False
            }
            courses.append(course)
    return courses

def generate_students(classrooms):
    """Generates mock student data for given classrooms as dictionaries."""
    students = []
    start_year = datetime.now().year - 4
    for classroom in classrooms:
        # Assuming classrooms is now a list of dictionaries
        classroom_id = classroom['classroom_id']
        for i in range(NUM_STUDENTS_PER_CLASSROOM):
            student = {
                'Sno': f"{classroom_id}-STU{i+1:03d}", # Mapping student_id to Sno
                'Sname': f"Student {classroom_id}-{i+1}",
                'entry_year': random.randint(start_year, datetime.now().year),
                'major': f"Major {random.randint(1, 5)}",
                'classroom_id': classroom_id,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_deleted': False
            }
            students.append(student)
    return students

def generate_scores(students, courses):
    """Generates mock score data for given students and courses as dictionaries."""
    scores = []
    # Create a mapping of classroom_id to courses in that classroom
    classroom_courses = {}
    for course in courses:
        # Assuming courses is now a list of dictionaries
        if course['classroom_id'] not in classroom_courses:
            classroom_courses[course['classroom_id']] = []
        classroom_courses[course['classroom_id']].append(course)

    for student in students:
        # Assuming students is now a list of dictionaries
        student_id = student['Sno'] # Use 'Sno' as per student dictionary structure
        # Get courses for the student's classroom
        courses_in_classroom = classroom_courses.get(student['classroom_id'], [])
        for course in courses_in_classroom:
            score_value = random.randint(MIN_SCORE, MAX_SCORE)
            score = {
                'student_id': student_id,
                'course_id': course['course_id'], # Use 'course_id' as per course dictionary structure
                'score': score_value,
                'exam_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_deleted': False
            }
            scores.append(score)
    return scores

def insert_data(db_connection, data_list):
    """Inserts a list of data objects into the database using PyMongo insert_many."""
    if not data_list:
        return
    
    # Determine collection name based on the keys present in the first dictionary


    first_item_keys = data_list[0].keys()
    collection_name = None

    # Map dictionary keys to collection name
    if 'classroom_id' in first_item_keys and 'classroom_name' in first_item_keys:
        collection_name = 'classrooms'
    elif 'course_id' in first_item_keys and 'course_name' in first_item_keys:
        collection_name = 'courses'
    elif 'Sno' in first_item_keys and 'Sname' in first_item_keys:
        collection_name = 'students'
    elif 'student_id' in first_item_keys and 'course_id' in first_item_keys and 'score' in first_item_keys:
        collection_name = 'scores'

    if not collection_name:
        print(f"Could not determine collection name from data keys: {first_item_keys}. Skipping insertion.")
        return

    try:
        # Use the provided db_connection object
        # Access collection dynamically
        result = db_connection[collection_name].insert_many(data_list)
        # Determine item_type for printing based on collection_name
        item_type_for_print = collection_name.rstrip('s') if collection_name.endswith('s') else collection_name
        print(f"Inserted {len(result.inserted_ids)} {item_type_for_print} records into '{collection_name}' collection.")

    except Exception as e:
        # Determine item_type for printing based on collection_name
        item_type_for_print = collection_name.rstrip('s') if collection_name.endswith('s') else collection_name if collection_name else 'unknown type'
        print(f"Error inserting {item_type_for_print} data: {e}")

if __name__ == "__main__":
    print("Connecting to database...")
    # Assuming db.py handles connection setup when imported
    # You might need to call a specific connect function here if required
    # Example: db.connect()
    
    print("Generating data...")
    classrooms = generate_classrooms()
    courses = generate_courses(classrooms)
    students = generate_students(classrooms)
    scores = generate_scores(students, courses)

    print("Inserting data...")
    # Note: The insert_data function is a placeholder.
    # You need to implement the actual database insertion logic
    # based on how your models and db object handle saving/inserting data.
    # For MongoDB with Flask-MongoEngine or PyMongo, this would involve
    # calling .save() on model instances or using collection.insert_many().
    
    # Get standalone database connection
    standalone_db = get_standalone_db()
    
    # Insert data using the updated function, passing the connection
    insert_data(standalone_db, classrooms)
    insert_data(standalone_db, courses)
    insert_data(standalone_db, students)
    insert_data(standalone_db, scores)
    
    # Close the connection when done
    standalone_db.client.close()
    
    print("Data generation script finished.")