# Quick Start - Public QR/Kiosk Attendance

## ⚡ 5 Phút Setup

### Step 1: Backend Configuration (1 phút)

Thêm vào `.env`:
```env
ATTEND_PUBLIC_TOKEN=your-super-secret-random-token-here
```

**Tạo token**:
```bash
# Linux/Mac
openssl rand -hex 32

# Windows (PowerShell)
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

### Step 2: Restart Backend (1 phút)

```bash
# Nếu dùng Docker
docker restart robis-backend

# Nếu chạy local
# Ctrl+C rồi chạy lại
python -m uvicorn app.main:app --reload
```

### Step 3: Test Backend (1 phút)

```bash
curl -i "http://localhost:8000/api/v1/public/employees?page=1&page_size=10" \
  -H "Authorization: Bearer your-super-secret-random-token-here"
```

**Expected Response** (200 OK):
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

### Step 4: Frontend Configuration (1 phút)

Thêm vào `.env.local`:
```env
NEXT_PUBLIC_ATTEND_TOKEN=your-super-secret-random-token-here
```

### Step 5: Test Frontend (1 phút)

```typescript
// Trong component React
const response = await fetch('/api/public/employees?page=1&page_size=10');
const data = await response.json();
console.log(data);
```

---

## 🧪 Test Endpoints

### 1. Lấy danh sách nhân viên
```bash
curl -i "http://localhost:8000/api/v1/public/employees?page=1&page_size=10" \
  -H "Authorization: Bearer your-token"
```

### 2. Chấm công vào
```bash
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/check-in" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "employee_id": 1,
    "check_in": "09:05:00",
    "note": "Kẹt xe"
  }'
```

### 3. Chấm công ra
```bash
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/check-out" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "employee_id": 1,
    "check_out": "17:30:00"
  }'
```

### 4. Đăng ký nghỉ phép
```bash
curl -i -X POST "http://localhost:8000/api/v1/public/attendance/leave" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "employee_id": 1,
    "leave_type": "personal",
    "start_date": "2025-11-27",
    "end_date": "2025-11-27",
    "reason": "Việc riêng"
  }'
```

---

## [object Object]eshooting

### ❌ 401 Unauthorized
**Nguyên nhân**: Token không hợp lệ

**Giải pháp**:
1. Kiểm tra token trong `.env` khớp với token gửi
2. Kiểm tra không có khoảng trắng thừa
3. Kiểm tra format: `Authorization: Bearer <token>`

### ❌ 500 Service token not configured
**Nguyên nhân**: `ATTEND_PUBLIC_TOKEN` chưa được set

**Giải pháp**:
1. Thêm `ATTEND_PUBLIC_TOKEN` vào `.env`
2. Restart backend

### ❌ 400 Bad Request
**Nguyên nhân**: Dữ liệu request không hợp lệ

**Giải pháp**:
1. Kiểm tra format JSON
2. Kiểm tra định dạng thời gian: `HH:MM:SS`
3. Kiểm tra định dạng ngày: `YYYY-MM-DD`

---

## 📚 Documentation

- **PUBLIC_QR_SETUP.md**: Hướng dẫn chi tiết
- **ENV_SETUP.md**: Setup environment
- **IMPLEMENTATION_SUMMARY.md**: Tóm tắt triển khai
- **test_public_attendance.py**: Test script

---

## ✅ Acceptance Criteria

- ✅ 4 API public trả 2xx khi có token
- ✅ Không cần JWT user
- ✅ FE hoạt động không cần đăng nhập
- ✅ Không ảnh hưởng các API cũ

---

## 🎯 Next Steps

1. Set `ATTEND_PUBLIC_TOKEN` trong `.env`
2. Restart backend
3. Test endpoints
4. Cấu hình frontend
5. Deploy to production

---

**Ready to go!** 🚀

