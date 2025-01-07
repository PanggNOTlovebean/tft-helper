from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json
from time import sleep
from common.logger import log

def get_items_data():
    # 读取英雄数据
    with open('../../data/stat/unit_url.json', 'r', encoding='utf-8') as f:
        units = json.load(f)
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.set_page_load_timeout(100)
    
    result = {}
    
    try:
        for unit in units:
            unit_name = unit['name']
            url = unit['href']
            log.info(f"开始获取 {unit_name} 的装备数据...")
            
            try:
                driver.get(url)
                sleep(2)  # 等待页面加载
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
                
                unit_data = {
                    'recommended_builds': [],
                    'top_items': []
                }
                
                # 获取推荐装备组合
                build_rows = driver.find_elements(By.CLASS_NAME, "ItemHolderRow")
                log.info(f"开始获取 {unit_name} 的推荐装备组合...")
                
                for idx, row in enumerate(build_rows[:5], 1):  # 只取前5个组合
                    build = {
                        'items': [],
                        'avg_place': '',
                        'place_change': '',
                        'play_rate': ''
                    }
                    
                    # 获取装备名称
                    items = row.find_elements(By.CLASS_NAME, "TableItemImg")
                    for item in items:
                        build['items'].append(item.get_attribute('alt'))
                    
                    # 获取统计数据
                    stats = row.find_elements(By.CLASS_NAME, "ItemHolderStatNum")
                    if len(stats) >= 2:
                        build['avg_place'] = stats[0].text
                        build['place_change'] = stats[1].text
                    
                    play_rate = row.find_element(By.CLASS_NAME, "ItemHolderStatNumPercent")
                    build['play_rate'] = play_rate.text
                    
                    unit_data['recommended_builds'].append(build)
                    log.info(f"已获取第 {idx} 个装备组合: {', '.join(build['items'])}")
                    log.info(f"平均名次: {build['avg_place']}, 名次变化: {build['place_change']}, 使用率: {build['play_rate']}")
                
                # 获取单件装备数据
                log.info(f"开始获取 {unit_name} 的单件装备数据...")
                top_items = driver.find_elements(By.CSS_SELECTOR, ".UnitDetailStatsItem .ItemHolderRow")
                
                for item_row in top_items:
                    item = {
                        'name': '',
                        'avg_place': '',
                        'place_change': '',
                        'play_rate': ''
                    }
                    
                    img = item_row.find_element(By.CLASS_NAME, "ItemHolderImg")
                    item['name'] = img.get_attribute('alt')
                    
                    stats = item_row.find_elements(By.CLASS_NAME, "ItemHolderStatNum")
                    if len(stats) >= 2:
                        item['avg_place'] = stats[0].text
                        item['place_change'] = stats[1].text
                    
                    play_rate = item_row.find_element(By.CLASS_NAME, "ItemHolderStatNumPercent")
                    item['play_rate'] = play_rate.text
                    
                    log.info(f"已获取装备: {item['name']}, 平均名次: {item['avg_place']}, 名次变化: {item['place_change']}, 使用率: {item['play_rate']}")
                    
                    unit_data['top_items'].append(item)
                
                result[unit_name] = unit_data
                log.info(f"✅ {unit_name} 数据获取完成 - 共获取 {len(unit_data['recommended_builds'])} 个装备组合和 {len(unit_data['top_items'])} 个单件装备")
                
            except Exception as e:
                log.error(f"获取 {unit_name} 数据时发生错误: {str(e)}")
                continue
        
        # 保存数据
        with open('../../data/stat/unit_items.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        log.error(f"发生错误: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_items_data()
