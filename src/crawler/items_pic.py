from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
import os
from time import sleep
from common.logger import log

def download_items_pics():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.set_page_load_timeout(100)
    
    try:
        # 访问装备页面
        url = "https://www.metatft.com/items"
        driver.get(url)
        sleep(2)
        log.info(f"正在访问页面: {url}")
        
        # 切换为中文
        lang_btn = driver.find_element(By.CLASS_NAME, "LanguageLabel")
        lang_btn.click()
        sleep(1)
        lang_btn_list = driver.find_elements(By.CLASS_NAME, "LanguageLabel")
        zh_btn = lang_btn_list[-4]
        zh_btn.click()
        sleep(2)
        log.info("已切换为中文界面")
        
        # 创建图片保存目录
        save_dir = "../../data/items"
        os.makedirs(save_dir, exist_ok=True)
        
        # 获取表格中的装备信息
        table = driver.find_element(By.XPATH, '//*[@id="content-wrap"]/div[1]/div[2]/div[2]/div/div[3]/figure/table')
        items = table.find_elements(By.CSS_SELECTOR, ".StatLink img.TableItemImg")
        log.info(f"在表格中找到 {len(items)} 个装备")
        
        for item in items:
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    name = item.get_attribute('alt')
                    img_url = item.get_attribute('src')
                    
                    if not name or not img_url:
                        break
                        
                    # 下载图片
                    img_path = os.path.join(save_dir, f"{name}.png")
                    if not os.path.exists(img_path):
                        response = requests.get(img_url)
                        if response.status_code == 200:
                            with open(img_path, 'wb') as f:
                                f.write(response.content)
                            log.info(f"已保存装备图片: {name}")
                            break  # 下载成功，退出重试循环
                        else:
                            log.error(f"下载图片失败: {name}, 状态码: {response.status_code}")
                    else:
                        log.info(f"装备图片已存在: {name}")
                        break  # 图片已存在，无需重试
                        
                except Exception as e:
                    retry_count += 1
                    # 获取当前处理的装备名称（如果可用）
                    current_item_name = item.get_attribute('alt') if item else "未知装备"
                    if retry_count < max_retries:
                        log.warning(f"处理装备 '{current_item_name}' 时发生错误: {str(e)}，正在进行第 {retry_count} 次重试")
                        sleep(1)  # 重试前等待1秒
                    else:
                        log.error(f"处理装备 '{current_item_name}' 失败，已重试 {max_retries} 次: {str(e)}")
                    continue
                
    except Exception as e:
        log.error(f"发生错误: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    download_items_pics()
