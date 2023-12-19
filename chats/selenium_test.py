# import time
# from selenium import webdriver
# # from selenium.webdriver.chrome import options
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# options = Options()
# options.add_argument("start-maximized")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('excludeSwitches', ['enable-logging'])
# options.add_experimental_option('useAutomationExtension', False)
# options.add_argument('--disable-blink-features=AutomationControlled')
# driver = webdriver.Chrome(options=options)
# URL = "https://rozetka.com.ua"
# driver.get(URL)

# def test_element_search():
#     # XPath locator
#     element = driver.find_element(By.XPATH, "//*[@class='header__button ng-star-inserted']")
#     assert element.is_displayed()

#     # CSS selector locator
#     element2_css = driver.find_element(By.CSS_SELECTOR, ".ng-star-inserted:nth-child(2)")
#     assert element2_css.is_enabled()

#     # By ID
#     el1 = driver.find_element(By.ID, "design-font-1")
#     el2 = driver.find_element(By.ID, "design-font-2")
#     assert el1.tag_name == 'link'
#     assert el2.tag_name == 'link'


# def test_title():
#     assert driver.title == "Інтернет-магазин ROZETKA™: офіційний сайт найпопулярнішого онлайн-гіпермаркету в Україні"


# # Test 3: Waiting for an element
# def test_wait():
#     wait = WebDriverWait(driver, 30)
#     wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
#     element = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/app-root/div/div/rz-main-page/div/main/rz-main-page-content/div/rz-top-slider/app-slider/div/div[1]/ul")))
#     assert element.is_displayed()


# time.sleep(4)
# test_element_search()
# test_title()
# test_wait()

# driver.quit()

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

class RozetkaTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_untitled(self):
        driver = self.driver
        driver.get("https://rozetka.com.ua/")
        driver.set_window_size(1366, 728)
        wait = WebDriverWait(driver, 30)
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

        driver.find_element(By.CSS_SELECTOR, ".menu-categories_type_main > .menu-categories__item:nth-child(7) font > font").click()
        element = driver.find_element(By.CSS_SELECTOR, ".simple-slider__item:nth-child(2) .top-widget__slider-picture")
        ActionChains(driver).move_to_element(element).perform()
        ActionChains(driver).move_by_offset(0, 0).perform()
        element = driver.find_element(By.CSS_SELECTOR, ".simple-slider__item:nth-child(2) > .top-widget__slider-item .ng-lazyloading")
        ActionChains(driver).move_to_element(element).perform()
        ActionChains(driver).move_by_offset(0, 0).perform()
        driver.find_element(By.CSS_SELECTOR, ".top-widget__slider .simple-slider__control--next > svg").click()
        driver.find_element(By.CSS_SELECTOR, ".portal-grid__cell:nth-child(3) .tile-cats__heading_type_center > font > font").click()
        driver.find_element(By.LINK_TEXT, "UA").click()
        element = driver.find_element(By.LINK_TEXT, "UA")
        ActionChains(driver).move_to_element(element).perform()
        ActionChains(driver).move_by_offset(0, 0).perform()
        element = driver.find_element(By.CSS_SELECTOR, ".portal-navigation__item:nth-child(5) .portal-navigation__link-text")
        ActionChains(driver).move_to_element(element).perform()
        ActionChains(driver).move_by_offset(0, 0).perform()
        element = driver.find_element(By.CSS_SELECTOR, ".catalog-grid__cell:nth-child(3) .ng-lazyloaded:nth-child(1)")
        ActionChains(driver).move_to_element(element).perform()
        ActionChains(driver).move_by_offset(0, 0).perform()

if __name__ == "__main__":
    unittest.main()



# import unittest
# import time


# class TestAssertions(unittest.TestCase):
#     def setUp(self):
#         options = Options()
#         options.add_argument("start-maximized")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('excludeSwitches', ['enable-logging'])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument('--disable-blink-features=AutomationControlled')
#         self.driver = webdriver.Chrome(options=options)
#         # driver = webdriver.Chrome()
#         URL = "https://rozetka.com.ua"
#         self.driver.get(URL)

#     def test_element_search(self):
#         # XPath locator
#         element_xpath = self.driver.find_element(By.XPATH, "//*[@class='header__button ng-star-inserted']")
#         self.assertTrue(element_xpath.is_displayed())

#         # CSS selector locator
#         element2_css = self.driver.find_element(By.CSS_SELECTOR, ".ng-star-inserted:nth-child(2)")
#         self.assertTrue(element2_css.is_enabled())

#         # ID locator
#         el1 = self.driver.find_element(By.ID, "design-font-1")
#         self.assertEqual(el1.tag_name, 'link')

#     def test_title(self):
#         self.assertEqual(self.driver.title, "Інтернет-магазин ROZETKA™: офіційний сайт найпопулярнішого онлайн-гіпермаркету в Україні")

#     def test_wait(self):
#         wait = WebDriverWait(self.driver, 20)
#         wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

#         element = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/app-root/div/div/rz-main-page/div/main/rz-main-page-content/div/rz-top-slider/app-slider/div/div[1]/ul")))
#         self.assertTrue(element.is_enabled())

#     def tearDown(self):
#         self.driver.quit()

# if __name__ == '__main__':
#     unittest.main()

# options = Options()
# options.add_argument("start-maximized")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('excludeSwitches', ['enable-logging'])
# options.add_experimental_option('useAutomationExtension', False)
# options.add_argument('--disable-blink-features=AutomationControlled')
# driver = webdriver.Chrome(options=options)
# URL = "https://nova.knetminer.tech/resources"

# def test_element_search():
#     driver.get(URL)
#     # myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='flex-align-center']")))
#     WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div.header-wrapper__content > div > div > div.resources-page__main.main-resources")))

#     # XPath locator
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div[2]/div/div/div[1]/div[3]/button")))
#     element = driver.find_element(By.XPATH, "//*[@id='root']/div[2]/div/div/div[1]/div[3]/button")
#     assert element.is_displayed()

#     # CSS selector locator
#     element2_css = driver.find_element(By.CSS_SELECTOR, "#root > div.header > div > div.header__right > a")
#     assert element2_css.is_enabled()

#     # By link text
#     el1 = driver.find_element(By.LINK_TEXT, "Open")
#     el2 = driver.find_element(By.PARTIAL_LINK_TEXT, "My Resources")
#     assert el1.tag_name == 'a'
#     assert el2.tag_name == 'a'


# def test_title():
#     driver.get(URL)
#     print(driver.title)
#     assert driver.title == "Knetminer"


# # Test 3: Waiting for an element
# def test_wait():
#     driver.get(URL)
#     element = driver.find_element(By.XPATH, "//*[@id='root']/div[2]/div/div/div[1]/div[3]/button")
#     assert element.is_displayed()
#     element.click()
#     wait = WebDriverWait(driver, 10)
#     element = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='make-enquiry-modal__container card']")))
#     assert element.is_displayed()


# # time.sleep(10)
# test_element_search()
# test_title()
# test_wait()

# driver.quit()
