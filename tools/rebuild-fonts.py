#!/usr/bin/env python3
"""按站点实际用字重建自托管字体分片。

加了新诗、或者改了文案之后跑一次，新出现的字才会用上文楷；
不跑也不会坏，只是那几个字会退回系统楷体。

用法:
    pip install fonttools brotli      # 只需装一次
    python3 tools/rebuild-fonts.py

它做的事：
  1. 扫 index.html / 404.html 里的可见文字（跳过 <script>、<style>）
  2. 按 unicode-range 找出覆盖这些字的字体分片
  3. 下载分片，用 pyftsubset 裁到只剩用到的字
  4. 重写 fonts.css，并核对覆盖率
"""

import os
import re
import sys
import urllib.request

CDN = "https://cdn.staticfile.org/lxgw-wenkai-webfont/1.7.0/"
CSS_URL = CDN + "lxgwwenkai-regular.css"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")

EXTRA = "0123456789.,:;!?·—…（）「」：、。，！“”《》"


def visible_text():
    chars = set()
    for name in ("index.html", "404.html"):
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            continue
        html = open(path, encoding="utf-8").read()
        html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S)
        html = re.sub(r"<[^>]+>", " ", html)
        chars |= {c for c in html if c.strip()}
    return chars | set(EXTRA)


def parse_ranges(ur):
    out = []
    for tok in ur.split(","):
        tok = tok.strip().lower().replace("u+", "")
        if not tok:
            continue
        a, _, b = tok.partition("-")
        out.append((int(a, 16), int(b, 16)) if b else (int(a, 16), int(a, 16)))
    return out


def main():
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:
        sys.exit("缺 fonttools：pip install fonttools brotli")

    print("读取字体 CSS …")
    css = urllib.request.urlopen(CSS_URL, timeout=30).read().decode("utf-8")
    blocks = re.findall(r"@font-face\s*\{(.*?)\}", css, re.S)
    chars = visible_text()
    print(f"站点可见字符：{len(chars)}")

    os.makedirs(FONTS, exist_ok=True)
    faces, keep_names = [], set()
    total_before = total_after = 0

    for block in blocks:
        m = re.search(r"url\('([^']+)'\)", block)
        u = re.search(r"unicode-range:\s*([^;}]+)", block)
        if not m or not u:
            continue
        ranges = parse_ranges(u.group(1))
        used = sorted(c for c in chars if any(a <= ord(c) <= z for a, z in ranges))
        if not used:
            continue

        name = os.path.basename(m.group(1))
        path = os.path.join(FONTS, name)

        # 本地那份可能已经被裁过一次；缺字就重新下载完整分片
        font = TTFont(path) if os.path.exists(path) else None
        if font is None or any(ord(c) not in font.getBestCmap() for c in used):
            data = urllib.request.urlopen(CDN + m.group(1).lstrip("./"), timeout=30).read()
            open(path, "wb").write(data)
            font = TTFont(path)
        total_before += os.path.getsize(path)
        cmap = font.getBestCmap()
        text = "".join(c for c in used if ord(c) in cmap)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        opts.notdef_outline = True
        sub = subset.Subsetter(options=opts)
        sub.populate(text=text)
        sub.subset(font)
        font.flavor = "woff2"
        font.save(path)
        total_after += os.path.getsize(path)

        keep_names.add(name)
        faces.append(
            "@font-face{font-family:'LXGW WenKai';font-style:normal;font-weight:400;"
            f"font-display:swap;src:url('./fonts/{name}') format('woff2');"
            f"unicode-range:{u.group(1).strip()};}}"
        )

    # 删掉这次没用到的旧分片
    for name in os.listdir(FONTS):
        if name.endswith(".woff2") and name not in keep_names:
            os.remove(os.path.join(FONTS, name))

    header = "/* LXGW 文楷 · SIL OFL 1.1（见 fonts/OFL.txt）· 按本页用字裁剪并自托管 */\n"
    open(os.path.join(ROOT, "fonts.css"), "w", encoding="utf-8").write(header + "\n".join(faces) + "\n")

    # 覆盖率核对
    cover = set()
    for name in keep_names:
        cover |= {chr(k) for k in TTFont(os.path.join(FONTS, name)).getBestCmap()}
    missing = sorted(c for c in chars if c not in cover)

    print(f"分片：{len(faces)} 个，{total_before/1024:.0f} KB → {total_after/1024:.0f} KB")
    print(f"缺字：{len(missing)} 个" + ("" if not missing else "  " + "".join(missing[:30])))
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
