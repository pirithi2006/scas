# ==========================================================
# 🧠 SMART CAMPUS DATA PREPARATION (ENHANCED)
# ==========================================================
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random, os

# Set seed for reproducibility
np.random.seed(42)
os.makedirs("data", exist_ok=True)

# ----------------------------------------------------------
# STUDENT PROFILE DATA (students.csv)
# ----------------------------------------------------------
departments = ["CSE", "ECE", "MECH", "CIVIL", "EEE", "BIO", "CHEM", "MATH"]
genders = ["Male", "Female"]
students = []

for i in range(1, 501):
    dept = random.choice(departments)
    year = random.randint(1, 4)
    gender = random.choice(genders)
    hostel_resident = random.choice(["Yes", "No"])
    attendance = np.round(np.random.uniform(50, 100), 2)
    avg_grade = np.round(np.random.uniform(4, 10), 2)
    assignments_submitted = random.randint(5, 10)
    extracurricular_score = np.round(np.random.uniform(0, 10), 2)
    avg_study_hours = np.round(np.random.uniform(1, 5), 2)
    attendance_trend = random.choice(["Improving", "Stable", "Declining"])

    # --- Additional realistic academic/lifestyle features ---
    parent_income = np.round(np.random.uniform(15000, 150000), 0)
    scholarship_status = random.choice(["Yes", "No"])
    library_visits_per_month = random.randint(0, 20)
    internet_usage_hours = np.round(np.random.uniform(0.5, 6), 2)
    sports_participation = random.choice(["Yes", "No"])
    sleep_hours = np.round(np.random.uniform(4, 9), 2)
    peer_interaction_score = np.round(np.random.uniform(0, 10), 2)
    counseling_sessions_attended = random.randint(0, 5)

    students.append([
        i, dept, year, gender, hostel_resident, attendance, avg_grade,
        assignments_submitted, extracurricular_score, avg_study_hours,
        attendance_trend, parent_income, scholarship_status,
        library_visits_per_month, internet_usage_hours, sports_participation,
        sleep_hours, peer_interaction_score, counseling_sessions_attended
    ])

students_df = pd.DataFrame(students, columns=[
    "student_id", "department", "year", "gender", "hostel_resident",
    "attendance_pct", "avg_grade", "assignments_submitted", "extracurricular_score",
    "avg_study_hours", "attendance_trend", "parent_income", "scholarship_status",
    "library_visits_per_month", "internet_usage_hours", "sports_participation",
    "sleep_hours", "peer_interaction_score", "counseling_sessions_attended"
])

students_df.to_csv("data/students.csv", index=False)
print("✅ students.csv created successfully")


# ----------------------------------------------------------
# SUBJECT-WISE PERFORMANCE DATA (students_subjects.csv)
# ----------------------------------------------------------

# Department-wise subject mapping
dept_subjects = {
    "CSE": ["Programming", "Data Structures", "DBMS", "Networks", "OS"],
    "ECE": ["Circuits", "Electronics", "Signals", "Communication", "Microprocessors"],
    "MECH": ["Thermodynamics", "Manufacturing", "Mechanics", "CAD", "Fluid Dynamics"],
    "CIVIL": ["Surveying", "Structures", "Concrete", "Hydraulics", "Construction"],
    "EEE": ["Machines", "Circuits", "Power Systems", "Control", "Measurements"],
    "BIO": ["Biology", "Genetics", "Biochemistry", "Microbiology", "Biotechnology"],
    "CHEM": ["Organic", "Inorganic", "Physical", "Analytical", "Industrial Chemistry"],
    "MATH": ["Algebra", "Calculus", "Statistics", "Probability", "Discrete Math"]
}

records = []

for _, row in students_df.iterrows():
    dept = row["department"]
    year = row["year"]
    subjects = dept_subjects[dept]

    for subj in subjects:
        # Generate random marks (no derived semester marks)
        m1 = np.round(np.random.uniform(40, 95), 2)
        m2 = np.round(np.random.uniform(40, 95), 2)
        m3 = np.round(np.random.uniform(40, 95), 2)
        model = np.round(np.random.uniform(45, 100), 2)
        practicals = np.round(np.random.uniform(50, 100), 2)

        records.append([
            row["student_id"], dept, year, subj,
            m1, m2, m3, model, practicals
        ])

subjects_df = pd.DataFrame(records, columns=[
    "student_id", "department", "year", "subject",
    "month1_marks", "month2_marks", "month3_marks",
    "model_marks", "practicals_marks"
])

subjects_df.to_csv("data/students_subjects.csv", index=False)
print("✅ students_subjects.csv created successfully")

# ----------------------------------------------------------
# 👨‍🏫 FACULTY DATA (Enhanced)
# ----------------------------------------------------------
faculty = []
for i in range(1, 101):
    dept = random.choice(departments)
    experience = random.randint(1, 30)
    age = random.randint(25, 65)
    gender = random.choice(["Male", "Female", "Other"])
    
    feedback_rating = np.round(np.random.uniform(2.5, 5.0), 2)
    publications = random.randint(0, 15)
    leaves_taken = random.randint(0, 10)
    sick_leaves = random.randint(0, leaves_taken)
    personal_leaves = leaves_taken - sick_leaves
    
    classes_handled = random.randint(5, 20)
    workload_hours = classes_handled * np.random.randint(1, 3)
    research_projects = random.randint(0, 5)
    
    courses_taught = random.randint(1, 6)
    avg_class_size = random.randint(20, 100)
    student_feedback_count = random.randint(50, 300)
    workshops_attended = random.randint(0, 5)
    certifications_obtained = random.randint(0, 3)
    awards_received = random.randint(0, 2)
    ongoing_grants = random.randint(0, 3)

    faculty.append([
        i, dept, age, gender, experience, feedback_rating, publications,
        leaves_taken, sick_leaves, personal_leaves,
        classes_handled, workload_hours, research_projects,
        courses_taught, avg_class_size, student_feedback_count,
        workshops_attended, certifications_obtained,
        awards_received, ongoing_grants
    ])

faculty_df = pd.DataFrame(faculty, columns=[
    "faculty_id", "department", "age", "gender", "experience_years",
    "feedback_rating", "publications", "leaves_taken", "sick_leaves",
    "personal_leaves", "classes_handled_per_week", "workload_hours",
    "research_projects", "courses_taught", "avg_class_size",
    "student_feedback_count", "workshops_attended",
    "certifications_obtained", "awards_received", "ongoing_grants"
])

faculty_df.to_csv("data/faculty.csv", index=False)
print("✅ Enhanced faculty_enhanced.csv created")

# ----------------------------------------------------------
# 💡 ENERGY DATA (Enhanced)
# ----------------------------------------------------------
buildings = ['Academic Block', 'Library', 'Hostel', 'Admin', 'Lab Block']
building_area = {'Academic Block': 3000, 'Library': 2000, 'Hostel': 5000, 'Admin': 1500, 'Lab Block': 2500}
floor_count = {'Academic Block': 3, 'Library': 2, 'Hostel': 4, 'Admin': 2, 'Lab Block': 3}
equipment_factor = {'Academic Block': 1.0, 'Library': 1.2, 'Hostel': 1.1, 'Admin': 0.9, 'Lab Block': 1.5}

dates = pd.date_range(start='2024-01-01', end='2025-04-30')
energy = []

for date in dates:
    weekday = date.weekday()
    is_holiday = 1 if weekday in [5, 6] else 0
    outside_temp = np.round(np.random.uniform(15, 35), 1)
    rainfall = np.round(np.random.uniform(0, 20), 1)
    
    for building in buildings:
        temp = np.round(np.random.uniform(20, 38), 1)
        humidity = np.round(np.random.uniform(30, 90), 1)
        occupancy = np.random.randint(10, 250)
        class_event_count = np.random.randint(0, 5)  # number of events/classes that day
        
        # Energy calculation with new factors
        energy_kwh = np.round(
            50 + 0.5*occupancy + 0.4*temp + 0.3*outside_temp + 0.2*humidity +
            0.05*class_event_count*50 +
            equipment_factor[building]*10 + np.random.uniform(-10, 10), 2
        )
        
        energy.append([
            date, building, energy_kwh, temp, humidity, occupancy,
            weekday, is_holiday, outside_temp, rainfall,
            building_area[building], floor_count[building],
            equipment_factor[building], class_event_count
        ])

energy_df = pd.DataFrame(energy, columns=[
    "date", "building", "energy_kwh", "temp_c", "humidity_pct",
    "occupancy_estimate", "weekday", "holiday_flag",
    "outside_temp_c", "rainfall_mm", "building_area_sqm",
    "floor_count", "equipment_factor", "class_event_count"
])

energy_df.to_csv("data/energy.csv", index=False)
print("✅ Enhanced energy dataset with additional fields created")

# ==========================================================
# 🏢 Enhanced Facility Logs with Extra Features
# ==========================================================
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --------------------------
# Base Facility Data
# --------------------------
facilities = ['Library', 'Gym', 'Computer Lab', 'Auditorium', 'Sports Complex']
facility_capacities = {'Library': 100, 'Gym': 50, 'Computer Lab': 200, 'Auditorium': 200, 'Sports Complex': 150}
facility_floors = {'Library': 1, 'Gym': 0, 'Computer Lab': 2, 'Auditorium': 1, 'Sports Complex': 0}
facility_zone = {'Library': 'Indoor', 'Gym': 'Indoor', 'Computer Lab': 'Indoor', 'Auditorium': 'Indoor', 'Sports Complex': 'Outdoor'}

# User types
user_types = ['Student', 'Staff', 'Visitor']

# Date range
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 10, 21)
date_range = pd.date_range(start=start_date, end=end_date)

# --------------------------
# Generate Logs
# --------------------------
logs = []
user_ids = np.arange(1, 501)
log_id = 1

for date in date_range:
    is_weekend = int(date.weekday() >= 5)
    day_of_week = date.strftime("%A")
    month = date.strftime("%B")
    
    for facility in facilities:
        capacity = facility_capacities[facility]
        floor = facility_floors[facility]
        zone = facility_zone[facility]

        # Number of users and crowding
        num_users_today = random.randint(max(5, int(capacity * 0.2)), capacity)
        avg_duration_today = round(random.uniform(1.0, 2.5), 2)
        crowding_index = round((num_users_today * avg_duration_today) / capacity, 2)
        special_event = np.random.choice([0, 1], p=[0.9, 0.1])
        temperature = round(np.random.uniform(20, 38), 1)

        sampled_users = np.random.choice(user_ids, size=num_users_today, replace=False)
        
        for user_id in sampled_users:
            duration = round(np.random.uniform(0.5, 3.5), 2)
            feedback = np.random.randint(1, 6)
            if is_weekend or crowding_index > 2.5:
                feedback = max(1, feedback - random.choice([0, 1]))
            
            # Assign random check-in time and derive day part
            check_in_hour = random.randint(7, 20)
            check_in_minute = random.randint(0, 59)
            check_in_time = datetime(date.year, date.month, date.day, check_in_hour, check_in_minute)
            check_out_time = check_in_time + timedelta(hours=duration)
            
            if check_in_hour < 12:
                day_part = 'Morning'
            elif check_in_hour < 17:
                day_part = 'Afternoon'
            else:
                day_part = 'Evening'
            
            user_type = random.choice(user_types)
            
            logs.append([
                log_id, user_id, facility, duration, feedback,
                date.strftime("%Y-%m-%d"), capacity, is_weekend,
                day_of_week, month, num_users_today, avg_duration_today,
                crowding_index, special_event, temperature,
                floor, zone, check_in_time.strftime("%H:%M"), check_out_time.strftime("%H:%M"),
                day_part, user_type
            ])
            log_id += 1

# --------------------------
# Create DataFrame & Save
# --------------------------
columns = [
    "log_id", "user_id", "facility_name", "duration_hr", "feedback_rating",
    "date", "facility_capacity", "is_weekend", "day_of_week", "month",
    "num_users_today", "avg_duration_today", "crowding_index", "special_event",
    "temperature", "floor", "zone", "check_in_time", "check_out_time",
    "day_part", "user_type"
]

facility_logs_df = pd.DataFrame(logs, columns=columns)
facility_logs_df.to_csv("data/facility_logs.csv", index=False)
print("✅ Enhanced facility_logs.csv with extra columns created successfully!")


# ----------------------------------------------------------
# 🍴 CANTEEN DATA (Enhanced + Time Slot + Footfall + Weather)
# ----------------------------------------------------------
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# -----------------------------
# Date range for the dataset
# -----------------------------
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 10, 21)
dates = pd.date_range(start=start_date, end=end_date)

# -----------------------------
# Fixed base prices (per item)
# -----------------------------
base_prices = {
    'Veg Rice': 50,
    'Chicken Rice': 80,
    'Idli': 25,
    'Dosa': 30,
    'Coffee': 20,
    'Tea': 15,
    'Juice': 35
}

# -----------------------------
# Menu items with categories
# -----------------------------
items = [
    ('Veg Rice', 'Meal'), ('Chicken Rice', 'Meal'),
    ('Idli', 'Snack'), ('Dosa', 'Snack'),
    ('Coffee', 'Beverage'), ('Tea', 'Beverage'), ('Juice', 'Beverage')
]

canteen = []

# -----------------------------
# Generate synthetic data
# -----------------------------
for date in dates:
    weekday = date.weekday()
    holiday_flag = 1 if weekday in [5, 6] else 0
    month = date.month

    # -----------------------------
    # Random daily contextual features
    # -----------------------------
    # Campus footfall: fewer on weekends or vacations
    base_footfall = np.random.randint(400, 800)
    if holiday_flag:
        base_footfall = int(base_footfall * np.random.uniform(0.4, 0.7))
    if month in [5, 12]:  # Assume May/Dec are vacation months
        base_footfall = int(base_footfall * np.random.uniform(0.5, 0.8))

    # Weather condition (affects beverages)
    weather_condition = random.choices(
        ['Sunny', 'Cloudy', 'Rainy'],
        weights=[0.6, 0.25, 0.15]
    )[0]
    temp = np.round(np.random.uniform(20, 35), 1)
    if weather_condition == 'Rainy':
        temp -= np.random.uniform(2, 4)

    # Special event (occasional spikes)
    special_event = random.choices(
        ['None', 'Sports Day', 'Cultural Fest', 'Tech Meet'],
        weights=[0.8, 0.07, 0.08, 0.05]
    )[0]

    # -----------------------------
    # Time slots (for meal segmentation)
    # -----------------------------
    time_slots = ['Breakfast', 'Lunch', 'Dinner']

    for slot in time_slots:
        for item_name, category in items:
            # Base quantity depends on time slot
            if slot == 'Breakfast' and item_name in ['Idli', 'Dosa', 'Coffee', 'Tea']:
                base_qty = np.random.randint(40, 120)
            elif slot == 'Lunch' and item_name in ['Veg Rice', 'Chicken Rice', 'Juice']:
                base_qty = np.random.randint(60, 150)
            elif slot == 'Dinner' and item_name in ['Veg Rice', 'Chicken Rice', 'Tea']:
                base_qty = np.random.randint(40, 100)
            else:
                base_qty = np.random.randint(10, 40)

            # Apply event boost
            if special_event != 'None':
                base_qty = int(base_qty * np.random.uniform(1.2, 1.6))

            # Temperature & weather effects
            if category == 'Beverage' and temp > 30 and weather_condition == 'Sunny':
                base_qty = int(base_qty * np.random.uniform(1.1, 1.3))
            elif category == 'Meal' and temp > 33:
                base_qty = int(base_qty * np.random.uniform(0.85, 0.95))
            elif category == 'Snack' and weather_condition == 'Rainy':
                base_qty = int(base_qty * np.random.uniform(1.1, 1.3))

            # Promotion flag (10% chance)
            promotion_flag = random.choices([0, 1], weights=[0.9, 0.1])[0]
            if promotion_flag:
                base_qty = int(base_qty * np.random.uniform(1.05, 1.25))

            # Footfall adjustment (more students → more demand)
            base_qty = int(base_qty * (base_footfall / 600) * np.random.uniform(0.9, 1.1))

            # Total revenue
            total_price = base_prices[item_name] * base_qty

            # Append record
            canteen.append([
                date, month, weekday, holiday_flag, special_event,
                time_slots.index(slot), slot, item_name, category,
                base_qty, total_price, temp, weather_condition,
                promotion_flag, base_footfall
            ])

# -----------------------------
# Create DataFrame
# -----------------------------
canteen_df = pd.DataFrame(canteen, columns=[
    "date", "month", "weekday", "holiday_flag", "special_event",
    "time_slot_code", "time_slot", "item", "category",
    "qty_sold", "price_inr", "temp_c", "weather_condition",
    "promotion_flag", "footfall"
])

# -----------------------------
# Add previous day quantity (lag feature)
# -----------------------------
canteen_df = canteen_df.sort_values(["item", "date"]).reset_index(drop=True)
canteen_df["previous_day_qty"] = (
    canteen_df.groupby("item")["qty_sold"].shift(1).bfill().astype(int)
)

# -----------------------------
# Save to CSV
# -----------------------------
canteen_df.to_csv("data/canteen.csv", index=False)
print("✅ Enhanced canteen.csv created successfully with realistic demand, weather, and time-slot effects!")


print("\n🎉 All ENHANCED datasets generated successfully in /data folder!")
