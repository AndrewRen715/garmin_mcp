#!/usr/bin/env python3
"""
攀岩日记自动化更新脚本
1. 拉取 Garmin 攀岩记录
2. 更新攀岩训练日记.md
3. 自动生成 HTML
"""
import os
import sys
import re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 获取脚本所在目录的父目录作为基础路径
base_dir = os.path.dirname(os.path.abspath(__file__))

# 添加 src 路径
src_path = os.path.join(base_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 配置路径（使用相对路径）
MD_PATH = os.path.join(base_dir, '攀岩训练日记.md')
HTML_PATH = os.path.join(base_dir, '攀岩训练日记.html')

def init_garmin_api():
    """初始化 Garmin API"""
    try:
        from garmin_mcp import init_api
        os.environ['GARMIN_CN'] = 'true'
        return init_api(None, None, is_cn=True)
    except Exception as e:
        print(f"初始化 Garmin API 失败: {e}")
        return None

# 从公共模块导入攀岩工具函数
from garmin_mcp.climbing_utils import get_climbing_activities, format_duration

def get_existing_dates(md_content):
    """获取已存在的训练日期"""
    dates = []
    pattern = r'### (\d{4}-\d{2}-\d{2})'
    for match in re.finditer(pattern, md_content):
        dates.append(match.group(1))
    return set(dates)

def generate_training_entry(activity):
    """生成训练记录条目"""
    date_str = activity['date']
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekdays[date_obj.weekday()]
    
    activity_type = "难度攀岩" if activity['type'] != 'bouldering' else "抱石"
    
    entry = f"""### {date_str} ({weekday}) - ???

**🎯 训练类型**: {activity_type} (Indoor Climbing)\\
**📊 Garmin**: {activity['duration_formatted']} | 平均 {activity['avg_hr']} BPM | 最大 {activity['max_hr']} BPM | {activity['calories']} kcal | 爬升 {activity['elevation_gain']}m

#### 📋 训练内容

> ⏳ *待补充：训练地点、完成的线路、训练感受等*

#### ❓ 待补充信息

- 📍 **地点**: 在哪个攀岩馆？
- 🧗 **完成线路**: 完成了哪些难度？
- 💪 **训练内容**: 主要练了什么？
- 💭 **训练感受**: 技术进步 or 遇到瓶颈？
- 🏆 **是否有突破**: 有没有完成之前没过的线路？

***"""
    return entry

def update_md_file(new_activities):
    """更新 Markdown 文件"""
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    existing_dates = get_existing_dates(content)
    new_entries = []
    
    for activity in new_activities:
        if activity['date'] not in existing_dates:
            new_entries.append(activity)
    
    if not new_entries:
        print("没有新的攀岩活动需要更新")
        return []
    
    pattern = r'(## 📝 详细训练记录\n\n\*\*\*\n\n)(### \d{4}-\d{2}-\d{2})'
    new_content = ""
    
    for activity in new_entries:
        entry = generate_training_entry(activity)
        new_content += entry + "\n\n"
    
    content = re.sub(pattern, r'\1' + new_content + r'\2', content)
    
    total_count = len(existing_dates) + len(new_entries)
    content = re.sub(r'总训练次数": (\d+) 次', f'总训练次数": {total_count} 次', content)
    
    latest_date = new_entries[0]['date']
    content = re.sub(r'最新训练": \d{4}-\d{2}-\d{2}', f'最新训练": {latest_date}', content)
    
    if new_entries:
        table_header = "| #  | 日期         | 类型      | 时长     | 心率      | 地点         | 关键进展                      |\n| -- | ---------- | ------- | ------ | ------- | ---------- | ------------------------- |\n"
        new_rows = ""
        for i, activity in enumerate(new_entries):
            rank = total_count - i
            new_rows += f"| {rank} | {activity['date']} | 难度      | {int(activity['duration']/60)}min | {activity['avg_hr']}/{activity['max_hr']} | ???         | ⏳ 待补充                     |\n"
        
        content = re.sub(re.escape(table_header), table_header + new_rows, content, count=1)
    
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已添加 {len(new_entries)} 条新记录")
    return new_entries

def generate_html():
    """调用外部模块生成 HTML"""
    try:
        from md_to_html import generate_html as md_generate_html
        md_generate_html(MD_PATH, HTML_PATH)
    except ImportError:
        print("无法导入 md_to_html 模块，跳过 HTML 生成")

def main():
    """主函数"""
    print("=== 攀岩日记自动化更新 ===")
    
    print("1. 连接 Garmin Connect...")
    garmin_client = init_garmin_api()
    
    if garmin_client:
        print("2. 获取最近攀岩活动...")
        activities = get_climbing_activities(garmin_client, days=30)
        print(f"   发现 {len(activities)} 条攀岩活动")
        
        print("3. 更新攀岩训练日记.md...")
        update_md_file(activities)
    else:
        print("无法连接 Garmin，跳过数据拉取")
    
    print("4. 生成攀岩训练日记.html...")
    generate_html()
    
    print("=== 更新完成 ===")

if __name__ == "__main__":
    main()