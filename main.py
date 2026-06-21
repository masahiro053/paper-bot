import os
import time
import requests
import random
import xml.etree.ElementTree as ET
from google import genai
import config

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID')

def load_history(filepath):
    """過去の送信済み論文IDリストを読み込む"""
    if not os.path.exists(filepath):
        return set()
    with open(filepath, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_history(filepath, new_ids):
    """新しく送信した論文IDを履歴ファイルに追記する"""
    with open(filepath, "a", encoding="utf-8") as f:
        for paper_id in new_ids:
            f.write(f"{paper_id}\n")

def build_arxiv_query(major_kws, minor_kws):
    major_query = "(" + " OR ".join([f'all:"{k}"' for k in major_kws]) + ")"
    minor_query = "(" + " OR ".join([f'all:"{k}"' for k in minor_kws]) + ")"
    return f"{major_query} AND {minor_query}"

def fetch_arxiv_papers(query, fetch_count=15):
    """指定した件数（少し多め）の論文データを取得する"""
    url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "start": random.randint(0, 10),
        "max_results": fetch_count,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    headers = {"User-Agent": "DailyArxivBot/1.0"}
    
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

def summarize_paper(paper_data, client):
    prompt = config.PROMPT_TEMPLATE.format(
        title=paper_data['title'],
        abstract=paper_data['abstract']
    )
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return response.text

def send_to_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    payload = {"to": LINE_USER_ID, "messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)

def main():
    if not all([GEMINI_API_KEY, LINE_CHANNEL_ACCESS_TOKEN, LINE_USER_ID]):
        print("環境変数が設定されていません。")
        return
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # 1. 履歴の読み込み
    history_ids = load_history(config.HISTORY_FILE)
    
    # 2. 論文を少し多め（20件）に取得
    query = build_arxiv_query(config.MAJOR_KEYWORDS, config.MINOR_KEYWORDS)
    papers = fetch_arxiv_papers(query, fetch_count=50)
    
    new_papers_count = 0
    new_sent_ids = []
    
    # 3. 取得した論文を1件ずつチェック
    for paper in papers:
        if paper['id'] in history_ids:
            continue
            
        # 💡 APIの混雑エラー（503）などをキャッチしてスキップする処理を追加
        try:
            summary = summarize_paper(paper, client)
        except Exception as e:
            print(f"⚠️ 論文 '{paper['title']}' の要約中にAPIエラーが発生したためスキップします: {e}")
            continue # この論文は諦めて、次の論文の処理へ進む
        
        msg = (f"📚 論文速報 ({new_papers_count+1}/{config.NUM_PAPERS})\n━━━━━━━━━━━━\n"
               f"💡 {paper['title']}\n📅 {paper['year']}\n━━━━━━━━━━━━\n\n"
               f"{summary}\n\n🔗 原文リンク\n{paper['id']}")
               
        send_to_line(msg)
        
        # 新しく送ったリストに追加
        new_sent_ids.append(paper['id'])
        new_papers_count += 1
        
        # 設定した件数に達したらループを終了
        if new_papers_count >= config.NUM_PAPERS:
            break
            
        time.sleep(5)
        
    # 4. 新しく送った論文があれば、履歴ファイルに追記して保存
    if new_sent_ids:
        save_history(config.HISTORY_FILE, new_sent_ids)
        print(f"{len(new_sent_ids)}件の新規論文を送信し、履歴を更新しました。")
    else:
        print("新しい論文はありませんでした。")

if __name__ == "__main__":
    main()