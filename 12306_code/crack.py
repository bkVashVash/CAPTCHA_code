import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chaojiying import Chaojiying
from selenium.common.exceptions import TimeoutException

EMAIL = '邮箱'
PASSWORD = '密码'

CHAOJIYING_USERNAME = '超级鹰用户名'
CHAOJIYING_PASSWORD = '超级鹰密码'
CHAOJIYING_SOFT_ID = '软件id'
CHAOJIYING_KIND = '验证码代号'


class CrackTouClick():
    """
    主类
    通过调用 chaojiying 类中的 多个方法进行图片上传，结果获取
    """
    def __init__(self):
        self.url = 'https://kyfw.12306.cn/otn/login/init'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.email = EMAIL
        self.password = PASSWORD
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)
    
    def __del__(self):
        self.browser.close()
    
    def open(self):
        """
        打开网页输入用户名密码
        :return: None
        """
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.ID, 'username')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
        email.send_keys(self.email)
        password.send_keys(self.password)

    def get_touclick_element(self):
        """
        获取验证图片对象，就是验证码的点击区域
        :return: 图片对象
        """
        element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'touclick')))
        return element
    
    def get_position(self):
        """
        从节点对象，获取验证码位置
        :return: 验证码位置元组
        """
        element = self.get_touclick_element()
        time.sleep(2)
        location = element.location
        size = element.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)
    
    def get_screenshot(self):
        """
        根据验证码位置，获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot
    
    def get_touclick_image(self, name='captcha.png'):
        """
        保存验证码图片到本地
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha
    
    def get_points(self, captcha_result):
        """
        {'err_no': 0, 'err_str': 'OK', 'pic_id': '9069220022448500002', 'pic_str': '208,75|269,156', 'md5': 'a2175369130a2ca56a77573cbf5cc7dc'}
        解析识别结果，就是解析超级鹰返回的数据
        :param captcha_result: 识别结果
        :return: 转化后的结果
        """
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations
    
    def touch_click_words(self, locations):
        """
        点击验证图片
        :param locations: 点击位置
        :return: None
        """
        for location in locations:
            print(location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_touclick_element(), location[0],
                                                                   location[1]).click().perform()
            time.sleep(1)
    
    def login(self):
        """
        登录
        :return: None
        """
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginSub')))
        submit.click()
        time.sleep(10)
    
    def crack(self):
        """
        破解入口
        :return: None
        """
        self.open()

        # 获取验证码图片
        image = self.get_touclick_image()
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG')

        # 识别验证码
        result = self.chaojiying.post_pic(bytes_array.getvalue(), CHAOJIYING_KIND)
        print(result)

        # 解析识别结果
        locations = self.get_points(result)

        # 进行点击图片
        self.touch_click_words(locations)
        time.sleep(2)

        # 点击登陆
        self.login()

        # 判断是否出现用户信息
        try:
            success = self.wait.until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'welcome-name'), '你的名字'))
            print(success)

            cc = self.browser.find_element_by_class_name('welcome-name')
            print(cc.text)

        except TimeoutException:
            # 如果失败了超级鹰会返回分值
            self.chaojiying.report_error(result['pic_id'])
            self.crack()


if __name__ == '__main__':
    crack = CrackTouClick()
    crack.crack()
