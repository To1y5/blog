# To1y5's Blog

线上：https://noeplex.com  
主题：Hexo 8 + Fluid。文章从旧站点 HTML 还原进 `source/_posts/`。

以前 GitHub 上的 `To1y5.github.io` **只有生成结果，没有 Hexo 源码**。本仓库才是源码，以后不要只把 `public/` 推上去。

## 日常

```bash
cd ~/blog
npm install          # 换电脑时跑一次

npx hexo new "文章标题"     # 生成 source/_posts/xxxx.md
npx hexo server             # http://localhost:4000 预览
npx hexo generate           # 只生成，不发布
npx hexo deploy             # 生成并推到 To1y5.github.io（master）
```

写完预览没问题再 `npx hexo deploy`。GitHub Pages 几分钟后更新 https://noeplex.com

## 目录

```
_config.yml          站点：标题、域名、deploy
_config.fluid.yml    主题：导航、首页标语、关于页
source/_posts/       文章 Markdown + 配图文件夹
source/about/        关于页
source/CNAME         noeplex.com
```

## 注意

- 旧文章是从 HTML 抽回来的，代码块和配图已对过常见篇，个别排版可能还有毛刺，直接改对应 `.md`。
- `To1y5.github.io` 继续只当发布仓库，不要在那边改文章。
- 域名证书、Pages 仍绑在 `To1y5.github.io` 的 `master` + CNAME `noeplex.com`。
