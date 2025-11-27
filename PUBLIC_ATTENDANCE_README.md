# Public QR/Kiosk Attendance System

## 🎯 Overview

Hệ thống Public QR/Kiosk Attendance cho phép chấm công nhanh mà không cần đăng nhập user, thông qua 1 service token an toàn.

**Key Features**:
- ✅ Không cần JWT user authentication
- ✅ Bảo mật bằng service token
- ✅ Tái sử dụng business logic hiện có
- ✅ Không ảnh hưởng các API cũ
- ✅ Field masking (không lộ thông tin nhạy cảm)
- ✅ Multi-day leave support

---

## 📁 Project Structure

```
robis-erp-backend/
├── app/
│   ├── api/
│   │   ├── dependencies/
│   │   │   ├── auth.py (existing)
│   │   │   └── service_auth.py (NEW) ← Service token auth
│   │   └── v1/
│   │       ├── public_attendance.py (NEW) ← Public endpoints
│   │       ├── attendance.py (existing)
│   │       ├── hr.py (existing)
│   │       └── ...
│   ├── core/
│   │   └── config.py (MODIFIED) ← Add ATTEND_PUBLIC_TOKEN
│   ├── services/
│   │   ├── attendance_service.py (existing)
│   │   └── hr_service.py (existing)
│   ├── schemas/
│   │   ├── attendance.py (existing)
│   │   └── hr.py (MODIFIED) ← Add PublicEmployee
│   └── main.py (MODIFIED) ← Register public router
│
├── test_public_attendance.py (NEW) ← Test script
├── PUBLIC_QR_SETUP.md (NEW) ← Detailed guide
├── ENV_SETUP.md (NEW) ← Environment setup
├── QUICK_START.md (NEW) ← 5-min setup
├── IMPLEMENTATION_SUMMARY.md (NEW) ← Summary
├── DEPLOYMENT_CHECKLIST.md (NEW) ← Deployment
├── API_REFERENCE.md (NEW) ← API docs
├── FILES_CREATED.md (NEW) ← File list
└── PUBLIC_ATTENDANCE_README.md (NEW) ← This file
```

---

## 🚀 Quick Start

### 1. Backend Setup (1 min)

```bash
# Add to .env
ATTEND_PUBLIC_TOKEN=your-super-secret-random-token-here

# Generate token
openssl rand -hex 32

# Restart backend
docker restart robis-backend
```

### 2. Test Backend (1 min)

```bash
curl -i "http://localhost:8000/api/v1/public/employees?page=1&page_size=10" \
  -H "Authorization: Bearer your-super-secret-random-token-here"
```

### 3. Frontend Setup (1 min)

```bash
# Add to .env.local
NEXT_PUBLIC_ATTEND_TOKEN=your-super-secret-random-token-here

# Configure proxy in next.config.js or vite.config.js
```

### 4. Test Frontend (1 min)

```javascript
const response = await fetch('/api/public/employees?page=1&page_size=10');
const data = await response.json();
console.log(data);
```

---

## 📚 Documentation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **QUICK_START.md** | 5-minute setup | 5 min |
| **PUBLIC_QR_SETUP.md** | Detailed guide | 20 min |
| **ENV_SETUP.md** | Environment setup | 15 min |
| **API_REFERENCE.md** | API documentation | 20 min |
| **IMPLEMENTATION_SUMMARY.md** | Technical summary | 15 min |
| **DEPLOYMENT_CHECKLIST.md** | Deployment guide | 10 min |
| **FILES_CREATED.md** | File list | 5 min |

---

## 🔌 API Endpoints

### 1. Get Employees
```
GET /api/v1/public/employees?page=1&page_size=10&search=name
Authorization: Bearer <ATTEND_PUBLIC_TOKEN>
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "employee_code": "EMP0001",
      "full_name": "Nguyễn Văn A",
      "email": "a@company.com",
      "department_id": 1,
      "position_id": 1,
      "hire_date": "2025-01-01",
      "employment_status": "active"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

### 2. Check-In
```
POST /api/v1/public/attendance/check-in
Authorization: Bearer <ATTEND_PUBLIC_TOKEN>
Content-Type: application/json

{
  "employee_id": 123,
  "check_in": "09:05:00",
  "note": "Kẹt xe"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "employee_id": 123,
  "date": "2025-11-27",
  "check_in": "09:05:00",
  "status": "late",
  "late_minutes": 5,
  "created_at": "2025-11-27T09:05:00"
}
```

### 3. Check-Out
```
POST /api/v1/public/attendance/check-out
Authorization: Bearer <ATTEND_PUBLIC_TOKEN>
Content-Type: application/json

{
  "employee_id": 123,
  "check_out": "17:30:00"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "employee_id": 123,
  "date": "2025-11-27",
  "check_in": "09:05:00",
  "check_out": "17:30:00",
  "work_hours": 480,
  "overtime_minutes": 30
}
```

### 4. Leave Request
```
POST /api/v1/public/attendance/leave
Authorization: Bearer <ATTEND_PUBLIC_TOKEN>
Content-Type: application/json

{
  "employee_id": 123,
  "leave_type": "personal",
  "start_date": "2025-11-27",
  "end_date": "2025-11-28",
  "reason": "Việc riêng"
}
```

**Response** (201 Created):
```json
{
  "id": 2,
  "employee_id": 123,
  "date": "2025-11-27",
  "status": "leave",
  "leave_type": "personal"
}
```

---

## 🔐 Security

### Service Token
- **Type**: Random string (not JWT)
- **Length**: 32+ characters
- **Storage**: Environment variable (not hard-coded)
- **Rotation**: Monthly or on-demand

### Field Masking
- ✅ Returned: id, employee_code, full_name, email, department_id
- ❌ Not returned: salary, personal_info, bank_account

### Authentication
- No JWT user required
- Service token in `Authorization: Bearer <token>` header
- No impact on existing APIs

---

## 🧪 Testing

### Run Test Script
```bash
python test_public_attendance.py
```

**Tests**:
- Test 0: Health check
- Test 1: Get employees
- Test 2: Check-in
- Test 3: Check-out
- Test 4: Leave request
- Test 5: Token validation

### Manual Testing with cURL

```bash
# Get employees
curl -i "http://localhost:8000/api/v1/public/employees" \
  -H "Authorization: Bearer your-token"

# Check-in
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/check-in" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"employee_id":1,"check_in":"09:05:00"}'

# Check-out
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/check-out" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"employee_id":1,"check_out":"17:30:00"}'

# Leave
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/leave" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"employee_id":1,"leave_type":"personal","start_date":"2025-11-27","end_date":"2025-11-27"}'
```

---

## 📊 Implementation Details

### Files Created (3)
1. **app/api/dependencies/service_auth.py** (50 lines)
   - Service token authentication dependency
   - Validates token from Authorization header

2. **app/api/v1/public_attendance.py** (250 lines)
   - 4 public endpoints
   - Reuses existing services
   - Comprehensive error handling

3. **test_public_attendance.py** (350 lines)
   - 6 test cases
   - Colored output
   - Detailed logging

### Files Modified (3)
1. **app/core/config.py** (+1 line)
   - Add `ATTEND_PUBLIC_TOKEN` env var

2. **app/main.py** (+2 lines)
   - Import and register public router

3. **app/schemas/hr.py** (+5 lines)
   - Add `PublicEmployee` schema

### Documentation (7 files)
- PUBLIC_QR_SETUP.md (500 lines)
- ENV_SETUP.md (300 lines)
- QUICK_START.md (150 lines)
- IMPLEMENTATION_SUMMARY.md (400 lines)
- DEPLOYMENT_CHECKLIST.md (300 lines)
- API_REFERENCE.md (600 lines)
- FILES_CREATED.md (300 lines)

---

## ✅ Acceptance Criteria

- ✅ 4 API public endpoints return 2xx with valid token
- ✅ No JWT user required
- ✅ No impact on existing APIs
- ✅ Frontend works without login
- ✅ Rate limiting can be enabled
- ✅ Audit logging can be enabled

---

## 🔄 Integration with Frontend

### Proxy Configuration (Next.js)

```javascript
// next.config.js
module.exports = {
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: '/api/public/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_URL}/api/v1/public/:path*`,
          headers: [
            {
              key: 'Authorization',
              value: `Bearer ${process.env.NEXT_PUBLIC_ATTEND_TOKEN}`,
            },
          ],
        },
      ],
    };
  },
};
```

### Environment Variables (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ATTEND_TOKEN=your-super-secret-random-token-here
```

### Frontend Usage

```typescript
// Get employees
const response = await fetch('/api/public/employees?page=1&page_size=10');
const employees = await response.json();

// Check-in
await fetch('/api/public/attendance/check-in', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    employee_id: 123,
    check_in: '09:05:00',
    note: 'Kẹt xe',
  }),
});

// Check-out
await fetch('/api/public/attendance/check-out', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    employee_id: 123,
    check_out: '17:30:00',
  }),
});

// Leave
await fetch('/api/public/attendance/leave', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    employee_id: 123,
    leave_type: 'personal',
    start_date: '2025-11-27',
    end_date: '2025-11-27',
    reason: 'Việc riêng',
  }),
});
```

---

## 🚨 Troubleshooting

### 401 Unauthorized
- Check token in `.env` matches token sent
- Check no extra whitespace in token
- Check header format: `Authorization: Bearer <token>`

### 500 Service token not configured
- Add `ATTEND_PUBLIC_TOKEN` to `.env`
- Restart backend

### 400 Bad Request
- Check JSON format
- Check time format: `HH:MM:SS`
- Check date format: `YYYY-MM-DD`

---

## 📋 Deployment Steps

### 1. Pre-Deployment
- [ ] Review code changes
- [ ] Run test script
- [ ] Check documentation

### 2. Backend Deployment
- [ ] Add `ATTEND_PUBLIC_TOKEN` to `.env`
- [ ] Restart backend
- [ ] Test endpoints

### 3. Frontend Deployment
- [ ] Add `NEXT_PUBLIC_ATTEND_TOKEN` to `.env.local`
- [ ] Configure proxy
- [ ] Test endpoints

### 4. Post-Deployment
- [ ] Monitor logs
- [ ] Check error rate
- [ ] Verify all endpoints working

---

## 📞 Support

For questions or issues:
1. Check relevant documentation file
2. Run test script: `python test_public_attendance.py`
3. Check backend logs: `docker logs robis-backend`
4. Contact backend team

---

## 📈 Monitoring (Optional)

### Rate Limiting
```bash
pip install slowapi
```

### Audit Logging
```python
import logging

logger = logging.getLogger(__name__)

def log_public_request(employee_id: int, action: str, request: Request):
    logger.info(
        f"PUBLIC_ATTENDANCE | "
        f"employee_id={employee_id} | "
        f"action={action} | "
        f"ip={request.client.host} | "
        f"timestamp={datetime.utcnow()}"
    )
```

---

## 🎯 Next Steps

1. **Backend Team**: Set token, restart, test
2. **Frontend Team**: Configure proxy, test
3. **DevOps Team**: Setup monitoring, deploy
4. **QA Team**: Test all scenarios, sign off

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-27 | Initial implementation |

---

## 📄 License

Internal use only - Robis ERP

---

**Status**: ✅ Ready for Testing
**Last Updated**: 2025-11-27
**Maintained By**: Backend Team

