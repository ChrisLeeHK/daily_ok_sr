from src.tasks.MyBaseTask import MyBaseTask


class TestClickOre(MyBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "測試點擊礦石"
        self.description = "測試在交易中心找到並點擊礦石圖示"

    def run(self):
        self.screenshot("test_ore_before")
        self.log_info("已截圖目前畫面至 screenshots/test_ore_before")

        ore_item = self.wait_until(lambda: self.find_one("ore_item"), time_out=10)

        if not ore_item:
            self.log_error("找不到礦石！請檢查 screenshots/test_ore_before 確認畫面是否正確")
            return

        self.log_info(f"找到礦石！位置: x={ore_item.x}, y={ore_item.y}, w={ore_item.width}, h={ore_item.height}")
        self.click_box(ore_item)
        self.sleep(0.5)
        self.screenshot("test_ore_after")
        self.log_info("點擊完成，截圖已存至 screenshots/test_ore_after", notify=True)
