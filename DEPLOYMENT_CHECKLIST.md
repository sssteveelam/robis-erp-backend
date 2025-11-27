# Deployment Checklist - Public QR/Kiosk Attendance

## Pre-Deployment

### Code Review
- [ ] Review `app/api/dependencies/service_auth.py`
- [ ] Review `app/api/v1/public_attendance.py`
- [ ] Review `app/core/config.py` changes
- [ ] Review `app/main.py` changes
- [ ] No syntax errors: `python -m py_compile app/api/v1/public_attendance.py`

### Testing
- [ ] Run test script: `python test_public_attendance.py`
- [ ] All 5 tests pass
- [ ] No console errors

### Documentation
- [ ] PUBLIC_QR_SETUP.md reviewed
- [ ] ENV_SETUP.md reviewed
- [ ] QUICK_START.md reviewed
- [ ] IMPLEMENTATION_SUMMARY.md reviewed

---

## Backend Deployment

### Configuration
- [ ] Create secure token: `openssl rand -hex 32`
- [ ] Add `ATTEND_PUBLIC_TOKEN` to `.env`
- [ ] Verify `.env` file exists in root directory
- [ ] Verify `.env` is in `.gitignore`

### Deployment
- [ ] Backend code deployed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database migrations run (if any): `alembic upgrade head`
- [ ] Backend restarted/redeployed

### Verification
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] Swagger docs available: `http://localhost:8000/docs`
- [ ] Public endpoints visible in Swagger

### Testing
- [ ] Test without token → 401
  ```bash
  curl -i "http://localhost:8000/api/v1/public/employees"
  ```

- [ ] Test with invalid token → 401
  ```bash
  curl -i "http://localhost:8000/api/v1/public/employees" \
    -H "Authorization: Bearer invalid-token"
  ```

- [ ] Test with valid token → 200
  ```bash
  curl -i "http://localhost:8000/api/v1/public/employees" \
    -H "Authorization: Bearer <ATTEND_PUBLIC_TOKEN>"
  ```

- [ ] Test check-in → 201
- [ ] Test check-out → 200
- [ ] Test leave → 201

---

## Frontend Deployment

### Configuration
- [ ] Add `NEXT_PUBLIC_ATTEND_TOKEN` to `.env.local`
- [ ] Token matches backend token
- [ ] Verify `.env.local` is in `.gitignore`

### Proxy Setup
- [ ] Proxy `/api/public/...` configured
- [ ] Authorization header added automatically
- [ ] Rewrite rules correct

### Verification
- [ ] Frontend builds without errors: `npm run build`
- [ ] No console errors in browser
- [ ] Network tab shows Authorization header

### Testing
- [ ] Fetch employees: `fetch('/api/public/employees')`
- [ ] Check-in: `fetch('/api/public/attendance/check-in', {...})`
- [ ] Check-out: `fetch('/api/public/attendance/check-out', {...})`
- [ ] Leave: `fetch('/api/public/attendance/leave', {...})`

---

## Production Hardening

### Security
- [ ] Token is strong (32+ characters)
- [ ] Token is random (not predictable)
- [ ] Token is not in logs
- [ ] Token is not in error messages
- [ ] Token is not in Git history

### Rate Limiting (Optional but Recommended)
- [ ] Install slowapi: `pip install slowapi`
- [ ] Configure rate limits (e.g., 10 req/min/IP)
- [ ] Test rate limiting works

### Audit Logging (Optional but Recommended)
- [ ] Setup logging for public endpoints
- [ ] Log: employee_id, action, IP, timestamp
- [ ] Logs are persisted
- [ ] Logs are monitored

### Monitoring
- [ ] Setup alerts for 401 errors
- [ ] Setup alerts for 500 errors
- [ ] Monitor response time
- [ ] Monitor error rate

---

## Post-Deployment

### Verification
- [ ] All endpoints working in production
- [ ] No errors in production logs
- [ ] Response times acceptable
- [ ] Error rate < 1%

### Documentation
- [ ] Update team wiki/docs
- [ ] Share token securely with team
- [ ] Document token rotation schedule
- [ ] Document troubleshooting steps

### Team Communication
- [ ] Notify backend team
- [ ] Notify frontend team
- [ ] Notify QA team
- [ ] Notify DevOps team

### Monitoring
- [ ] Setup dashboard for public endpoints
- [ ] Monitor daily for first week
- [ ] Check logs for errors
- [ ] Check logs for suspicious activity

---

## Rollback Plan

If issues occur:

### Step 1: Immediate Actions
- [ ] Stop accepting requests to public endpoints
- [ ] Disable public router in `main.py`
- [ ] Redeploy backend
- [ ] Notify team

### Step 2: Investigation
- [ ] Check backend logs
- [ ] Check database logs
- [ ] Check frontend logs
- [ ] Identify root cause

### Step 3: Resolution
- [ ] Fix issue
- [ ] Test thoroughly
- [ ] Redeploy
- [ ] Verify all endpoints working

---

## Token Rotation

### Monthly Rotation
- [ ] Generate new token: `openssl rand -hex 32`
- [ ] Update backend `.env` with new token
- [ ] Update frontend `.env.local` with new token
- [ ] Restart backend and frontend
- [ ] Test all endpoints
- [ ] Monitor for errors

### Emergency Rotation (if token leaked)
- [ ] Generate new token immediately
- [ ] Update backend `.env`
- [ ] Update frontend `.env.local`
- [ ] Restart services immediately
- [ ] Review logs for suspicious activity
- [ ] Notify security team

---

## Sign-Off

### Backend Team
- [ ] Name: ________________
- [ ] Date: ________________
- [ ] Status: ✅ Approved / ❌ Rejected

### Frontend Team
- [ ] Name: ________________
- [ ] Date: ________________
- [ ] Status: ✅ Approved / ❌ Rejected

### DevOps Team
- [ ] Name: ________________
- [ ] Date: ________________
- [ ] Status: ✅ Approved / ❌ Rejected

### QA Team
- [ ] Name: ________________
- [ ] Date: ________________
- [ ] Status: ✅ Approved / ❌ Rejected

---

## Notes

```
[Add any additional notes or issues here]




```

---

**Deployment Date**: ________________
**Deployed By**: ________________
**Status**: ✅ Complete / ⏳ In Progress / ❌ Failed

