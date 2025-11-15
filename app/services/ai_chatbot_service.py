"""
AI Chatbot Service using Google Gemini
Robis ERP Assistant
"""

import os
import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import date, timedelta
import google.generativeai as genai
from dotenv import load_dotenv
from app.models.user import User

import re

load_dotenv()


class RobisAIChatbot:
    """AI Chatbot cho Robis ERP sử dụng Google Gemini"""

    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user

        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)

        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))

        # Initialize model
        self.model = genai.GenerativeModel(self.model_name)

    def _build_system_prompt(self) -> str:
        """Build system prompt with user context"""
        return f"""
            Bạn là trợ lý AI thông minh của hệ thống ERP Robis.

            THÔNG TIN NGƯỜI DÙNG:
            - Username: {self.current_user.username}
            - Email: {self.current_user.email}

            KHẢ NĂNG:
            1. Trả lời câu hỏi về đơn hàng
            2. Kiểm tra tồn kho sản phẩm
            3. Thông tin nhân viên
            4. Chấm công và attendance

            QUY TẮC:
            - Trả lời ngắn gọn (2-3 câu)
            - Chuyên nghiệp, thân thiện
            - Sử dụng số liệu cụ thể
            - Gợi ý nếu không có dữ liệu

            NGÔN NGỮ: Tiếng Việt
            """

    def analyze_intent(self, message: str) -> Dict[str, Any]:
        """Phân tích ý định user và trích xuất entities"""
        prompt = f"""
            Analyze this Vietnamese message and return ONLY a JSON object:

            {{
                "intent": "<intent_name>",
                "entities": {{
                    "product_sku": "<SKU if mentioned>",
                    "date": "<date if mentioned>"
                }},
                "confidence": <0.0-1.0>
            }}

            INTENT RULES:
            - "check_stock": Product inventory questions (keywords: "còn bao nhiêu", "tồn kho", "SP-", "sản phẩm")
            - "get_orders": Order questions (keywords: "đơn hàng", "order")
            - "check_attendance": Attendance questions (keywords: "chấm công", "đi muộn")
            - "employee_info": Employee questions (keywords: "nhân viên", "thông tin")
            - "help": Help requests (keywords: "làm gì", "giúp", "hướng dẫn")
            - "general": Greetings, thanks, other

            ENTITY EXTRACTION:
            - If message contains "SP-XXX" pattern, extract it as product_sku
            - If message contains product code, extract it
            - If no entities, return empty dict {{}}

            Examples:
            - "Sản phẩm SP-001 còn bao nhiêu?" → {{"intent": "check_stock", "entities": {{"product_sku": "SP-001"}}, "confidence": 0.95}}
            - "Hôm nay có bao nhiêu đơn?" → {{"intent": "get_orders", "entities": {{}}, "confidence": 0.9}}

            Message: "{message}"

            Return ONLY valid JSON, no markdown.
            """

        try:
            response = self.model.generate_content(
                prompt, generation_config={"temperature": 0.1, "max_output_tokens": 300}
            )

            # Clean response
            text = response.text.strip()

            # --- FIX SYNTAX START ---
            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]  # Bỏ ```json
            if text.startswith("```"):
                text = text[3:]  # Bỏ ```
            if text.endswith("```"):
                text = text[:-3]  # Bỏ ```
            # --- FIX SYNTAX END ---

            text = text.strip()

            result = json.loads(text)

            # Ensure entities is a dict
            if "entities" not in result:
                result["entities"] = {}

            return result

        except Exception as e:
            print(f"Intent analysis error: {e}")

            # Fallback: Extract entities manually
            message_lower = message.lower()
            entities = {}

            # Extract product SKU (pattern: SP-XXX)
            # (import re đã được chuyển lên đầu file cho đúng chuẩn)
            sku_match = re.search(r"SP-\d+", message.upper())
            if sku_match:
                entities["product_sku"] = sku_match.group(0)

            # Detect intent by keywords
            if any(
                kw in message_lower
                for kw in ["tồn kho", "còn bao nhiêu", "sp-", "sản phẩm", "kho"]
            ):
                return {
                    "intent": "check_stock",
                    "entities": entities,
                    "confidence": 0.8,
                }
            elif any(kw in message_lower for kw in ["đơn hàng", "order", "đơn"]):
                return {"intent": "get_orders", "entities": entities, "confidence": 0.8}
            else:
                return {"intent": "general", "entities": {}, "confidence": 0.5}

    def get_orders_data(self, entities: Dict) -> str:
        """Lấy dữ liệu đơn hàng"""
        try:
            from app.models.order import Order
            from sqlalchemy import func, cast, Date  # ⭐ THÊM IMPORT NÀY

            date_str = entities.get("date", "today")
            if date_str == "today":
                target_date = date.today()
            elif date_str == "yesterday":
                target_date = date.today() - timedelta(days=1)
            else:
                target_date = date.today()

            # ⭐ SỬA DÒNG NÀY: Dùng created_at và cast sang Date
            orders = (
                self.db.query(Order)
                .filter(cast(Order.created_at, Date) == target_date)
                .all()
            )

            if not orders:
                return (
                    f"❌ Không có đơn hàng nào ngày {target_date.strftime('%d/%m/%Y')}"
                )

            total_amount = sum(o.total_amount for o in orders)

            return f"""
    📊 Đơn hàng {target_date.strftime('%d/%m/%Y')}:
    • Tổng số: {len(orders)} đơn
    • Giá trị: {total_amount:,.0f} VNĐ
    """
        except Exception as e:
            return f"⚠️ Lỗi khi lấy dữ liệu đơn hàng: {str(e)}"

    def check_stock(self, entities: Dict, message: str = "") -> str:
        """Kiểm tra tồn kho"""
        try:
            from app.models.product import Product
            from app.models.inventory import Stock

            # Lấy SKU từ entities
            product_sku = entities.get("product_sku", "").upper()

            # Nếu không có trong entities, thử extract từ message
            if not product_sku and message:
                import re

                sku_match = re.search(r"SP-\d+", message.upper())
                if sku_match:
                    product_sku = sku_match.group(0)

            if not product_sku:
                return "⚠️ Vui lòng cung cấp mã sản phẩm (VD: SP-001)"

            # Query product từ database
            product = self.db.query(Product).filter(Product.sku == product_sku).first()

            if not product:
                return f"❌ Không tìm thấy sản phẩm với mã: {product_sku}"

            # Query stock/inventory
            stocks = self.db.query(Stock).filter(Stock.product_id == product.id).all()

            total_quantity = sum(s.quantity for s in stocks) if stocks else 0

            # ⭐ SỬA PHẦN NÀY: Hiển thị tên category thay vì category_id
            category_name = "Chưa phân loại"
            if product.category:  # Nếu có relationship với ProductCategory
                category_name = product.category.name

            # Format response với đúng field names
            return f"""
    📦 {product.name} (SKU: {product_sku})
    • Tổng tồn: {total_quantity} {product.unit or 'đơn vị'}
    • Giá bán: {product.unit_price:,.0f} VNĐ
    • Danh mục: {category_name}
    • Trạng thái: {'✅ Còn hàng' if total_quantity > 0 else '❌ Hết hàng'}
    """
        except Exception as e:
            return f"⚠️ Lỗi khi kiểm tra tồn kho: {str(e)}"

    def get_help(self) -> str:
        """Hướng dẫn sử dụng"""
        return """
        🤖 Tôi có thể giúp bạn:

        📋 Đơn hàng:
        • "Hôm nay có bao nhiêu đơn?"

        📦 Tồn kho:
        • "Sản phẩm SP-001 còn bao nhiêu?"

        💡 Hãy hỏi tôi bất cứ điều gì!
        """

    def chat(self, message: str) -> Dict[str, Any]:
        """Main chat function"""
        # 1. Analyze intent
        intent_data = self.analyze_intent(message)
        intent = intent_data.get("intent", "general")
        entities = intent_data.get("entities", {})
        confidence = intent_data.get("confidence", 0.0)

        # 2. Get data based on intent
        context = ""

        try:
            if intent == "get_orders":
                context = self.get_orders_data(entities)

            elif intent == "check_stock":
                # Thêm message vào đây
                context = self.check_stock(entities, message)

            elif intent == "help":
                context = self.get_help()

            elif intent == "general":
                context = "Xin chào! Tôi là trợ lý AI của Robis ERP."

            else:
                context = self.get_help()

        except Exception as e:
            context = f"❌ Lỗi: {str(e)}"

        # 3. Generate response with Gemini
        try:
            final_prompt = f"""
                {self._build_system_prompt()}

                Câu hỏi: {message}

                Dữ liệu: {context}

                Trả lời ngắn gọn dựa trên dữ liệu trên.
            """

            response = self.model.generate_content(
                final_prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                },
            )

            final_response = response.text

        except Exception as e:
            final_response = context

        return {"response": final_response, "intent": intent, "confidence": confidence}
