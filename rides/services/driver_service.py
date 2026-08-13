def make_driver_available(driver):
    if driver:
        driver.is_available = True
        driver.save(update_fields=["is_available"])