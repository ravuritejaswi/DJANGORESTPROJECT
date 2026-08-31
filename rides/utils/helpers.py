def get_driver_name(driver):
    if not driver:
        return None

    return driver.user.get_full_name() or driver.user.username
