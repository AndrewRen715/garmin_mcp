#!/usr/bin/env python3
"""
优化版 Markdown 转 HTML - 修复空白页面和显示问题
"""
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def parse_markdown(md_content):
    """解析 Markdown 内容，生成结构化数据"""
    lines = md_content.split('\n')
    blocks = []
    current_block = None
    
    for line in lines:
        # 标题
        if line.startswith('# '):
            if current_block:
                blocks.append(current_block)
            blocks.append({'type': 'h1', 'content': line[2:]})
            current_block = None
        elif line.startswith('## '):
            if current_block:
                blocks.append(current_block)
            blocks.append({'type': 'h2', 'content': line[3:]})
            current_block = None
        elif line.startswith('### '):
            if current_block:
                blocks.append(current_block)
            blocks.append({'type': 'h3', 'content': line[4:]})
            current_block = None
        # 分隔线
        elif line.startswith('***') or line.startswith('---'):
            if current_block:
                blocks.append(current_block)
            blocks.append({'type': 'hr'})
            current_block = None
        # 表格
        elif line.startswith('|'):
            if current_block and current_block['type'] != 'table':
                blocks.append(current_block)
                current_block = {'type': 'table', 'rows': []}
            elif not current_block:
                current_block = {'type': 'table', 'rows': []}
            current_block['rows'].append(line)
        # 列表项
        elif line.startswith('- '):
            if current_block and current_block['type'] != 'list':
                blocks.append(current_block)
                current_block = {'type': 'list', 'items': []}
            elif not current_block:
                current_block = {'type': 'list', 'items': []}
            
            # 检查是否是任务列表
            if line.startswith('- [x] '):
                current_block['items'].append({'content': line[6:], 'completed': True})
            elif line.startswith('- [ ] '):
                current_block['items'].append({'content': line[6:], 'completed': False})
            else:
                current_block['items'].append({'content': line[2:], 'completed': None})
        # 普通段落
        else:
            if not current_block:
                current_block = {'type': 'p', 'content': ''}
            if current_block['type'] == 'p':
                current_block['content'] += (line + '\n')
    
    if current_block:
        blocks.append(current_block)
    
    return blocks

def blocks_to_html(blocks):
    """将结构化数据转换为 HTML"""
    html_parts = []
    
    for block in blocks:
        if block['type'] == 'h1':
            html_parts.append(f'<h1>{escape_html(block["content"])}</h1>')
        elif block['type'] == 'h2':
            html_parts.append(f'<h2>{escape_html(block["content"])}</h2>')
        elif block['type'] == 'h3':
            html_parts.append(f'<h3>{escape_html(block["content"])}</h3>')
        elif block['type'] == 'hr':
            html_parts.append('<hr class="divider">')
        elif block['type'] == 'table':
            html_parts.append(convert_table(block['rows']))
        elif block['type'] == 'list':
            html_parts.append(convert_list(block['items']))
        elif block['type'] == 'p':
            content = block['content'].strip()
            if content:
                content = process_inline(content)
                html_parts.append(f'<p>{content}</p>')
    
    return '\n'.join(html_parts)

def escape_html(text):
    """转义 HTML 特殊字符"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def process_inline(text):
    """处理行内元素"""
    # 粗体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # 斜体
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # 链接
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # 代码
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

def convert_table(rows):
    """转换表格"""
    if len(rows) < 2:
        return ''
    
    html = '<table class="data-table">\n'
    
    # 解析表头
    header_cells = [c.strip() for c in rows[0].split('|')[1:-1]]
    
    # 检查第二行是否是分隔线
    is_header_separator = len(rows) > 1 and all('---' in cell for cell in rows[1].split('|')[1:-1])
    
    html += '  <thead>\n    <tr>\n'
    for cell in header_cells:
        html += f'      <th>{escape_html(cell)}</th>\n'
    html += '    </tr>\n  </thead>\n  <tbody>\n'
    
    start_row = 2 if is_header_separator else 1
    
    for row in rows[start_row:]:
        cells = [c.strip() for c in row.split('|')[1:-1]]
        html += '    <tr>\n'
        for cell in cells:
            html += f'      <td>{process_inline(escape_html(cell))}</td>\n'
        html += '    </tr>\n'
    
    html += '  </tbody>\n</table>'
    return html

def convert_list(items):
    """转换列表"""
    html = '<ul>\n'
    for item in items:
        content = process_inline(escape_html(item['content']))
        if item['completed'] is True:
            html += f'  <li class="completed">✓ {content}</li>\n'
        elif item['completed'] is False:
            html += f'  <li class="pending">○ {content}</li>\n'
        else:
            html += f'  <li>{content}</li>\n'
    html += '</ul>'
    return html

def generate_html(md_path, html_path):
    """生成完整的 HTML 文件"""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    last_update = '未知'
    match = re.search(r'\*最后更新：(\d{4}-\d{2}-\d{2})', md_content)
    if match:
        last_update = match.group(1)
    
    blocks = parse_markdown(md_content)
    content_html = blocks_to_html(blocks)
    
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧗 攀岩训练日记</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            scroll-behavior: smooth;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 1.1em; }}
        
        .content {{ padding: 30px; }}
        
        h1 {{
            color: #2c3e50;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        h2 {{
            color: #34495e;
            font-size: 1.5em;
            margin: 25px 0 15px;
            padding-left: 10px;
            border-left: 4px solid #764ba2;
        }}
        
        h3 {{
            color: #4a6785;
            font-size: 1.3em;
            margin: 20px 0 12px;
        }}
        
        p {{
            line-height: 1.8;
            color: #555;
            margin-bottom: 15px;
        }}
        
        ul {{
            margin-left: 25px;
            margin-bottom: 15px;
        }}
        
        li {{
            line-height: 1.8;
            color: #555;
            padding: 5px 0;
        }}
        
        li.completed {{
            color: #27ae60;
            text-decoration: line-through;
        }}
        
        li.pending {{
            color: #f39c12;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .data-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
            color: #555;
        }}
        
        .data-table tr:hover td {{
            background: #f8f9fa;
        }}
        
        .data-table tr:last-child td {{
            border-bottom: none;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        em {{
            color: #7f8c8d;
            font-style: italic;
        }}
        
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 0.9em;
        }}
        
        a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        hr.divider {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #ddd, transparent);
            margin: 25px 0;
        }}
        
        pre {{
            background: #2c3e50;
            color: white;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 15px 0;
        }}
        
        pre code {{
            background: none;
            color: inherit;
            padding: 0;
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .container {{ border-radius: 10px; }}
            .content {{ padding: 15px; }}
            .data-table th, .data-table td {{ padding: 8px 10px; font-size: 0.9em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧗 攀岩训练日记</h1>
            <p>最后更新：{last_update} | 数据来源：Garmin Connect + 自我记录</p>
        </div>
        <div class="content">
            {content_html}
        </div>
    </div>
</body>
</html>'''
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ HTML 文件已生成: {html_path}")

if __name__ == "__main__":
    md_path = r"c:\Users\25646\TRAE\mcpserver\garmin_mcp\攀岩训练日记.md"
    html_path = r"c:\Users\25646\TRAE\mcpserver\garmin_mcp\攀岩训练日记.html"
    
    if len(sys.argv) >= 3:
        md_path = sys.argv[1]
        html_path = sys.argv[2]
    
    if not os.path.exists(md_path):
        print(f"❌ 错误：Markdown 文件不存在: {md_path}")
        sys.exit(1)
    
    generate_html(md_path, html_path)