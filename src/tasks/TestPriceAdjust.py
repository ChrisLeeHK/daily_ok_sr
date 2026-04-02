import re

from src.tasks.MyBaseTask import MyBaseTask


def _parse_price(boxes):
    """Extract the first integer from a list of OCR Box results."""
    for box in boxes:
        text = str(box.name) if box.name else ''
        match = re.search(r'\d+', text)
        if match:
            return int(match.group())
    return None


class TestPriceAdjust(MyBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "測試價格調整"
        self.description = "測試OCR讀取當前價格與最低市場價格，並自動調整"
        self.default_config.update({
            'current_price_x':  0.73,
            'current_price_y':  0.59,
            'current_price_x2': 0.76,
            'current_price_y2': 0.62,
            'lowest_price_x':   0.77,
            'lowest_price_y':   0.62,
            'lowest_price_x2':  0.82,
            'lowest_price_y2':  0.68,
            'only_read': False,  # True = just read prices, no clicking
        })

    def run(self):
        cx  = self.config.get('current_price_x',  0.73)
        cy  = self.config.get('current_price_y',  0.59)
        cx2 = self.config.get('current_price_x2', 0.76)
        cy2 = self.config.get('current_price_y2', 0.62)
        lx  = self.config.get('lowest_price_x',   0.77)
        ly  = self.config.get('lowest_price_y',   0.62)
        lx2 = self.config.get('lowest_price_x2',  0.82)
        ly2 = self.config.get('lowest_price_y2',  0.68)
        only_read = self.config.get('only_read', True)

        self.screenshot("test_price_before")

        # Crop and save the exact OCR regions so you can verify coordinates
        frame = self.frame
        if frame is not None:
            import cv2
            h, w = frame.shape[:2]
            # Current price region
            x1 = int(cx * w);  y1 = int(cy * h)
            x2 = int(cx2 * w); y2 = int(cy2 * h)
            cv2.imwrite("screenshots/debug_current_price.png", frame[y1:y2, x1:x2])
            # Lowest price region
            lx1 = int(lx * w);  ly1 = int(ly * h)
            lx2i = int(lx2 * w); ly2i = int(ly2 * h)
            cv2.imwrite("screenshots/debug_lowest_price.png", frame[ly1:ly2i, lx1:lx2i])
            self.log_info(f"已截圖 OCR 區域至 screenshots/debug_current_price.png 和 debug_lowest_price.png")

        # Read both prices
        current_raw = self.ocr(cx, cy, cx2, cy2, log=True)
        lowest_raw  = self.ocr(lx, ly, lx2, ly2, log=True)

        self.log_info(f"OCR 當前價格原始值: {[b.name for b in current_raw]}")
        self.log_info(f"OCR 最低市場價原始值: {[b.name for b in lowest_raw]}")

        if not current_raw:
            self.log_error("無法讀取當前價格 — 請調整 current_price 座標")
            return
        if not lowest_raw:
            self.log_error("無法讀取最低市場價 — 請調整 lowest_price 座標")
            return

        cur = _parse_price(current_raw)
        low = _parse_price(lowest_raw)
        if cur is None or low is None:
            self.log_error(f"無法解析數字 — current='{current_raw}' lowest='{lowest_raw}'")
            return

        self.log_info(f"當前價格: {cur}  |  最低市場價: {low}")

        if only_read:
            self.log_info("only_read=True，僅讀取不調整價格")
            return

        # Adjust price
        for _ in range(500):
            current_raw = self.ocr(cx, cy, cx2, cy2, log=False)
            lowest_raw  = self.ocr(lx, ly, lx2, ly2, log=False)

            if not current_raw or not lowest_raw:
                self.log_error("OCR 讀取失敗，停止調整")
                break

            cur = _parse_price(current_raw)
            low = _parse_price(lowest_raw)
            if cur is None or low is None:
                self.log_error(f"解析失敗 — current='{current_raw}' lowest='{lowest_raw}'")
                break

            self.log_info(f"當前價格: {cur}  |  最低市場價: {low}")

            if cur == low:
                self.log_info("價格已達最低市場價，完成！", notify=True)
                break
            elif cur < low:
                minus_btn = self.find_one("price_minus_button", use_gray_scale=True)
                if minus_btn:
                    self.click_box(minus_btn)
                else:
                    self.log_error("找不到 - 按鈕，停止調整")
                    break
            else:
                plus_btn = self.find_one("price_plus_button", use_gray_scale=True)
                if plus_btn:
                    self.click_box(plus_btn)
                else:
                    self.log_error("找不到 + 按鈕，停止調整")
                    break

            self.sleep(0.1)
