from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

NOTICE_URL = 'https://www.kw.ac.kr/ko/life/notice.jsp'

def fetch_notices():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

        response = requests.get(NOTICE_URL, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        notices = []
        board_texts = soup.select('.board-text')

        for board in board_texts:
            title_tag = board.find('a')
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            if '신규게시글' in title:
                title = title.split('신규게시글')[0].strip()

            link = title_tag.get('href')
            if link and not link.startswith('http'):
                link = f'https://www.kw.ac.kr{link}'

            date_tag = board.find_next_sibling('div', class_='board-date')
            date_text = date_tag.get_text(strip=True) if date_tag else ''
            date_matches = re.findall(r'\d{4}-\d{2}-\d{2}', date_text)
            date = date_matches[0] if len(date_matches) >= 1 else ''
            update_date = date_matches[1] if len(date_matches) >= 2 else ''

            if not date:
                date_fallback = re.findall(r'\d{4}-\d{2}-\d{2}', board.get_text())
                if date_fallback:
                    date = date_fallback[0]
                    update_date = date_fallback[1] if len(date_fallback) > 1 else ''

            if title and link and date:
                notices.append({
                    'title': title,
                    'date': date,
                    'update_date': update_date,
                    'url': link
                })

        if not notices:
            print('[경고] 공지사항이 없습니다. 구조가 변경되었을 수 있습니다.')
            print(soup.prettify()[:500])

        return notices

    except Exception as e:
        print(f'[오류] 공지사항 크롤링 실패: {e}')
        return []

@app.route('/notice', methods=['GET'])
def get_notices():
    notices = fetch_notices()
    return jsonify({'notices': notices})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
