# 🐳 Docker Deployment Guide

## การใช้งาน Docker สำหรับ Attendance Tracking System

### 📋 ไฟล์ที่เกี่ยวข้อง
- `Dockerfile` - สร้าง container สำหรับแอปพลิเคชัน
- `docker-compose.yml` - จัดการ services (app + nginx)
- `nginx.conf` - ค่าตั้งค่า Nginx reverse proxy
- `.dockerignore` - ไฟล์ที่ไม่ต้องการ include ใน image

### 🚀 การติดตั้งและรัน

#### 1. ติดตั้ง Docker และ Docker Compose
```bash
# Windows/Mac: ดาวน์โหลดจาก docker.com
# Linux (Ubuntu/Debian):
sudo apt update
sudo apt install docker.io docker-compose
```

#### 2. Build และรันด้วย Docker Compose
```bash
# Build และรันทั้งหมด
docker-compose up --build

# หรือรันใน background
docker-compose up -d --build
```

#### 3. ตรวจสอบสถานะ
```bash
# ดูสถานะ containers
docker-compose ps

# ดู logs
docker-compose logs -f

# ตรวจสอบ health
curl http://localhost/health
```

### 🌐 การเข้าใช้งาน
- **Frontend**: http://localhost (ผ่าน Nginx)
- **Backend API**: http://localhost/api
- **Health Check**: http://localhost/health

### 📁 โครงสร้างใน Container

```
Container Structure:
├── /app/
│   ├── app.py              # Backend Flask application
│   ├── static/             # React frontend build
│   │   ├── index.html
│   │   ├── static/
│   │   │   ├── js/
│   │   │   ├── css/
│   │   │   └── media/
│   ├── attendance.db       # SQLite database
│   ├── init_data.py        # Sample data script
│   └── import_employees.py # Excel import script
└── /var/log/nginx/         # Nginx logs
```

### 🔄 การจัดการข้อมูล

#### 1. Import ข้อมูลพนักงาน
```bash
# คัดลอกไฟล์ Excel เข้า container
docker cp Employee_List.xlsx attendance-app:/app/

# รัน script import
docker exec attendance-app python import_employees.py Employee_List.xlsx

# ตรวจสอบข้อมูล
docker exec attendance-app python import_employees.py --show
```

#### 2. สร้างข้อมูลตัวอย่าง
```bash
docker exec attendance-app python init_data.py
```

#### 3. Backup ฐานข้อมูล
```bash
# คัดลอก database ออกจาก container
docker cp attendance-app:/app/attendance.db ./backup/
```

### ⚙️ การตั้งค่า Environment Variables

สร้างไฟล์ `.env`:
```bash
FLASK_ENV=production
DATABASE_URL=sqlite:///attendance.db
PORT=5000
```

แก้ไข `docker-compose.yml`:
```yaml
services:
  attendance-app:
    build: .
    env_file:
      - .env
    # ... rest of configuration
```

### 🔧 การแก้ไขปัญหา

#### 1. ดู logs แบบ real-time
```bash
docker-compose logs -f attendance-app
docker-compose logs -f nginx
```

#### 2. เข้าไปใน container
```bash
docker exec -it attendance-app bash
```

#### 3. Rebuild หลังแก้ไข code
```bash
docker-compose up --build --force-recreate
```

#### 4. ล้าง containers และ images
```bash
docker-compose down
docker system prune -a
```

### 📊 Monitoring

#### 1. ตรวจสอบ resource usage
```bash
docker stats
```

#### 2. Health check
```bash
curl -f http://localhost/health || echo "Service down"
```

### 🔒 การตั้งค่า Production

#### 1. เปลี่ยน port
แก้ไข `docker-compose.yml`:
```yaml
services:
  nginx:
    ports:
      - "8080:80"  # เปลี่ยนจาก 80 เป็น 8080
```

#### 2. เพิ่ม security
แก้ไข `nginx.conf`:
```nginx
# Add security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

### 🚀 การ Deploy บน Server

#### 1. บน Cloud Server (AWS, GCP, Azure)
```bash
# คัดลอกไฟล์ขึ้น server
scp -r . user@server:/path/to/app/

# รันบน server
cd /path/to/app
docker-compose up -d --build
```

#### 2. บน Raspberry Pi
```bash
# ใช้ ARM-based images
docker-compose -f docker-compose.arm.yml up -d --build
```

### 📝 คำสั่งที่ใช้บ่อย

```bash
# Build และรัน
docker-compose up -d --build

# ดู logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# ลบ volumes (ลบข้อมูล)
docker-compose down -v

# Update หลังแก้ไข code
docker-compose up -d --build --force-recreate
```

### 🎯 ประโยชน์ของการใช้ Docker

1. **Consistency** - ทำงานเหมือนกันทุกที่
2. **Portability** - ย้ายข้ามเครื่องง่าย
3. **Scalability** - ขยายได้ง่าย
4. **Isolation** - ไม่กระทบระบบอื่น
5. **Version Control** - จัดการ version ของแอปพลิเคชัน

🎉 **พร้อมใช้งาน!** รัน `docker-compose up -d --build` แล้วเข้า http://localhost
