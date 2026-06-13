import os
import time
import requests
import random
import xml.etree.ElementTree as ET
from google import genai

# ==========================================
# 設定エリア
# ==========================================
# 【大カテゴリ】対象とする業界やドメイン（いずれかを含む）
MAJOR_KEYWORDS = ["Advertising", "Marketing", "Ad Tech", "Generative AI", "Marketing Data"]

# 【小カテゴリ】具体的な技術や手法（いずれかを含む）
MINOR_KEYWORDS = ["Machine Learning", "Optimization", "Mix Modeling", 
"Causal Inference", "LLM","Bayesian", "State Space Models", "Gradient Boosting", "Bayesian", "Time Series", "Causal Inference","Marketing Mix Modeling"]
NUM_PAPERS = 3

# 取得する論文の数（スマホで毎朝サクッと読むなら3〜5件がおすすめです）
NUM_PAPERS = 3
# ==========================================

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID')

def build_arxiv_query(major_kws, minor_kws):
    """大カテゴリと小カテゴリを掛け合わせた検索クエリを作成する"""
    # 例: (all:"Advertising" OR ...) AND (all:"Machine Learning" OR ...)
    major_parts = [f'all:"{k}"' for k in major_kws]
    minor_parts = [f'all:"{k}"' for k in minor_kws]
    
    major_query = "(" + " OR ".join(major_parts) + ")"
    minor_query = "(" + " OR ".join(minor_parts) + ")"
    
    return f"{major_query} AND {minor_query}"

def fetch_arxiv_papers(query, num_papers=3):
    """arXiv APIから本物の論文データを取得する"""
    url = "https://export.arxiv.org/api/query" # エラー対策: HTTPSに変更
    random_start = random.randint(0, 10)
    
    params = {
        "search_query": query,
        "start": random_start,
        "max_results": num_papers,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    # エラー対策: User-Agentを追加
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
    """Geminiによるスマホ（LINE）特化型・非専門家向けの要約生成"""
    prompt = f"""
あなたは、最新の学術論文をビジネスパーソン向けに「正確に、かつ圧倒的にわかりやすく」解説するプロのコンサルタントです。
以下の論文（タイトルと要約）を読み、LINEで読むのに適したフォーマットで要約を作成してください。

・タイトル: {paper_data['title']}
・内容: {paper_data['abstract']}

【ターゲット読者】
日常的に学術論文を読むわけではないが、マーケティングやデータ分析の実務に活かせる「新しいアイデアや知見」を求めているビジネスパーソン。

【翻訳・要約のルール】
1. 直訳調の不自然な日本語（例：「～が示唆された」「～を提案する」など）を避け、自然で流暢なビジネス日本語で記述すること。
2. 論文の元の主張（正確性）は絶対に曲げず、存在しない情報を捏造しないこと。
3. 難解なアルゴリズムの詳細は追わず、「つまり、どんな賢いアプローチなのか」という直感的な理解を優先し、専門用語は極力噛み砕くこと。
4. 各項目は箇条書きまたは2〜3行の短い文章にまとめ、スマホでの視認性を高く保つこと。
5. 挨拶や前置きは一切不要。

【出力フォーマット】（以下の見出しを厳密に使用してください）

🎯 なぜこの研究が必要だった？（背景・課題）
・

💡 どんな「賢いアイデア」？（アプローチ）
・

📊 結局、何がわかった？（結論・成果）
・

🚀 実務へのヒント（アイデアの種）
・(読者が「なるほど、自社の〇〇の改善に使えるかも」と知見を深められるようなインスピレーションを1〜2文で提案)
"""
    try:
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "⚠️ 要約生成に失敗しました。"

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
    
    # 検索クエリの組み立て
    query = build_arxiv_query(MAJOR_KEYWORDS, MINOR_KEYWORDS)
    print(f"Searching for: {query}")
    
    papers = fetch_arxiv_papers(query, NUM_PAPERS)
    
    if not papers:
        send_to_line("⚠️ 条件に合致する最新論文が見つかりませんでした。")
        return
        
    for i, paper in enumerate(papers):
        summary = summarize_paper(paper, client)
        
        # LINE用のメッセージフォーマット（見出しをスッキリさせて区切り線をスマホサイズに調整）
        msg = (f"📚 論文速報 ({i+1}/{NUM_PAPERS})\n"
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