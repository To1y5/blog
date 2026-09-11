#!/usr/bin/env python3
"""从 Fluid 生成的 HTML 还原 Hexo Markdown 源。"""
from __future__ import annotations

import html as htmlmod
import re
import shutil
from pathlib import Path

SITE = Path("/tmp/to1y5-blog/site")
OUT = Path("/Users/noeplex/blog/source/_posts")
ABOUT = Path("/Users/noeplex/blog/source/about/index.md")


def inner_markdown_body(html: str) -> str:
    start = html.find('<div class="markdown-body">')
    if start < 0:
        raise ValueError("no markdown-body")
    start += len('<div class="markdown-body">')
    end = html.find("</article>", start)
    if end < 0:
        raise ValueError("no article end")
    inner = html[start:end]
    # 去掉 markdown-body 自己的闭合，不要用非贪婪 </div>，里面代码高亮也有 div
    inner = re.sub(r"</div>\s*$", "", inner.strip())
    return inner


def decode_code_cell(cell: str) -> str:
    # highlight.js wraps tokens in spans; drop tags, keep text, then unescape
    text = re.sub(r"<br\s*/?>", "\n", cell, flags=re.I)
    text = re.sub(r"</p>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = htmlmod.unescape(text)
    return text.replace("\xa0", " ").rstrip("\n") + "\n"


def figures_to_fences(src: str) -> str:
    def repl(m: re.Match) -> str:
        lang = (m.group(1) or "").strip()
        inner = m.group(2)
        # 用 code 列整格，避免 code 块内部出现 </code> 时非贪婪匹配提前截断
        cm = re.search(r'<td class="code"><pre>(.*?)</pre></td>', inner, re.S)
        if not cm:
            cm = re.search(r"<code class=\"hljs[^\"]*\">(.*)</code>", inner, re.S)
        code = decode_code_cell(cm.group(1) if cm else inner)
        return f"\n```{lang}\n{code}```\n"

    return re.sub(
        r'<figure class="highlight\s*([^"]*)">(.*?)</figure>',
        repl,
        src,
        flags=re.S,
    )


def _html_fragment_to_md(body: str) -> str:
    # headerlink anchors
    body = re.sub(r'<a href="#[^"]*" class="headerlink"[^>]*></a>', "", body)
    # images
    body = re.sub(
        r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*/?>',
        lambda m: f'![{m.group(2)}]({m.group(1)})',
        body,
    )
    body = re.sub(
        r'<img[^>]*src="([^"]+)"[^>]*/?>',
        lambda m: f'![]({m.group(1)})',
        body,
    )
    # links
    body = re.sub(
        r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        lambda m: f'[{re.sub("<[^>]+>", "", m.group(2))}]({m.group(1)})',
        body,
        flags=re.S,
    )
    # headings
    for i in range(6, 0, -1):
        body = re.sub(
            rf"<h{i}[^>]*>(.*?)</h{i}>",
            lambda m, i=i: f'\n{"#" * i} {re.sub("<[^>]+>", "", m.group(1)).strip()}\n',
            body,
            flags=re.S,
        )
    body = re.sub(r"<blockquote>(.*?)</blockquote>", lambda m: "\n> " + re.sub("<[^>]+>", "", m.group(1)).strip().replace("\n", "\n> ") + "\n", body, flags=re.S)
    body = re.sub(r"<li[^>]*>(.*?)</li>", lambda m: "- " + re.sub("<[^>]+>", "", m.group(1)).strip() + "\n", body, flags=re.S)
    body = re.sub(r"</?ul[^>]*>", "\n", body)
    body = re.sub(r"</?ol[^>]*>", "\n", body)
    body = re.sub(r"<pre><code(?: class=\"[^\"]*\")?>(.*?)</code></pre>", lambda m: f"\n```\n{htmlmod.unescape(m.group(1))}\n```\n", body, flags=re.S)
    body = re.sub(r"<code>(.*?)</code>", lambda m: f"`{htmlmod.unescape(re.sub('<[^>]+>', '', m.group(1)))}`", body, flags=re.S)
    body = re.sub(r"<strong>(.*?)</strong>", r"**\1**", body, flags=re.S)
    body = re.sub(r"<em>(.*?)</em>", r"*\1*", body, flags=re.S)
    body = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
    body = re.sub(r"</p>", "\n\n", body, flags=re.I)
    body = re.sub(r"<p[^>]*>", "", body)
    body = re.sub(r"<hr[^>]*>", "\n---\n", body)
    body = re.sub(r"<[^>]+>", "", body)
    body = htmlmod.unescape(body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def html_to_md(body: str) -> str:
    body = figures_to_fences(body)
    # 先切出 ``` 代码块，避免后面的 <[^>]+> 把 <?php ... ?> 整段当 HTML 标签吃掉
    chunks = body.split("```")
    out = []
    for i, chunk in enumerate(chunks):
        if i % 2 == 1:
            out.append("```" + chunk + "```")
        else:
            out.append(_html_fragment_to_md(chunk))
    text = "\n\n".join(x for x in out if x)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def post_meta(html: str, url_date: str):
    title_m = re.search(r'<h1 style="display: none">([^<]+)</h1>', html)
    title = htmlmod.unescape(title_m.group(1)) if title_m else "untitled"
    dt = re.search(r'<time datetime="([^"]+)"', html)
    date = dt.group(1).strip() if dt else url_date + " 00:00:00"
    if re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", date):
        date += ":00"
    tags = [htmlmod.unescape(t) for t in re.findall(r'href="/tags/([^/"]+)/"', html)]
    cats = [htmlmod.unescape(t) for t in re.findall(r'href="/categories/([^/"]+)/"', html)]
    return title, date, tags, cats


def yaml_list(xs):
    if not xs:
        return ""
    inner = ", ".join(xs)
    return f"\n{inner}" if False else xs


def write_post(html_path: Path) -> Path:
    # .../2023/04/29/maybe/index.html
    parts = html_path.parts
    year, month, day, slug = parts[-5], parts[-4], parts[-3], parts[-2]
    html = html_path.read_text(encoding="utf-8", errors="replace")
    title, date, tags, cats = post_meta(html, f"{year}-{month}-{day}")
    md = html_to_md(inner_markdown_body(html))
    permalink = f"{year}/{month}/{day}/{slug}/"
    fm = [
        "---",
        f"title: {title}",
        f"slug: {slug}",
        f"permalink: {permalink}",
        f"date: {date}",
    ]
    if tags:
        fm.append("tags:")
        for t in tags:
            fm.append(f"  - {t}")
    if cats:
        fm.append("categories:")
        for c in cats:
            fm.append(f"  - {c}")
    fm.append("---")
    fm.append("")
    # filename: keep slug; hexo permalink uses title by default but we'll set permalink in config
    safe = slug
    out = OUT / f"{year}-{month}-{day}-{safe}.md"
    # 文章配图：原站放在同目录，Hexo post_asset_folder 要求同名文件夹
    asset_src = html_path.parent
    asset_dst = OUT / f"{year}-{month}-{day}-{safe}"
    imgs = [p for p in asset_src.iterdir() if p.is_file() and p.name != "index.html"]
    if imgs:
        if asset_dst.exists():
            shutil.rmtree(asset_dst)
        asset_dst.mkdir(parents=True)
        for img in imgs:
            shutil.copy2(img, asset_dst / img.name)
        md = re.sub(
            rf"\(/?{year}/{month}/{day}/{re.escape(slug)}/([^)]+)\)",
            r"(\1)",
            md,
        )
    out.write_text("\n".join(fm) + md, encoding="utf-8")
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # drop hexo default hello-world
    for old in OUT.glob("*.md"):
        old.unlink()
    written = []
    for p in sorted(SITE.glob("20*/*/*/*/index.html")):
        out = write_post(p)
        written.append(out)
        print("wrote", out.name)
    about_html = (SITE / "about/index.html").read_text(encoding="utf-8", errors="replace")
    ABOUT.parent.mkdir(parents=True, exist_ok=True)
    about_md = html_to_md(inner_markdown_body(about_html))
    ABOUT.write_text(
        "---\n"
        "title: about\n"
        "date: 2023-03-14 00:00:00\n"
        "layout: about\n"
        "---\n\n" + about_md,
        encoding="utf-8",
    )
    print("about", ABOUT)
    print("posts", len(written))


if __name__ == "__main__":
    main()
