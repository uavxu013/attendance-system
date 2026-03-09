# ระบบติดตามการเข้างาน (Attendance Tracking System)

ระบบติดตามการเข้างานพนักงานพร้อมแดชบอร์ดแสดงผลการเข้างานประจำวันและกราฟเปอร์เซ็นต์

## ฟีเจอร์หลัก

- 📊 **แดชบอร์ดสรุป** - แสดงสถิติการเข้างานวันนี้ สัปดาห์นี้ และเดือนนี้
- 📈 **กราฟเปอร์เซ็นต์** - แสดงสัดส่วนการเข้างานในรูปแบบ Pie Chart และ Bar Chart
- 👥 **รายละเอียดพนักงาน** - แสดงรายชื่อพนักงานที่เข้างานพร้อมเวลา
- 📋 **ประวัติการเข้างาน** - บันทึกข้อมูลย้อนหลัง 30 วัน
- 💾 **ฐานข้อมูล** - ใช้ SQLite สำหรับเก็บข้อมูลการเข้างาน

## โครงสร้างระบบ

### Backend (Python Flask)
- **app.py** - API server สำหรับจัดการข้อมูลพนักงานและการเข้างาน
- **SQLite Database** - ฐานข้อมูลสำหรับเก็บข้อมูลพนักงานและประวัติการเข้างาน

### Frontend (React.js)
- **React 18** - สร้าง UI แบบ Interactive
- **Chart.js & Recharts** - สำหรับสร้างกราฟ visualization
- **Axios** - สำหรับเรียก API

## การติดตั้งและรัน

### 1. ติดตั้ง Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
npm install
```

### 2. รัน Backend Server
```bash
python app.py
```
Server จะรันที่ http://localhost:5000

### 3. รัน Frontend
```bash
npm start
```
Frontend จะรันที่ http://localhost:3000

## API Endpoints

### พนักงาน
- `GET /api/employees` - ดึงข้อมูลพนักงานทั้งหมด
- `POST /api/employees` - เพิ่มพนักงานใหม่

### การเข้างาน
- `POST /api/attendance/check-in` - บันทึกเวลาเข้างาน
- `POST /api/attendance/check-out` - บันทึกเวลาออกงาน
- `GET /api/attendance/today` - ข้อมูลการเข้างานวันนี้
- `GET /api/attendance/history` - ประวัติการเข้างาน 30 วันล่าสุด

### แดชบอร์ด
- `GET /api/dashboard/stats` - สถิติสรุป (วันนี้/สัปดาห์/เดือน)

## โครงสร้างฐานข้อมูล

### Employees Table
- id (Primary Key)
- name (ชื่อพนักงาน)
- employee_id (รหัสพนักงาน - Unique)
- department (แผนก)
- created_at (วันที่สร้าง)

### Attendance Table
- id (Primary Key)
- employee_id (Foreign Key)
- check_in (เวลาเข้างาน)
- check_out (เวลาออกงาน)
- date (วันที่)
- status (สถานะ: present, absent, late)

## การใช้งาน

1. เริ่มต้นให้เพิ่มข้อมูลพนักงานผ่าน API `POST /api/employees`
2. พนักงานสามารถ check-in ผ่าน API `POST /api/attendance/check-in`
3. ดูแดชบอร์ดการเข้างานได้ที่ http://localhost:3000
4. ระบบจะแสดง:
   - จำนวนพนักงานที่มาทำงานวันนี้
   - เปอร์เซ็นต์การเข้างาน
   - กราฟแสดงสัดส่วนการเข้างาน
   - ประวัติการเข้างานย้อนหลัง

## การนำเข้าข้อมูลพนักงานจาก Excel

### 1. ติดตั้ง dependencies เพิ่มเติม
```bash
pip install openpyxl
```

### 2. สร้างไฟล์ Excel ตาม template
```bash
python import_employees.py --template
```
จะสร้างไฟล์ `Employee_List_Template.xlsx` สำหรับใช้เป็นตัวอย่าง

### 3. จัดเตรียมข้อมูลใน Excel
สร้างไฟล์ Excel ชื่อ `Employee_List.xlsx` ที่มีคอลัมน์:
- **name**: ชื่อพนักงาน
- **employee_id**: รหัสพนักงาน (ต้องไม่ซ้ำกัน)
- **department**: แผนกกิจการ

### 4. Import ข้อมูลเข้าฐานข้อมูล
```bash
python import_employees.py Employee_List.xlsx
```

### 5. ตรวจสอบข้อมูลที่ import แล้ว
```bash
python import_employees.py --show
```

### คำสั่งอื่นๆ
- `python import_employees.py --template` - สร้างไฟล์ตัวอย่าง
- `python import_employees.py --show` - แสดงพนักงานที่มีอยู่ในฐานข้อมูล
- `python import_employees.py <filename>` - import ข้อมูลจากไฟล์ Excel

**หมายเหตุ**: ระบบใช้ openpyxl ในการอ่านไฟล์ Excel ซึ่งเบากว่า pandas และไม่ต้องการ dependencies ซับซ้อน

## ตัวอย่างการเพิ่มพนักงาน

```bash
curl -X POST http://localhost:500pip0/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "name": "สมชาย ใจดี",
    "employee_id": "EMP001",
    "department": "IT"
  }'
```

## ตัวอย่างการ Check-in

```bash
curl -X POST http://localhost:5000/api/attendance/check-in \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001"
  }'
```

## หมายเหตุ

- ระบบจะสร้างฐานข้อมูล SQLite อัตโนมัติเมื่อรันครั้งแรก
- ข้อมูลการเข้างานจะถูกบันทึกตามวันที่จริง
- สามารถติดตั้งบน Server จริงได้โดยปรับ production settings
