from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
import sys

app = Flask(__name__)
CORS(app)

# Database configuration
database_path = os.path.join(os.getcwd(), 'attendance.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    check_in = db.Column(db.DateTime, nullable=False)
    check_out = db.Column(db.DateTime)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='present')  # present, absent, late
    
    employee = db.relationship('Employee', backref='attendances')

@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    try:
        return send_from_directory('static', 'index.html')
    except Exception as e:
        return jsonify({'error': 'Frontend not available', 'details': str(e)}), 404

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        return send_from_directory('static', filename)
    except Exception as e:
        return jsonify({'error': 'Static file not found', 'details': str(e)}), 404

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if db.engine.execute('SELECT 1').scalar() else 'disconnected'
    })

# Routes
@app.route('/api/employees', methods=['GET', 'POST'])
def employees():
    if request.method == 'POST':
        data = request.json
        new_employee = Employee(
            name=data['name'],
            employee_id=data['employee_id'],
            department=data.get('department', '')
        )
        db.session.add(new_employee)
        db.session.commit()
        return jsonify({'message': 'Employee created successfully'}), 201
    
    employees = Employee.query.all()
    return jsonify([{
        'id': emp.id,
        'name': emp.name,
        'employee_id': emp.employee_id,
        'department': emp.department
    } for emp in employees])

@app.route('/api/attendance/check-in', methods=['POST'])
def check_in():
    data = request.json
    employee = Employee.query.filter_by(employee_id=data['employee_id']).first()
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    today = date.today()
    existing_attendance = Attendance.query.filter_by(
        employee_id=employee.id, 
        date=today
    ).first()
    
    if existing_attendance:
        return jsonify({'error': 'Already checked in today'}), 400
    
    # Check time and determine status
    now = datetime.utcnow()
    current_time = now.time()
    
    # Convert to Thailand time (UTC+7)
    from datetime import timedelta
    thailand_time = now + timedelta(hours=7)
    th_time = thailand_time.time()
    
    # Define time ranges (Thailand time)
    on_time_start = datetime.strptime('07:00', '%H:%M').time()
    on_time_end = datetime.strptime('08:03', '%H:%M').time()
    
    status = 'late'  # default
    if on_time_start <= th_time <= on_time_end:
        status = 'present'
    
    attendance = Attendance(
        employee_id=employee.id,
        check_in=now,
        date=today,
        status=status
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify({
        'message': 'Check-in successful',
        'status': status,
        'check_in_time': thailand_time.strftime('%H:%M:%S')
    }), 200

@app.route('/api/attendance/check-out', methods=['POST'])
def check_out():
    data = request.json
    employee = Employee.query.filter_by(employee_id=data['employee_id']).first()
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    today = date.today()
    attendance = Attendance.query.filter_by(
        employee_id=employee.id, 
        date=today
    ).first()
    
    if not attendance:
        return jsonify({'error': 'No check-in record found'}), 404
    
    if attendance.check_out:
        return jsonify({'error': 'Already checked out'}), 400
    
    attendance.check_out = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Check-out successful'}), 200

@app.route('/api/attendance/today', methods=['GET'])
def today_attendance():
    today = date.today()
    
    # Get all employees
    total_employees = Employee.query.all()
    
    # Get today's attendance
    today_attendances = Attendance.query.filter_by(date=today).all()
    present_count = len([att for att in today_attendances if att.status == 'present'])
    late_count = len([att for att in today_attendances if att.status == 'late'])
    
    # Calculate percentage
    attendance_percentage = (len(today_attendances) / len(total_employees) * 100) if total_employees else 0
    
    # Get detailed attendance info
    attendance_details = []
    for attendance in today_attendances:
        # Convert to Thailand time for display
        from datetime import timedelta
        th_check_in = attendance.check_in + timedelta(hours=7)
        th_check_out = None
        if attendance.check_out:
            th_check_out = attendance.check_out + timedelta(hours=7)
        
        attendance_details.append({
            'employee_name': attendance.employee.name,
            'employee_id': attendance.employee.employee_id,
            'check_in': th_check_in.strftime('%H:%M:%S'),
            'check_out': th_check_out.strftime('%H:%M:%S') if th_check_out else None,
            'status': attendance.status
        })
    
    return jsonify({
        'date': today.strftime('%Y-%m-%d'),
        'total_employees': len(total_employees),
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': len(total_employees) - len(today_attendances),
        'attendance_percentage': round(attendance_percentage, 2),
        'attendance_details': attendance_details
    })

@app.route('/api/attendance/history', methods=['GET'])
def attendance_history():
    # Get last 30 days of attendance data
    from datetime import timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    history = []
    current_date = start_date
    
    while current_date <= end_date:
        total_employees = len(Employee.query.all())
        attendances = Attendance.query.filter_by(date=current_date).all()
        present_count = len([att for att in attendances if att.status == 'present'])
        late_count = len([att for att in attendances if att.status == 'late'])
        
        history.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'total_employees': total_employees,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': total_employees - len(attendances),
            'attendance_percentage': round((len(attendances) / total_employees * 100) if total_employees > 0 else 0, 2)
        })
        
        current_date += timedelta(days=1)
    
    return jsonify(history)

@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    today = date.today()
    
    # Today's stats
    total_employees = len(Employee.query.all())
    today_attendances = Attendance.query.filter_by(date=today).all()
    present_today = len([att for att in today_attendances if att.status == 'present'])
    
    # This week's stats
    from datetime import timedelta, datetime
    week_start = today - timedelta(days=today.weekday())
    week_attendances = Attendance.query.filter(
        Attendance.date >= week_start,
        Attendance.date <= today
    ).all()
    
    # This month's stats
    month_start = today.replace(day=1)
    month_attendances = Attendance.query.filter(
        Attendance.date >= month_start,
        Attendance.date <= today
    ).all()
    
    return jsonify({
        'today': {
            'present': present_today,
            'total': total_employees,
            'percentage': round((present_today / total_employees * 100) if total_employees > 0 else 0, 2)
        },
        'week': {
            'present': len(set(att.employee_id for att in week_attendances if att.status == 'present')),
            'total': total_employees,
            'percentage': round((len(set(att.employee_id for att in week_attendances if att.status == 'present')) / total_employees * 100) if total_employees > 0 else 0, 2)
        },
        'month': {
            'present': len(set(att.employee_id for att in month_attendances if att.status == 'present')),
            'total': total_employees,
            'percentage': round((len(set(att.employee_id for att in month_attendances if att.status == 'present')) / total_employees * 100) if total_employees > 0 else 0, 2)
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
