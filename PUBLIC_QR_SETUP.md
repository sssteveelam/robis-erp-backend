# Public QR/Kiosk Attendance Setup Guide

## Mục tiêu

Bật trang Chấm công Nhanh (QR) công khai mà không cần đăng nhập user, thông qua 1 service token an toàn.

## Cấu hình Backend

### 1. Thêm biến môi trường

Thêm vào file `.env` của backend:

```env
# Public QR/Kiosk Service Token
ATTEND_PUBLIC_TOKEN=your-super-secret-random-token-here
```

**Yêu cầu token**:
- Chuỗi random đủ dài (ít nhất 32 ký tự)
- Không phải JWT user
- Có thể rotate theo kỳ (ví dụ: hàng tháng)
- Nên lưu trữ dưới Secret Manager (Docker/K8s/Cloud)

**Ví dụ tạo token**:
```bash
# Linux/Mac
openssl rand -hex 32

# Python
import secrets
print(secrets.token_urlsafe(32))
```

### 2. Cấu trúc code đã triển khai

```
app/
├── api/
│   ├── dependencies/
│   │   └── service_auth.py          # ← NEW: Service token auth dependency
│   └── v1/
│       └── public_attendance.py     # ← NEW: Public QR endpoints
├── core/
│   └── config.py                    # ← UPDATED: Thêm ATTEND_PUBLIC_TOKEN
└── main.py                          # ← UPDATED: Đăng ký public router
```

## API Endpoints

### 1. GET /api/v1/public/employees

Lấy danh sách nhân viên để chọn từ QR kiosk.

**Authentication**: Service token via `Authorization: Bearer <ATTEND_PUBLIC_TOKEN>`

**Query Parameters**:
- `page` (int, default=1): Trang thứ mấy
- `page_size` (int, default=10, max=100): Số item trên trang
- `search` (string, optional): Tìm theo name, email, employee_code

**Response**:
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

**cURL Example**:
```bash
curl -i "http://localhost:8000/api/v1/public/employees?page=1&page_size=10&search=Nguyễn" \
  -H "Authorization: Bearer your-super-secret-random-token-here"
```

### 2. POST /api/v1/public/attendance/check-in

Chấm công vào (QR/Kiosk).

**Authentication**: Service token via `Authorization: Bearer <ATTEND_PUBLIC_TOKEN>`

**Request Body**:
```json
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

**cURL Example**:
```bash
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/check-in" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-super-secret-random-token-here" \
  -d '{
    "employee_id": 123,
    "check_in": "09:05:00",
    "note": "Kẹt xe"
  }'
```

### 3. POST /api/v1/public/attendance/check-out

Chấm công ra (QR/Kiosk).

**Authentication**: Service token via `Authorization: Bearer <ATTEND_PUBLIC_TOKEN>`

**Request Body**:
```json
{
  "employee_id": 123,
  "check_out": "17:30:00",
  "note": "Đi sớm"
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

**cURL Example**:
```bash
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/check-out" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-super-secret-random-token-here" \
  -d '{
    "employee_id": 123,
    "check_out": "17:30:00"
  }'
```

### 4. POST /api/v1/public/attendance/leave

Đăng ký nghỉ phép (QR/Kiosk).

**Authentication**: Service token via `Authorization: Bearer <ATTEND_PUBLIC_TOKEN>`

**Request Body**:
```json
{
  "employee_id": 123,
  "leave_type": "personal",
  "start_date": "2025-11-27",
  "end_date": "2025-11-28",
  "reason": "Việc riêng"
}
```

**Leave Types**:
- `annual`: Nghỉ phép hàng năm
- `sick`: Nghỉ ốm
- `personal`: Nghỉ việc riêng
- `maternity`: Nghỉ thai sản
- `unpaid`: Nghỉ không lương

**Response** (201 Created):
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

**cURL Example**:
```bash
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/leave" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-super-secret-random-token-here" \
  -d '{
    "employee_id": 123,
    "leave_type": "personal",
    "start_date": "2025-11-27",
    "end_date": "2025-11-27",
    "reason": "Việc riêng"
  }'
```

## Cấu hình Frontend

### 1. Proxy Setup (Next.js/Vite)

Trong `next.config.js` hoặc `vite.config.js`, cấu hình proxy để gắn service token:

**Next.js** (`next.config.js`):
```javascript
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

**Vite** (`vite.config.js`):
```javascript
export default {
  server: {
    proxy: {
      '/api/public': {
        target: process.env.VITE_API_URL,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/public/, '/api/v1/public'),
        headers: {
          'Authorization': `Bearer ${process.env.VITE_ATTEND_TOKEN}`,
        },
      },
    },
  },
};
```

### 2. Environment Variables

Thêm vào `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ATTEND_TOKEN=your-super-secret-random-token-here
```

### 3. Frontend Usage

```typescript
// Lấy danh sách nhân viên
const response = await fetch('/api/public/employees?page=1&page_size=10');
const data = await response.json();

// Chấm công vào
await fetch('/api/public/attendance/check-in', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    employee_id: 123,
    check_in: '09:05:00',
    note: 'Kẹt xe',
  }),
});

// Chấm công ra
await fetch('/api/public/attendance/check-out', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    employee_id: 123,
    check_out: '17:30:00',
  }),
});

// Đăng ký nghỉ phép
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

## Bảo mật & Vận hành

### 1. Token Management

- **Rotation**: Rotate token hàng tháng hoặc khi có nhân viên rời công ty
- **Backup**: Lưu 2 token song song trong thời gian cutover
- **Monitoring**: Log tất cả các request đến public endpoints
- **Revocation**: Có cơ chế revoke token nếu bị lộ

### 2. Rate Limiting (Khuyến nghị)

Cài đặt rate limit để tránh abuse:

```bash
pip install slowapi
```

Thêm vào `main.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Áp dụng rate limit cho public endpoints
@app.get("/api/v1/public/employees")
@limiter.limit("10/minute")
def public_get_employees(...):
    ...
```

### 3. Audit Logging (Khuyến nghị)

Log tất cả các request đến public endpoints:

```python
import logging
from datetime import datetime

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

### 4. Field Masking

Các public endpoints chỉ trả về fields công khai:
- ✅ id, employee_code, full_name, email, department_id
- ❌ salary, personal_info, bank_account, etc.

### 5. Search Restrictions (Khuyến nghị)

Để tránh lộ danh sách nhân viên:

```python
# Bắt buộc search parameter
@router.get("/employees")
def public_get_employees(
    search: str = Query(..., min_length=2),  # Bắt buộc, ít nhất 2 ký tự
    ...
):
    ...
```

## Troubleshooting

### 1. 401 Unauthorized

**Nguyên nhân**: Token không hợp lệ hoặc không được gửi

**Giải pháp**:
- Kiểm tra `ATTEND_PUBLIC_TOKEN` trong `.env`
- Kiểm tra header `Authorization: Bearer <token>`
- Kiểm tra token không có khoảng trắng thừa

### 2. 500 Service token not configured

**Nguyên nhân**: `ATTEND_PUBLIC_TOKEN` không được set

**Giải pháp**:
- Thêm `ATTEND_PUBLIC_TOKEN` vào `.env`
- Restart backend server

### 3. 400 Bad Request

**Nguyên nhân**: Dữ liệu request không hợp lệ

**Giải pháp**:
- Kiểm tra format JSON
- Kiểm tra định dạng thời gian (HH:MM:SS)
- Kiểm tra định dạng ngày (YYYY-MM-DD)

## Testing

### Sử dụng Postman

1. Tạo Environment:
   - `base_url`: `http://localhost:8000`
   - `token`: `your-super-secret-random-token-here`

2. Tạo Request:
   - **Method**: GET
   - **URL**: `{{base_url}}/api/v1/public/employees?page=1&page_size=10`
   - **Headers**: 
     - `Authorization: Bearer {{token}}`

### Sử dụng cURL

```bash
# Test token auth
curl -i "http://localhost:8000/api/v1/public/employees" \
  -H "Authorization: Bearer your-super-secret-random-token-here"

# Test check-in
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/check-in" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-super-secret-random-token-here" \
  -d '{"employee_id":1,"check_in":"09:05:00"}'
```

## Acceptance Criteria

- ✅ 4 API public trả 2xx khi có `Authorization: Bearer <ATTEND_PUBLIC_TOKEN>`
- ✅ Không cần JWT user; không ảnh hưởng các API cũ
- ✅ FE `/public/attendance` hoạt động không cần đăng nhập
- ✅ Có thể bật rate-limit/audit logs cho các public endpoints

## Liên hệ

Nếu có vấn đề, liên hệ team backend hoặc DevOps.

