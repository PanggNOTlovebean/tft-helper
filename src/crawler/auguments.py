from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json
from time import sleep
from common.logger import log
def get_augments_data():
    result = {}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    # 设置页面加载超时时间
    driver.set_page_load_timeout(100)
    
    try:
        url = "https://www.metatft.com/augments"
        log.info("开始访问页面...")
        try:
            driver.get(url)
        except TimeoutException:
            log.info("加载超时，继续执行...")
        # sleep(10)
        log.info("加载完成")
        lang_btn = driver.find_element(By.CLASS_NAME, "LanguageLabel")
        lang_btn.click()
        sleep(1)
        log.info("点击切换语言菜单")
        lang_btn_list = driver.find_elements(By.CLASS_NAME, "LanguageLabel")
        zh_btn = lang_btn_list[-4]
        log.info(f"切换至 {zh_btn.text}")
        zh_btn.click()
        sleep(3)
        log.info("切换成中文")
        tier_list_row = driver.find_elements(By.CLASS_NAME, "TierListRow")
        tier = ('S', 'A', 'B', 'C', 'D')
        for tier, row in zip(tier, tier_list_row):
            augment_list = row.find_elements(By.CLASS_NAME, "AugmentLabel")
            for augment in augment_list:
                name = ''.join(char for char in augment.text if '\u4e00' <= char <= '\u9fff' or char in '+ICD')
                result[name] = tier
        log.info(f"统计得到{len(result)}个强化符文")

        with open('../../data/stat/augments.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return driver.page_source
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_augments_data()
