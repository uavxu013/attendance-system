#!/usr/bin/env python3
"""
Script to initialize sample data for testing the attendance system
"""

import requests
import json

BASE_URL = "http://192.168.1.117:5000/api"

# Sample employees
sample_employees = [
    {"name": "สมชาย ใจดี", "employee_id": "EMP001", "department": "IT"},
    {"name": "สมศรี รักดี", "employee_id": "EMP002", "department": "HR"},
    {"name": "วิชัย มั่งคั่ง", "employee_id": "EMP003", "department": "Sales"},
    {"name": "มานี แสนสุข", "employee_id": "EMP004", "department": "Marketing"},
    {"name": "ประสิทธิ์ โชคดี", "employee_id": "EMP005", "department": "IT"},
    {"name": "นฤมล สุขใจ", "employee_id": "EMP006", "department": "Finance"},
    {"name": "อนุชิต รุ่งเรือง", "employee_id": "EMP007", "department": "Operations"},
    {"name": "กิตติศักดิ์ มีชัย", "employee_id": "EMP008", "department": "Sales"},
    {"name": "สุนิสา ใจสว่าง", "employee_id": "EMP009", "department": "HR"},
    {"name": "ธีรพงษ์ กำลังใจ", "employee_id": "EMP010", "department": "IT"}
]

def create_employees():
    """Create sample employees"""
    print("Creating sample employees...")
    
    for employee in sample_employees:
        try:
            response = requests.post(f"{BASE_URL}/employees", json=employee)
            if response.status_code == 201:
                print(f"✅ Created: {employee['name']} ({employee['employee_id']})")
            elif response.status_code == 200:
                print(f"⚠️  Already exists: {employee['name']} ({employee['employee_id']})")
            else:
                print(f"❌ Error creating {employee['name']}: {response.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend server. Please run 'python app.py' first.")
            return False
    
    return True

def check_employees():
    """Check existing employees"""
    try:
        response = requests.get(f"{BASE_URL}/employees")
        if response.status_code == 200:
            employees = response.json()
            print(f"\n📋 Current employees ({len(employees)}):")
            for emp in employees:
                print(f"  - {emp['name']} ({emp['employee_id']}) - {emp['department']}")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server.")
        return False

if __name__ == "__main__":
    print("🚀 Initializing attendance system with sample data...\n")
    
    if create_employees():
        print("\n" + "="*50)
        check_employees()
        print("\n✅ Initialization complete!")
        print("\nNext steps:")
        print("1. Run 'python app.py' to start the backend server")
        print("2. Run 'npm start' to start the frontend")
        print("3. Visit http://localhost:3000 to see the dashboard")
    else:
        print("\n❌ Initialization failed. Please check if the backend server is running.")
