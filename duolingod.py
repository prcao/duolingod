import googletrans
from googletrans import Translator
from selenium import webdriver

# t = Translator()

# x = t.translate('aa fuck', dest='zh-cn')
# print(x)

driver = webdriver.Firefox()
driver.get("http://www.python.org")