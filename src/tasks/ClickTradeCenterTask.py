from ok import BaseTask

class ClickTradeCenterTask(BaseTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = "Click Trade Center"
        self.description = "Find the Trade Center icon and click it once"

    def run(self):
        self.log_info("Looking for Trade Center icon...", notify=True)

        # Try to find the feature on screen
        trade_center = self.wait_until(
            lambda: self.find_one("trade_center"),
            time_out=10
        )

        if not trade_center:
            self.log_error("Could not find Trade Center icon")
            self.screenshot("trade_center_not_found")
            return

        self.log_info(
            f"Found Trade Center icon at ({trade_center.x}, {trade_center.y}), clicking it..."
        )
        self.click_box(trade_center)
        self.sleep(1)
        self.screenshot("after_trade_center_click")
        self.log_info("Clicked Trade Center icon", notify=True)