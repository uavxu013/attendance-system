#!/usr/bin/env python3
"""
Script to import employee data from Excel file to database
"""

import pandas as pd
import sys
import os
from app import app, Employee, db

def import_employees_from_excel(excel_file_path):
    """Import employees from Excel file"""
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file_path)
        
        # Expected columns: name, employee_id, department
        required_columns = ['name', 'employee_id', 'department']
        
        # Check if required columns exist
        for col in required_columns:
            if col not in df.columns:
                print(f"❌ Error: Column '{col}' not found in Excel file")
                print(f"Required columns: {required_columns}")
                print(f"Found columns: {list(df.columns)}")
                return False
        
        with app.app_context():
            imported_count = 0
            skipped_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Check if employee already exists
                    existing_employee = Employee.query.filter_by(
                        employee_id=str(row['employee_id']).strip()
                    ).first()
                    
                    if existing_employee:
                        print(f"⚠️  Skipping existing employee: {row['name']} ({row['employee_id']})")
                        skipped_count += 1
                        continue
                    
                    # Create new employee
                    new_employee = Employee(
                        name=str(row['name']).strip(),
                        employee_id=str(row['employee_id']).strip(),
                        department=str(row['department']).strip() if pd.notna(row['department']) else ''
                    )
                    
                    db.session.add(new_employee)
                    imported_count += 1
                    print(f"✅ Imported: {row['name']} ({row['employee_id']}) - {row['department']}")
                    
                except Exception as e:
                    print(f"❌ Error importing row {index + 1}: {e}")
                    continue
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n" + "="*50)
            print(f"📊 Import Summary:")
            print(f"✅ Successfully imported: {imported_count} employees")
            print(f"⚠️  Skipped (already exists): {skipped_count} employees")
            print(f"📋 Total processed: {imported_count + skipped_count}")
            
            return True
            
    except FileNotFoundError:
        print(f"❌ Error: File '{excel_file_path}' not found")
        return False
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False

def show_current_employees():
    """Show current employees in database"""
    with app.app_context():
        employees = Employee.query.all()
        print(f"\n📋 Current employees in database ({len(employees)}):")
        for emp in employees:
            print(f"  - {emp.name} ({emp.employee_id}) - {emp.department}")

def create_sample_excel():
    """Create a sample Excel file template"""
    sample_data = {
        'name': ['สมชาย ใจดี', 'สมศรี รักดี', 'วิชัย มั่งคั่ง'],
        'employee_id': ['EMP001', 'EMP002', 'EMP003'],
        'department': ['IT', 'HR', 'Sales']
    }
    
    df = pd.DataFrame(sample_data)
    sample_file = 'Employee_List_Template.xlsx'
    df.to_excel(sample_file, index=False)
    print(f"✅ Sample template created: {sample_file}")
    print("You can use this template to create your employee list")

if __name__ == "__main__":
    print("🚀 Employee Import Tool")
    print("="*50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python import_employees.py <excel_file_path>    # Import from Excel")
        print("  python import_employees.py --show             # Show current employees")
        print("  python import_employees.py --template         # Create sample template")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == "--show":
        show_current_employees()
    elif arg == "--template":
        create_sample_excel()
    elif arg.endswith('.xlsx') or arg.endswith('.xls'):
        if os.path.exists(arg):
            import_employees_from_excel(arg)
        else:
            print(f"❌ File '{arg}' not found")
    else:
        print("❌ Invalid argument. Use --show, --template, or provide Excel file path")
