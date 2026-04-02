from src.tasks.MyBaseTask import MyBaseTask

class DailyTradeTask(MyBaseTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "每日交易任務"
        self.description = "登入 → 買礦石 → 鑄造 → 賣神秘金屬 → 登出"

    def run(self):
        self.do_login()
        self.buy_materials()
        self.craft()
        self.sell_metal()
        self.logout()

    def do_login(self):
        # a. Wait for HAOPLAY login screen
        self.wait_until(lambda: self.find_one("haoplay_login_screen"), time_out=30)
        
        # b. Click email login button
        self.click_box(self.find_one("email_login_button"))
        self.sleep(1)
        
        # c/d. Get account from DB and enter email
        email, password = self.get_account_from_db()
        self.click_box(self.find_one("email_input_field"))
        self.send_key(email)
        
        # e. Click "get verification code"
        self.click_box(self.find_one("get_verify_code_button"))
        
        # f. Fetch code from email (needs separate helper)
        code = self.fetch_email_code(email)
        
        # g. Enter code
        self.click_box(self.find_one("verify_code_input"))
        self.send_key(code)
        
        # h/i. Start and select character
        self.click_box(self.find_one("start_button"))
        self.wait_until(lambda: self.find_one("character_select_screen"), time_out=30)
        self.click_box(self.find_one("character_start_button"))

    def buy_materials(self):
        self.send_key('esc')
        self.click_box(self.wait_until(lambda: self.find_one("trade_center_button"), time_out=10))
        self.click_box(self.wait_until(lambda: self.find_one("sell_tab"), time_out=10))
        self.click_box(self.find_one("extract_one_button"))
        
        # Record current Runo — use OCR on the balance area
        runo = self.ocr(0.8, 0.05, 1.0, 0.1, match=None, log=True)
        self.log_info(f"Current Runo: {runo}")
        
        self.click_box(self.find_one("buy_tab"))
        self.click_box(self.find_one("ore_item"))
        # Set quantity to 240 — may need OCR input or +/- clicks
        self.set_quantity(240)
        self.click_box(self.find_one("purchase_button"))
        self.send_key('esc')

    def craft(self):
        self.send_key('f')
        self.wait_until(lambda: self.find_one("craft_menu"), time_out=10)
        self.click_box(self.find_one("mysterious_metal_option"))
        self.click_box(self.find_one("recipe_5"))
        self.click_box(self.find_one("max_quantity_button"))
        self.click_box(self.find_one("start_craft_button"))
        
        # Wait until focus reaches 0 — poll via OCR
        self.wait_until(
            lambda: self.ocr_focus_is_zero(),
            time_out=300  # adjust based on how long crafting takes
        )
        self.send_key('esc')

    def ocr_focus_is_zero(self):
        result = self.ocr(0.x, 0.y, 0.x2, 0.y2, match="0", log=True)
        return result is not None



    def sell_metal(self):
        self.click_box(self.wait_until(lambda: self.find_one("trade_center_button"), time_out=10))
        self.click_box(self.find_one("sell_tab"))
        self.click_box(self.find_one("mysterious_metal_item"))
        self.click_box(self.find_one("max_quantity_button"))
        
        # Press (-) until price is lowest or can't press anymore
        self.lower_price_to_minimum()
        
        self.click_box(self.find_one("list_item_button"))
        self.send_key('esc')

    def lower_price_to_minimum(self):
        for _ in range(500):  # safety cap
            minus_btn = self.find_one("price_minus_button")
            if not minus_btn:
                break
            self.click_box(minus_btn)
            self.sleep(0.05)




    def logout(self):
        self.click_box(self.wait_until(lambda: self.find_one("exit_login_button"), time_out=10))
        self.click_box(self.wait_until(lambda: self.find_one("switch_account_button"), time_out=10))
