import requests
from bs4 import BeautifulSoup
import json

# 定义基本URL和页数范围
BASE_URL = "https://src.sjtu.edu.cn/rank/firm/0/?page="
PAGE_RANGE = range(1, 209)
CHUNK_SIZE = 500

# 定义敏感词列表
SENSITIVE_WORDS = ["众测", "解放军"]

def fetch_data(page_num):
    url = BASE_URL + str(page_num)
    print(f"访问URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='am-table')
    
    if table:
        rows = table.find_all('tr')[1:]  # 跳过表头行
        page_data = []
        for row in rows:
            columns = row.find_all('td')
            if columns:
                rank = columns[0].text.strip()
                name = columns[1].a.text.strip()
                total_vulnerabilities = columns[2].text.strip()
                threat_value = columns[3].text.strip()
                
                entry = {
                    "Rank": rank,
                    "Name": name,
                    "Total Vulnerabilities": total_vulnerabilities,
                    "Threat Value": threat_value
                }
                page_data.append(entry)
        
        return page_data
    else:
        return []

def save_data_to_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# 步骤1: 获取数据
all_data = []
for page_num in PAGE_RANGE:
    page_data = fetch_data(page_num)
    all_data.extend(page_data)
    print("获取到的数据:", page_data)

# 保存所有数据到JSON文件
save_data_to_json('table_data.json', all_data)
print("数据已成功爬取并保存为table_data.json文件")

# 步骤2: 数据清洗和格式处理
def filter_sensitive_words(text, sensitive_words):
    for word in sensitive_words:
        text = text.replace(word, '')
    return text

cleaned_data = [filter_sensitive_words(item['Name'], SENSITIVE_WORDS) for item in all_data if 'Name' in item and '众测' not in item['Name']]

formatted_data = [{
    "id": f"{item}:company",
    "label": item,
    "type": "company",
    "attributes": {
        "type": "company",
        "name": item
    },
    "interface": {
        "17": 2
    }
} for item in cleaned_data]

# 分割数据并保存到多个JSON文件
num_chunks = len(formatted_data) // CHUNK_SIZE + (len(formatted_data) % CHUNK_SIZE > 0)
for i in range(num_chunks):
    start = i * CHUNK_SIZE
    end = (i + 1) * CHUNK_SIZE
    chunk = formatted_data[start:end]

    filename = f'formatted_data_{i + 1}.json'
    save_data_to_json(filename, chunk)

print(f"数据已成功分割成{num_chunks}个文件")
