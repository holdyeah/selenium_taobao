import random
import time
import pickle
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import csv

# 指定ChromeDriver的完整路径
driver_path = r'C:\Users\zhang\Desktop\项目\qq\chromedriver.exe'  # 替换为您的 chromedriver 实际路径

# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速（可选）

# 初始化 WebDriver
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 修改 navigator.webdriver 属性为 false
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
    """
})

def save_cookies(driver, path):
    """保存当前浏览器会话中的所有cookies"""
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookies(driver, path, url):
    """加载之前保存的cookies"""
    driver.get(url)  # 必须先访问目标网站才能设置其cookies
    if os.path.exists(path):
        with open(path, 'rb') as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                driver.add_cookie(cookie)


def scroll_to_bottom(driver):
    """将鼠标移动到页面的左下方，点击一下，然后模拟滚轮下滚动"""
    try:
        # 创建 ActionChains 对象
        actions = ActionChains(driver)

        # 获取页面尺寸
        window_size = driver.get_window_size()
        window_width = window_size['width']
        window_height = window_size['height']

        # 计算页面四分之一的位置（从左上角开始）
        quarter_width = window_width // 4
        quarter_height = window_height // 4

        # 移动鼠标到页面四分之一位置
        actions.move_by_offset(quarter_width, quarter_height).perform()
        print("已将鼠标移动到页面四分之一位置")

        # 模拟用户点击
        actions.click().perform()
        print("已在页面四分之一位置点击")

        # 暂停一段时间以确保点击生效
        time.sleep(random.uniform(0.5, 1))

        # 模拟滚轮滚动
        actions.scroll_by_amount(0, 1600).perform()  # 向下滚动 600 像素
        print("已完成模拟滚轮下滚动")

        # 暂停一段时间以确保滚动生效
        time.sleep(random.uniform(1, 3))

    except Exception as e:
        print(f"处理过程中出错: {e}")



def read_reviews(driver, product_name):
    """读取当前页面上的所有评价"""
    reviews = []

    # 定义CSS选择器模板用于匹配所有评价项
    # review_container_css = '[class*="leftDrawer--"][class*="content--"][class*="Comments--"][class*="clearfix"][class*="comments--"][class*="beautify-scroll-bar"]'
    review_container_css = '[class*="leftDrawer--"]'
    review_item_css = '[class*="Comment--"]'
    header_css = '[class*="header--"]'
    avatar_css = '[class*="avatar--"] img'
    user_info_css = '[class*="userInfo--"]'
    user_name_css = '[class*="userName--"] span'
    meta_css = '[class*="meta--"]'
    like_css = '[class*="like--"] button span'
    content_wrapper_css = '[class*="contentWrapper--"]'
    content_css = '[class*="content--"]'
    album_css = '[class*="album--"] div'

    try:
        # 等待评价容器出现
        wait = WebDriverWait(driver, 10)
        print("等待评价容器加载...")
        review_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, review_container_css)))
        print(f"找到评价容器: {review_container}")

        # 获取所有评价项
        review_items = review_container.find_elements(By.CSS_SELECTOR, review_item_css)
        print(f"找到 {len(review_items)} 条评价")

        for idx, item in enumerate(review_items, start=1):
            review = {}
            
            try:
                # 获取ID（用户名）
                try:
                    id_element = item.find_element(By.CSS_SELECTOR, user_name_css)
                    review['ID'] = id_element.get_attribute('textContent').strip() if id_element else None
                except NoSuchElementException:
                    review['ID'] = None

                # 获取meta信息（例如用户名、评价时间等）
                try:
                    meta_element = item.find_element(By.CSS_SELECTOR, meta_css)
                    review['meta'] = meta_element.get_attribute('textContent').strip() if meta_element else None
                except NoSuchElementException:
                    review['meta'] = None

                # 获取点赞数
                try:
                    like_count_text = item.find_element(By.CSS_SELECTOR, like_css)
                    review['likeCountText'] = like_count_text.get_attribute('textContent').strip() if like_count_text else None
                except NoSuchElementException:
                    review['likeCountText'] = None
                
                # 获取内容
                try:
                    content_element = item.find_element(By.CSS_SELECTOR, content_css)
                    review['content'] = content_element.get_attribute('textContent').strip() if content_element else None
                except NoSuchElementException:
                    review['content'] = None
                
                # 获取相册（如果有）
                try:
                    album_element = item.find_element(By.CSS_SELECTOR, album_css)
                    review['album'] = album_element.get_attribute('innerHTML') if album_element else None
                except NoSuchElementException:
                    review['album'] = None
                
                # 获取头像
                try:
                    avatar_element = item.find_element(By.CSS_SELECTOR, avatar_css)
                    review['avatar'] = avatar_element.get_attribute('src') if avatar_element else None
                except NoSuchElementException:
                    review['avatar'] = None
                
                # 添加商品名称
                review['product_name'] = product_name
                
                reviews.append(review)
                print(f"已读取评价: {review}")
                
            except Exception as e:
                print(f"处理第 {idx} 条评价时出错: {e}")
                continue

    except (NoSuchElementException, TimeoutException) as e:
        print(f"读取评价时出错: {e}")

    return reviews

def write_reviews_to_csv(reviews, filename='reviews.csv'):
    """将评价信息写入CSV文件"""
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        headers = ['Product Name', 'ID', 'Meta', 'Like Count', 'Content', 'Album', 'Avatar']
        writer.writerow(headers)  # 写入表头
        
        for review in reviews:
            row = [
                review['product_name'],
                review['ID'],
                review['meta'],
                review['likeCountText'],
                review['content'],
                review['album'] or '',  # 如果没有相册，则为空字符串
                review['avatar']
            ]
            writer.writerow(row)


def navigate_and_handle_windows(driver, target_element_xpath):
    """根据指定XPath读取href属性并导航，处理可能的新窗口"""
    try:
        # 查找目标元素
        target_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, target_element_xpath))
        )
        
        # 获取href属性值
        href_value = target_element.get_attribute('href')
        if href_value:
            print(f"找到链接: {href_value}")
            
            # 记录当前窗口句柄
            original_window = driver.current_window_handle
            original_windows = driver.window_handles
            
            # 使用获取到的URL进行导航
            driver.get(href_value)
            print("已根据href导航至新页面")
            
            # 等待一段时间以确保页面加载完成（可选）
            time.sleep(2)  # 根据需要调整等待时间

            # 检查是否有新窗口出现
            try:
                wait.until(lambda d: len(d.window_handles) > len(original_windows))
                new_window = [window for window in driver.window_handles if window not in original_windows][0]

                # 切换到新窗口
                driver.switch_to.window(new_window)
                print(f"已切换到新窗口: {new_window}")

                # 如果有需要，可以在这里处理新窗口的内容
            except TimeoutException:
                print("没有检测到新窗口，继续在当前窗口操作")
                # 继续在当前窗口操作
                driver.switch_to.window(original_window)  # 确保仍在原始窗口中操作

            return True
        else:
            print("未找到有效的href属性")
            return False
    except Exception as e:
        print(f"导航或处理窗口过程中发生错误: {e}")
        return False



def scroll_to_element(driver, element):
    """滚动到指定元素位置"""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

def navigate_items_by_href(driver, xpath_template):
    """查找所有符合条件的商品项，读取其 href 属性并导航"""
    try:
        all_reviews = []  # 存储所有商品项的评价信息
        # 确保页面已经完全加载
        wait = WebDriverWait(driver, 60)
        
        # 查找所有符合条件的商品项
        elements = driver.find_elements(By.XPATH, xpath_template)
        print(f"找到 {len(elements)} 个符合条件的商品项")

        for index, element in enumerate(elements):
            try:
                # 滚动到元素位置以确保它在视口内
                scroll_to_element(driver, element)
                
                # 获取元素的 href 属性值
                href_value = element.get_attribute('href')
                if href_value:
                    print(f"第 {index + 1} 个商品项的链接: {href_value}")

                    # 使用获取到的URL进行导航
                    driver.get(href_value)
                    print(f"已根据href导航至新页面: {href_value}")

                    time.sleep(60)
                    # 获取商品名称
                    product_name_element = driver.find_element(By.XPATH, '//*[@id="ice-container"]/div/div[2]/div[1]/div[1]/a/div[1]/div[2]/span')  # 假设商品名称位于此XPath下
                    product_name = product_name_element.text if product_name_element else 'Unknown Product'
                    print(f"商品名称: {product_name}")

                    # 点击“全部评价”按钮
                    all_reviews_button_xpath = '//*[@id="ice-container"]/div/div[2]/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/div/div[4]/div'
                    all_reviews_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, all_reviews_button_xpath))
                    )
                    all_reviews_button.click()
                    print("成功点击了‘全部评价’按钮")

                    # 模拟用户点击“全部评价”按钮后的思考时间
                    think_time = random.uniform(10, 30)  # 点击按钮后思考1到3秒
                    time.sleep(think_time)

                    # 滚动加载所有评价
                    scroll_to_bottom(driver)

                    # 读取所有评价
                    reviews = read_reviews(driver, product_name)
                    all_reviews.extend(reviews)
                    print(f"共读取到 {len(reviews)} 条评价")


                    # 模拟用户处理完一个商品后的休息时间
                    rest_time = random.uniform(2, 5)  # 商品间休息2到5秒
                    time.sleep(rest_time)
                        
                else:
                    print(f"第 {index + 1} 个商品项未找到有效的href属性")
            except Exception as e:
                print(f"处理第 {index + 1} 个商品项时发生错误: {e}")
                break

                # 将所有评价信息写入CSV文件
        write_reviews_to_csv(all_reviews)
        print(f"所有评价已成功写入CSV文件")
    except Exception as e:
        print(f"查找或处理商品项过程中发生错误: {e}")

try:
    # 设置浏览器窗口为全屏
    driver.maximize_window()  # 设置窗口最大化

    # 定义cookies保存路径
    cookies_path = 'my_cookies.pkl'
    login_url = "https://login.taobao.com/member/login.jhtml"

    # 如果已经有保存的cookies，则尝试加载它们
    load_cookies(driver, cookies_path, login_url)

    # 访问淘宝登录页面
    driver.get(login_url)

    # 使用显式等待代替固定的 sleep
    wait = WebDriverWait(driver, 30)

    # 检查是否已经登录
    try:
        # 尝试查找表明已登录的元素（例如用户昵称或欢迎信息）
        user_nickname = wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "nick")]')))
        print(f"检测到用户昵称: {user_nickname.text}")
    except TimeoutException:
        print("尚未登录，等待用户完成登录...")
        # 等待用户扫码登录等操作...
        wait.until(lambda d: any([
            d.current_url.startswith("https://www.taobao.com"),
            d.current_url.startswith("https://i.taobao.com"),  # 添加对个人中心URL的支持
            EC.presence_of_element_located((By.CLASS_NAME, 'site-nav-user'))(d)
        ]))

        # 登录完成后保存cookies
        save_cookies(driver, cookies_path)
        print("登录完成，cookies已保存.")
        print("用户已成功登录，正在导航到淘宝首页...")
        
        if not driver.current_url.startswith("https://www.taobao.com"):
            print("正在导航到淘宝首页...")
            driver.get("https://www.taobao.com/")
            wait.until(EC.url_to_be("https://www.taobao.com/"))
            print("已手动导航到淘宝首页")

        # 点击指定的元素，打开新窗口
        target_element_xpath = '//*[@id="ice-container"]/div[2]/div[2]/div[2]/div[1]/div/ul/li[5]/div[2]/div/div/div[1]/div[4]/a[11]'

        try:
            # 根据href属性导航
            if navigate_and_handle_windows(driver, target_element_xpath):
                original_windows = driver.window_handles  # 保存点击前的所有窗口句柄
                print("成功点击了目标元素")

                # 查找并点击所有符合条件的商品项
                xpath_template = '//*[@id[starts-with(., "item_id_")]]'  # 注意这里的 /a 是假设链接在 a 标签中
                    
                    # 查找所有符合条件的商品项并根据 href 导航
                navigate_items_by_href(driver, xpath_template)



        except TimeoutException:
            print(f"未能找到或点击目标元素 ({target_element_xpath})")
        
    except TimeoutException:
        print("未找到扫码登录选项，关闭浏览器")
        driver.quit()
        exit()

except Exception as e:
    print(f"遇到了错误: {e}")
    driver.quit()

finally:
    driver.quit()  # 确保浏览器实例被正确关闭