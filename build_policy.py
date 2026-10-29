"""Build the public pages and optionally sync identical text into the Godot app."""
from pathlib import Path
import argparse
import hashlib
import html
import re

ROOT = Path(__file__).resolve().parent
LANGUAGES = [('en', 'English', 'index.html'), ('ru', 'Русский', 'ru.html'), ('uk', 'Українська', 'uk.html')]
STYLE = '''*{box-sizing:border-box}body{margin:0;background:#10151f;color:#dbe2ed;font:17px/1.75 system-ui,sans-serif}main{max-width:850px;margin:0 auto;padding:44px 24px 72px}header{letter-spacing:.35em;color:#85d8c3;font-size:22px;margin-bottom:28px}nav{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:32px}nav a{border:1px solid #35514f;border-radius:22px;padding:7px 18px;color:#c7d0df;text-decoration:none}nav a[aria-current]{background:#1e3538;color:#85d8c3}nav a:hover,nav a:focus-visible{border-color:#85d8c3}h1{font-weight:450;font-size:clamp(26px,5vw,36px);line-height:1.3;color:#ecf0f5}h2{font-size:22px;font-weight:500;line-height:1.4;color:#ecf0f5;margin-top:36px}p{white-space:pre-line;overflow-wrap:anywhere}p a{color:#9ae4d0;text-underline-offset:3px}p a:focus-visible{outline:2px solid #9ae4d0;outline-offset:3px}.meta{color:#9aa8ba}footer{margin-top:48px;color:#9aa8ba;font-size:14px}'''

def rich(text):
    escaped = html.escape(text)
    return re.sub(r'https://[^\s<]+', lambda m: '<a href="' + m[0] + '">' + m[0] + '</a>', escaped)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-project', type=Path)
    args = parser.parse_args()
    for lang, _, filename in LANGUAGES:
        text = (ROOT / f'policy-{lang}.txt').read_text(encoding='utf-8-sig').replace('\r\n', '\n').strip() + '\n'
        digest = hashlib.sha256(text.encode()).hexdigest()
        groups = text.strip().split('\n\n')
        title, *meta = groups[0].splitlines()
        body = ['<h1>' + html.escape(title) + '</h1>', '<p class="meta">' + rich('\n'.join(meta)) + '</p>']
        for group in groups[1:]:
            lines = group.splitlines()
            if re.match(r'^\d+\. ', lines[0]):
                body.append('<h2>' + html.escape(lines.pop(0)) + '</h2>')
            if lines:
                body.append('<p>' + rich('\n'.join(lines)) + '</p>')
        nav = ''.join(f'<a {"aria-current=\"page\" " if code == lang else ""}href="{target}" lang="{code}">{label}</a>' for code, label, target in LANGUAGES)
        page = f'<!doctype html>\n<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>{html.escape(title)} — FEDOT</title><style>{STYLE}</style></head><body><main><header>NUMIO</header><nav aria-label="Language">{nav}</nav><article id="policy-body" data-source-sha256="{digest}">' + '\n'.join(body) + '</article><footer>FEDOT · archigamesads@gmail.com</footer></main></body></html>\n'
        (ROOT / filename).write_text(page, encoding='utf-8', newline='\n')
        if args.game_project:
            destination = args.game_project / 'assets' / 'legal' / f'privacy-policy-{lang}.txt'
            if not destination.parent.is_dir():
                raise ValueError(f'Missing game legal directory: {destination.parent}')
            destination.write_text(text, encoding='utf-8', newline='\n')
        print(f'{lang}: {filename}, sha256={digest}')

if __name__ == '__main__':
    main()
