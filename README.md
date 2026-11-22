# 十页 · 日常诗集

纯静态站点，没有构建步骤、没有后端、没有外部依赖（字体也已自托管）。把整个目录传到任意静态托管上就能跑。

## 目录

```
.
├── index.html          首页（全部内容都在这一个文件里）
├── 404.html            找不到页面时的样子
├── styles.css          全部样式，宣纸 + 墨 + 一点朱砂
├── script.js           手机菜单、滚动淡入
├── fonts.css           自托管字体声明（按本页用字裁剪过）
├── fonts/              24 个字体分片，共约 94 KB，另有 OFL.txt
├── robots.txt
└── tools/
    └── rebuild-fonts.py  加了新诗之后补字用
```

## 本地预览

```bash
python3 -m http.server 8000
# 打开 http://127.0.0.1:8000
```

直接双击 `index.html` 也能看，但 404 页和根路径链接只有在 http 下才正常。

## 部署：Cloudflare Pages（推荐，长期维护）

1. 把本目录推到一个 GitHub 仓库（公开或私有都行）：

   ```bash
   git remote add origin git@github.com:你的名字/shiye.git
   git branch -M main
   git push -u origin main
   ```

2. 打开 <https://dash.cloudflare.com/> → Workers & Pages → Create → Pages → Connect to Git，选这个仓库。
3. 构建设置：
   - Framework preset：**None**
   - Build command：**留空**
   - Build output directory：**`/`**
4. 保存，一分钟后拿到 `https://xxx.pages.dev`。
5. 以后改诗：改完 `git push`，自动重新发布。

绑定自己的域名：Pages 项目 → Custom domains → 添加，按提示在域名商那里加一条 CNAME。HTTPS 自动签，不用管。

## 部署：Netlify Drop（最快，30 秒）

不用仓库，直接把整个文件夹（或 zip）拖到 <https://app.netlify.com/drop>，立刻得到临时网址。
适合「今天就想发给人看」；想长期维护还是走上面的 Git 流程。

## 加一首诗

在 `index.html` 里 `<div class="poems__list">` 内部复制一整块：

```html
<article id="题目" class="poem-entry reveal">
  <h3 class="poem-entry__title"><a href="#题目">题目</a></h3>
  <p class="poem-entry__body">
    <span class="line">第一句，</span>
    <span class="line">第二句。</span>
  </p>
  <p class="poem-entry__meta">五言 · 新吟</p>
</article>
```

三件事别忘：

1. `id` 和 `href="#..."` 要一致，而且不能用空格；同名的话后面加 `-二`。
2. 顶部 `<nav class="poems__index">` 里补一行链接，不然目录里看不到。
3. **诗句一行一个 `<span class="line">`**，不要用 `<br>`，也不要把两句写在一行里。

## 加了新字之后：补字体

字体是裁剪过的，只包含当前页面用到的字。新诗里出现生僻字，那个字会退回系统楷体——不会报错，只是字形不一致。

补一次就好：

```bash
pip install fonttools brotli     # 只需一次
python3 tools/rebuild-fonts.py
```

它会重新扫描 `index.html` 和 `404.html`，重新裁剪并核对覆盖，最后告诉你「缺字：0 个」。跑完把 `fonts/` 和 `fonts.css` 一起提交。

## 字体与许可

字体是 [LXGW 文楷](https://github.com/lxgw/LxgwWenKai)，SIL Open Font License 1.1，允许自托管、修改、再分发，**保留许可文件即可**（`fonts/OFL.txt`，别删）。

## 几个坑

- **别在子路径部署。** `404.html` 里有一行 `<base href="/">`，站点假定自己住在根域名。如果非要放到 `example.com/repo/`，把这行改成 `<base href="/repo/">`。
- **zip 的层级**：打包时要让 `index.html` 在压缩包**根目录**，而不是外面多套一层文件夹，否则很多托管会显示目录列表而不是首页。
- **改了样式记得刷新缓存**：静态托管的 HTML 默认有缓存，改完看不到就先强制刷新（手机上一般是下拉刷新或换浏览器隐私模式）。
- `data-theme="dark"` 的变量还留在 CSS 里，但界面上没有切换入口。想开夜墨：把 `<html>` 的 `data-theme` 改成 `dark`。
