#!/usr/bin/env python3
"""
Test script cho Public QR/Kiosk Attendance Endpoints

Sử dụng:
    python test_public_attendance.py

Yêu cầu:
    - Backend chạy tại http://localhost:8000
    - ATTEND_PUBLIC_TOKEN được set trong .env
    - Có ít nhất 1 employee trong database
"""

import requests
import json
from datetime import datetime, date, time, timedelta
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
SERVICE_TOKEN = "your-super-secret-random-token-here"  # Thay bằng token thực tế

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text: str):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text: str):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def get_headers() -> dict:
    """Tạo headers với service token"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SERVICE_TOKEN}",
    }


def test_employees_list():
    """Test GET /api/v1/public/employees"""
    print_header("TEST 1: Lấy danh sách nhân viên")

    url = f"{BASE_URL}/api/v1/public/employees?page=1&page_size=10"

    try:
        response = requests.get(url, headers=get_headers())

        print(f"Status Code: {response.status_code}")
        print(f"URL: {url}\n")

        if response.status_code == 200:
            data = response.json()
            print_success(f"Lấy được {len(data['items'])} nhân viên")
            print_info(f"Total: {data['total']}, Pages: {data['total_pages']}")

            if data['items']:
                emp = data['items'][0]
                print_info(f"Sample employee: {emp['employee_code']} - {emp['full_name']}")
                return emp['id']  # Return first employee ID for next tests
            return None

        else:
            print_error(f"Failed: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None


def test_check_in(employee_id: Optional[int] = None):
    """Test POST /api/v1/public/attendance/check-in"""
    print_header("TEST 2: Chấm công vào")

    if not employee_id:
        print_warning("Không có employee_id, bỏ qua test này")
        return

    url = f"{BASE_URL}/api/v1/public/attendance/check-in"

    # Tạo check-in time (9:05 AM)
    check_in_time = "09:05:00"

    payload = {
        "employee_id": employee_id,
        "check_in": check_in_time,
        "note": "Test check-in từ script",
    }

    try:
        response = requests.post(url, json=payload, headers=get_headers())

        print(f"Status Code: {response.status_code}")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}\n")

        if response.status_code == 201:
            data = response.json()
            print_success(f"Check-in thành công")
            print_info(f"Attendance ID: {data['id']}")
            print_info(f"Status: {data['status']}")
            print_info(f"Late minutes: {data['late_minutes']}")
            return data['id']

        else:
            print_error(f"Failed: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None


def test_check_out(employee_id: Optional[int] = None):
    """Test POST /api/v1/public/attendance/check-out"""
    print_header("TEST 3: Chấm công ra")

    if not employee_id:
        print_warning("Không có employee_id, bỏ qua test này")
        return

    url = f"{BASE_URL}/api/v1/public/attendance/check-out"

    # Tạo check-out time (5:30 PM)
    check_out_time = "17:30:00"

    payload = {
        "employee_id": employee_id,
        "check_out": check_out_time,
        "note": "Test check-out từ script",
    }

    try:
        response = requests.post(url, json=payload, headers=get_headers())

        print(f"Status Code: {response.status_code}")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}\n")

        if response.status_code == 200:
            data = response.json()
            print_success(f"Check-out thành công")
            print_info(f"Attendance ID: {data['id']}")
            print_info(f"Check-in: {data['check_in']}")
            print_info(f"Check-out: {data['check_out']}")
            print_info(f"Work hours: {data['work_hours']} minutes")
            print_info(f"Overtime: {data['overtime_minutes']} minutes")

        else:
            print_error(f"Failed: {response.text}")

    except Exception as e:
        print_error(f"Exception: {str(e)}")


def test_leave_request(employee_id: Optional[int] = None):
    """Test POST /api/v1/public/attendance/leave"""
    print_header("TEST 4: Đăng ký nghỉ phép")

    if not employee_id:
        print_warning("Không có employee_id, bỏ qua test này")
        return

    url = f"{BASE_URL}/api/v1/public/attendance/leave"

    # Tạo leave request cho ngày mai
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    payload = {
        "employee_id": employee_id,
        "leave_type": "personal",
        "start_date": tomorrow,
        "end_date": tomorrow,
        "reason": "Việc riêng",
    }

    try:
        response = requests.post(url, json=payload, headers=get_headers())

        print(f"Status Code: {response.status_code}")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}\n")

        if response.status_code == 201:
            data = response.json()
            print_success(f"Đăng ký nghỉ phép thành công")
            print_info(f"Attendance ID: {data['id']}")
            print_info(f"Leave type: {data['leave_type']}")
            print_info(f"Date: {data['date']}")

        else:
            print_error(f"Failed: {response.text}")

    except Exception as e:
        print_error(f"Exception: {str(e)}")


def test_invalid_token():
    """Test với token không hợp lệ"""
    print_header("TEST 5: Kiểm tra xác thực token")

    url = f"{BASE_URL}/api/v1/public/employees?page=1&page_size=10"

    # Test 1: Không có token
    print_info("Test 5.1: Không có Authorization header")
    try:
        response = requests.get(url, headers={"Content-Type": "application/json"})
        if response.status_code == 401:
            print_success(f"Đúng: Trả 401 Unauthorized")
        else:
            print_warning(f"Unexpected status: {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")

    # Test 2: Token sai
    print_info("Test 5.2: Token không hợp lệ")
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid-token-12345",
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            print_success(f"Đúng: Trả 401 Unauthorized")
        else:
            print_warning(f"Unexpected status: {response.status_code}")
    except Exception as e:
        print_error(f"Exception: {str(e)}")


def test_health_check():
    """Test health check endpoint"""
    print_header("TEST 0: Health Check")

    url = f"{BASE_URL}/health"

    try:
        response = requests.get(url)

        print(f"Status Code: {response.status_code}")
        print(f"URL: {url}\n")

        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is healthy: {data}")
            return True
        else:
            print_error(f"Backend is not healthy: {response.text}")
            return False

    except Exception as e:
        print_error(f"Cannot connect to backend: {str(e)}")
        print_warning("Make sure backend is running at http://localhost:8000")
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   Public QR/Kiosk Attendance API Test Suite               ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Service Token: {SERVICE_TOKEN[:20]}...")

    # Test 0: Health check
    if not test_health_check():
        return

    # Test 1: Get employees
    employee_id = test_employees_list()

    # Test 2: Check-in
    if employee_id:
        test_check_in(employee_id)

    # Test 3: Check-out
    if employee_id:
        test_check_out(employee_id)

    # Test 4: Leave request
    if employee_id:
        test_leave_request(employee_id)

    # Test 5: Invalid token
    test_invalid_token()

    # Summary
    print_header("Test Suite Complete")
    print_info("Tất cả các test đã hoàn thành!")
    print_info("Kiểm tra kết quả ở trên để xác nhận các endpoints hoạt động đúng.")


if __name__ == "__main__":
    main()

