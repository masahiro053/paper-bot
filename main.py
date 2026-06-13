import os
import time
import requests
import random
import xml.etree.ElementTree as ET
from google import genai

# 作成した設定ファイルを読み込む
import config

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID')

def build_arxiv_query(major_kws, minor_kws):
    """大カテゴリと小カテゴリを掛け合わせた検索クエリを作成する"""
    major_parts = [f'all:"{k}"' for k in major_kws]
    minor_parts = [f'all:"{k}"' for k in minor_kws]
    
    major_query = "(" + " OR ".join(major_parts) + ")"
    minor_query = "(" + " OR ".join(minor_parts) + ")"
    
    return f"{major_query} AND {minor_query}"

def fetch_arxiv_papers(query, num_papers):
    """arXiv APIから本物の論文データを取得する"""
    url = "https://export.arxiv.org/api/query"
    random_start = random.randint(0, 10)
    
    params = {
        "search_query": query,
        "start": random_start,
        "max_results": num_papers,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    headers = {
        "User-Agent": "DailyArxivBot/1.0"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            papers.append({
                'title': entry.find('atom:title', ns).text.replace('\n', ' ').strip(),
                'abstract': entry.find('atom:summary', ns).text.replace('\n', ' ').strip(),
                'year': entry.find('atom:published', ns).text[:10],
                'id': entry.find('atom:id', ns).text
            })
        return papers
    except Exception as e:
        print(f"Fetch error: {e}")
        return []

def summarize_paper(paper_data, client):
    """config.pyからプロンプトを読み込み要約を生成する"""
    # config.pyのテンプレートに、実際のタイトルと概要を埋め込む
    prompt = config.PROMPT_TEMPLATE.format(
        title=paper_data['title'],
        abstract=paper_data['abstract']
    )
    
    try:
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "⚠️ 要約生成に失敗しました。"

def send_to_line(message):
    """LINEにメッセージを送信する"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    payload = {"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)

def main():
    if not all([GEMINI_API_KEY, LINE_CHANNEL_ACCESS_TOKEN, LINE_USER_ID]):
        print("環境変数が設定されていません。")
        return
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # configからキーワードを読み込んで検索クエリを作成
    query = build_arxiv_query(config.MAJOR_KEYWORDS, config.MINOR_KEYWORDS)
    print(f"Searching for: {query}")
    
    # configから取得件数を読み込んで論文を取得
    papers = fetch_arxiv_papers(query, config.NUM_PAPERS)
    
    if not papers:
        send_to_line("⚠️ 条件に合致する最新論文が見つかりませんでした。")
        return
        
    for i, paper in enumerate(papers):
        summary = summarize_paper(paper, client)
        
        msg = (f"📚 論文速報 ({i+1}/{config.NUM_PAPERS})\n"
               f"━━━━━━━━━━━━\n"
               f"💡 {paper['title']}\n"
               f"📅 {paper['year']}\n"
               f"━━━━━━━━━━━━\n\n"
               f"{summary}\n\n"
               f"🔗 原文リンク\n{paper['id']}")
               
        send_to_line(msg)
        time.sleep(5)

if __name__ == "__main__":
    main()