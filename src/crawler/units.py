from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
from time import sleep
from common.logger import log

def get_units_data():
    result = []
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
        url = "https://www.metatft.com/units"
        log.info("开始访问英雄页面...")
        try:
            driver.get(url)
        except TimeoutException:
            log.info("加载超时，继续执行...")
            
        log.info("加载完成")
        # 切换语言到中文
        lang_btn = driver.find_element(By.CLASS_NAME, "LanguageLabel")
        lang_btn.click()
        sleep(1)
        log.info("点击切换语言菜单")
        lang_btn_list = driver.find_elements(By.CLASS_NAME, "LanguageLabel")
        zh_btn = lang_btn_list[-3]  # 中文选项
        log.info(f"切换至 {zh_btn.text}")
        zh_btn.click()
        sleep(3)
        log.info("切换成中文")
        
        # 等待表格加载
        table_xpath = '//*[@id="content-wrap"]/div[1]/div[2]/div[2]/div/div[3]/figure/table/tbody'
        WebDriverWait(driver, 10000).until(
            EC.presence_of_element_located((By.XPATH, table_xpath))
        )
        
        # 获取所有英雄链接
        unit_links = driver.find_elements(By.CLASS_NAME, "StatLink")
        
        for link in unit_links:
            href = link.get_attribute('href')
            english_name = link.text.strip()

            if href and english_name:
                result.append({
                    'name': english_name,
                    'href': href
                })
                
        log.info(f"统计得到{len(result)}个英雄单位")

        # 保存数据
        with open('../../data/stat/units.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result
        
    except Exception as e:
        log.error(f"发生错误: {str(e)}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    get_units_data()
