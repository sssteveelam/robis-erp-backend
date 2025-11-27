# Environment Setup for Public QR/Kiosk Attendance

## Biến môi trường cần thêm

Thêm vào file `.env` của backend:

```env
# Public QR/Kiosk Service Token
ATTEND_PUBLIC_TOKEN=your-super-secret-random-token-here
```

## Cách tạo token an toàn

### Option 1: Sử dụng OpenSSL (Linux/Mac)
```bash
openssl rand -hex 32
```

**Output ví dụ**:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

### Option 2: Sử dụng Python
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Output ví dụ**:
```
KF_9mK-L8pQ3xR2vN5tY7wZ1aB4cD6eF8gH0jK2lM4nO6pQ8rS0tU2vW4xY6zA8bC
```

### Option 3: Sử dụng Node.js
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

## Cấu hình cho các môi trường

### Development (.env.local)
```env
ATTEND_PUBLIC_TOKEN=dev-token-12345678901234567890123456789012
```

### Staging (.env.staging)
```env
ATTEND_PUBLIC_TOKEN=staging-token-abcdefghijklmnopqrstuvwxyz123456
```

### Production (Secret Manager)
```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name robis/attend-public-token \
  --secret-string "prod-token-xyz..."

# Docker
docker run -e ATTEND_PUBLIC_TOKEN="prod-token-xyz..." ...

# Kubernetes
kubectl create secret generic attend-token \
  --from-literal=token="prod-token-xyz..."
```

## Kiểm tra cấu hình

### 1. Kiểm tra token được load
```bash
# Chạy backend và kiểm tra logs
# Nếu không thấy lỗi "Service token not configured", token đã được load

# Hoặc test endpoint:
curl -i "http://localhost:8000/api/v1/public/employees" \
  -H "Authorization: Bearer dev-token-12345678901234567890123456789012"
```

### 2. Kiểm tra token không hợp lệ
```bash
# Nên trả 401 Unauthorized
curl -i "http://localhost:8000/api/v1/public/employees" \
  -H "Authorization: Bearer wrong-token"
```

### 3. Kiểm tra không có token
```bash
# Nên trả 401 Unauthorized
curl -i "http://localhost:8000/api/v1/public/employees"
```

## Rotation Token

### Khi cần rotate token

1. **Tạo token mới**:
   ```bash
   openssl rand -hex 32
   ```

2. **Cập nhật backend** (hỗ trợ 2 token song song):
   ```env
   ATTEND_PUBLIC_TOKEN=new-token-xyz...
   ATTEND_PUBLIC_TOKEN_OLD=old-token-abc...  # Optional, cho thời gian transition
   ```

3. **Cập nhật FE** (.env.local):
   ```env
   NEXT_PUBLIC_ATTEND_TOKEN=new-token-xyz...
   ```

4. **Restart services**:
   ```bash
   # Backend
   docker restart robis-backend

   # Frontend
   npm run build && npm start
   ```

5. **Xóa token cũ** (sau 24h):
   ```env
   # Xóa ATTEND_PUBLIC_TOKEN_OLD
   ```

## Bảo mật Best Practices

### ✅ DO
- ✅ Sử dụng token random đủ dài (32+ ký tự)
- ✅ Lưu token trong Secret Manager (không hard-code)
- ✅ Rotate token hàng tháng
- ✅ Log tất cả requests đến public endpoints
- ✅ Áp dụng rate limiting
- ✅ Giới hạn fields trả về (không trả salary, personal info)

### ❌ DON'T
- ❌ Không hard-code token trong code
- ❌ Không commit token vào Git
- ❌ Không sử dụng token yếu (< 16 ký tự)
- ❌ Không share token qua email/chat không mã hóa
- ❌ Không để token trong logs/error messages
- ❌ Không sử dụng cùng token cho nhiều services

## Troubleshooting

### Token không được load
```
Error: Service token not configured on server
```

**Giải pháp**:
1. Kiểm tra `.env` file có `ATTEND_PUBLIC_TOKEN`
2. Kiểm tra `.env` file nằm trong root directory
3. Restart backend: `docker restart robis-backend` hoặc `python -m uvicorn app.main:app --reload`

### Token không khớp
```
Error: Invalid or missing service token
```

**Giải pháp**:
1. Kiểm tra token trong `.env` khớp với token gửi từ FE
2. Kiểm tra không có khoảng trắng thừa
3. Kiểm tra format: `Authorization: Bearer <token>`

### 401 Unauthorized
```
Status: 401 Unauthorized
```

**Giải pháp**:
1. Kiểm tra header `Authorization` được gửi
2. Kiểm tra token không bị truncate
3. Kiểm tra FE proxy gắn token đúng

## Monitoring & Logging

### Log requests đến public endpoints
```python
# app/api/v1/public_attendance.py
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

### Metrics cần monitor
- Số requests/phút đến public endpoints
- Số failed authentication attempts
- Response time
- Error rate

## Liên hệ

Nếu có vấn đề với token setup, liên hệ team DevOps hoặc Backend.

