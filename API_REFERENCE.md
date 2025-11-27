# Public QR/Kiosk Attendance - API Reference

## Base URL
```
http://localhost:8000  (Development)
https://api.robis.com  (Production)
```

## Authentication

All public endpoints require service token in Authorization header:

```
Authorization: Bearer <ATTEND_PUBLIC_TOKEN>
```

**Example**:
```bash
curl -H "Authorization: Bearer your-super-secret-random-token-here" \
  http://localhost:8000/api/v1/public/employees
```

---

## Endpoints

### 1. GET /api/v1/public/employees

Lấy danh sách nhân viên để chọn từ QR kiosk.

#### Request

**Method**: GET

**URL**: `/api/v1/public/employees`

**Headers**:
```
Authorization: Bearer <ATTEND_PUBLIC_TOKEN>
Content-Type: application/json
```

**Query Parameters**:
| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| page | integer | 1 | - | Trang thứ mấy (bắt đầu từ 1) |
| page_size | integer | 10 | 100 | Số item trên trang |
| search | string | null | - | Tìm theo name, email, employee_code |

#### Response

**Status**: 200 OK

**Body**:
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
    },
    {
      "id": 2,
      "employee_code": "EMP0002",
      "full_name": "Trần Thị B",
      "email": "b@company.com",
      "department_id": 2,
      "position_id": 2,
      "hire_date": "2025-02-01",
      "employment_status": "active"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

#### Error Responses

**401 Unauthorized** (Missing or invalid token):
```json
{
  "detail": "Invalid or missing service token"
}
```

**500 Internal Server Error** (Token not configured):
```json
{
  "detail": "Service token not configured on server"
}
```

#### Examples

**cURL**:
```bash
curl -i "http://localhost:8000/api/v1/public/employees?page=1&page_size=10&search=Nguyễn" \
  -H "Authorization: Bearer your-token"
```

**JavaScript/Fetch**:
```javascript
const response = await fetch('/api/public/employees?page=1&page_size=10', {
  headers: {
    'Authorization': 'Bearer your-token'
  }
});
const data = await response.json();
```

**Python/Requests**:
```python
import requests

headers = {
    'Authorization': 'Bearer your-token'
}
response = requests.get(
    'http://localhost:8000/api/v1/public/employees',
    params={'page': 1, 'page_size': 10},
    headers=headers
)
data = response.json()
```

---

### 2. POST /api/v1/public/attendance/check-in

Chấm công vào (QR/Kiosk).

Auto-calculate `late_minutes` nếu `check_in > 09:00`.

#### Request

**Method**: POST

**URL**: `/api/v1/public/attendance/check-in`

**Headers**:
```
Authorization: Bearer <ATTEND_PUBLIC_TOKEN>
Content-Type: application/json
```

**Body**:
```json
{
  "employee_id": 123,
  "check_in": "09:05:00",
  "note": "Kẹt xe"
}
```

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| employee_id | integer | ✅ | ID nhân viên |
| check_in | string (HH:MM:SS) | ✅ | Giờ chấm công vào |
| note | string | ❌ | Ghi chú (max 500 ký tự) |

#### Response

**Status**: 201 Created

**Body**:
```json
{
  "id": 1,
  "employee_id": 123,
  "date": "2025-11-27",
  "check_in": "09:05:00",
  "check_out": null,
  "status": "late",
  "late_minutes": 5,
  "overtime_minutes": 0,
  "work_hours": 0,
  "leave_type": null,
  "approved_by": null,
  "approved_at": null,
  "note": "Kẹt xe",
  "created_at": "2025-11-27T09:05:00",
  "updated_at": null
}
```

#### Error Responses

**400 Bad Request** (Employee already checked in):
```json
{
  "detail": "Employee đã check-in hôm nay rồi!"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Invalid or missing service token"
}
```

#### Examples

**cURL**:
```bash
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/check-in" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "employee_id": 123,
    "check_in": "09:05:00",
    "note": "Kẹt xe"
  }'
```

**JavaScript/Fetch**:
```javascript
const response = await fetch('/api/public/attendance/check-in', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-token'
  },
  body: JSON.stringify({
    employee_id: 123,
    check_in: '09:05:00',
    note: 'Kẹt xe'
  })
});
const data = await response.json();
```

---

### 3. POST /api/v1/public/attendance/check-out

Chấm công ra (QR/Kiosk).

Auto-calculate `overtime_minutes` và `work_hours`.

#### Request

**Method**: POST

**URL**: `/api/v1/public/attendance/check-out`

**Headers**:
```
Authorization: Bearer <ATTEND_PUBLIC_TOKEN>
Content-Type: application/json
```

**Body**:
```json
{
  "employee_id": 123,
  "check_out": "17:30:00",
  "note": "Đi sớm"
}
```

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| employee_id | integer | ✅ | ID nhân viên |
| check_out | string (HH:MM:SS) | ✅ | Giờ chấm công ra |
| note | string | ❌ | Ghi chú (max 500 ký tự) |

#### Response

**Status**: 200 OK

**Body**:
```json
{
  "id": 1,
  "employee_id": 123,
  "date": "2025-11-27",
  "check_in": "09:05:00",
  "check_out": "17:30:00",
  "status": "late",
  "late_minutes": 5,
  "overtime_minutes": 30,
  "work_hours": 480,
  "leave_type": null,
  "approved_by": null,
  "approved_at": null,
  "note": "Kẹt xe | Đi sớm",
  "created_at": "2025-11-27T09:05:00",
  "updated_at": "2025-11-27T17:30:00"
}
```

#### Error Responses

**400 Bad Request** (Employee not checked in):
```json
{
  "detail": "Employee chưa check-in hôm nay!"
}
```

**400 Bad Request** (Already checked out):
```json
{
  "detail": "Employee đã check-out rồi!"
}
```

#### Examples

**cURL**:
```bash
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/check-out" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "employee_id": 123,
    "check_out": "17:30:00"
  }'
```

---

### 4. POST /api/v1/public/attendance/leave

Đăng ký nghỉ phép (QR/Kiosk).

Hỗ trợ multi-day leave (tự động tạo record cho từng ngày).

#### Request

**Method**: POST

**URL**: `/api/v1/public/attendance/leave`

**Headers**:
```
Authorization: Bearer <ATTEND_PUBLIC_TOKEN>
Content-Type: application/json
```

**Body**:
```json
{
  "employee_id": 123,
  "leave_type": "personal",
  "start_date": "2025-11-27",
  "end_date": "2025-11-28",
  "reason": "Việc riêng"
}
```

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| employee_id | integer | ✅ | ID nhân viên |
| leave_type | string | ✅ | Loại nghỉ: annual, sick, personal, maternity, unpaid |
| start_date | string (YYYY-MM-DD) | ✅ | Ngày bắt đầu |
| end_date | string (YYYY-MM-DD) | ✅ | Ngày kết thúc |
| reason | string | ❌ | Lý do (max 500 ký tự) |
| note | string | ❌ | Ghi chú (max 500 ký tự) |

#### Response

**Status**: 201 Created

**Body** (trả về record ngày đầu tiên):
```json
{
  "id": 2,
  "employee_id": 123,
  "date": "2025-11-27",
  "check_in": null,
  "check_out": null,
  "status": "leave",
  "late_minutes": 0,
  "overtime_minutes": 0,
  "work_hours": 0,
  "leave_type": "personal",
  "approved_by": null,
  "approved_at": null,
  "note": "Việc riêng",
  "created_at": "2025-11-27T10:00:00",
  "updated_at": null
}
```

#### Error Responses

**400 Bad Request** (Invalid leave_type):
```json
{
  "detail": "Invalid leave_type. Must be one of: annual, sick, personal, maternity, unpaid"
}
```

**400 Bad Request** (Invalid date format):
```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD"
}
```

**400 Bad Request** (Missing required field):
```json
{
  "detail": "Missing required field: leave_type"
}
```

#### Examples

**cURL** (single day):
```bash
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/leave" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "employee_id": 123,
    "leave_type": "personal",
    "start_date": "2025-11-27",
    "end_date": "2025-11-27",
    "reason": "Việc riêng"
  }'
```

**cURL** (multi-day):
```bash
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/leave" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "employee_id": 123,
    "leave_type": "annual",
    "start_date": "2025-11-27",
    "end_date": "2025-11-30",
    "reason": "Nghỉ phép hàng năm"
  }'
```

---

## Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful (check-out) |
| 201 | Created | Resource created (check-in, leave) |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid token |
| 500 | Internal Server Error | Server error (token not configured) |

---

## Rate Limiting (Optional)

If rate limiting is enabled:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1635338400
```

**Error** (429 Too Many Requests):
```json
{
  "detail": "Rate limit exceeded"
}
```

---

## Data Types

### Time Format
- Format: `HH:MM:SS` (24-hour)
- Examples: `09:00:00`, `17:30:00`, `23:59:59`

### Date Format
- Format: `YYYY-MM-DD`
- Examples: `2025-11-27`, `2025-12-31`

### Leave Types
- `annual`: Nghỉ phép hàng năm
- `sick`: Nghỉ ốm
- `personal`: Nghỉ việc riêng
- `maternity`: Nghỉ thai sản
- `unpaid`: Nghỉ không lương

### Employment Status
- `active`: Đang làm việc
- `probation`: Thử việc
- `terminated`: Đã nghỉ việc
- `on_leave`: Nghỉ phép dài hạn

---

## Best Practices

### 1. Error Handling
```javascript
try {
  const response = await fetch('/api/public/attendance/check-in', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error.detail);
    return;
  }

  const data = await response.json();
  console.log('Success:', data);
} catch (error) {
  console.error('Network error:', error);
}
```

### 2. Retry Logic
```javascript
async function fetchWithRetry(url, options, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.ok) return response;
      if (response.status === 401) throw new Error('Unauthorized');
      if (i === retries - 1) throw new Error('Max retries exceeded');
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    } catch (error) {
      if (i === retries - 1) throw error;
    }
  }
}
```

### 3. Caching
```javascript
const cache = new Map();

async function getEmployees(page = 1) {
  const key = `employees_${page}`;
  if (cache.has(key)) {
    return cache.get(key);
  }

  const response = await fetch(`/api/public/employees?page=${page}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  cache.set(key, data);
  return data;
}
```

---

## Support

For issues or questions:
1. Check logs: `docker logs robis-backend`
2. Run test script: `python test_public_attendance.py`
3. Contact backend team

---

**Last Updated**: 2025-11-27
**Version**: 1.0.0

