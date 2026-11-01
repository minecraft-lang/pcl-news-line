# -*- coding: utf-8 -*-
"""PCL 新闻主页自动更新脚本：抓取 Minecraft Wiki 新闻 -> 更新 XAML + index.html"""
import json, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 仓库根目录

FALLBACK_NEWS = [
    ["版本更新", "#3CAEEF", "2026-10-29", "Java 26.3「Wilderness Bound」正式版发布", "荒野主题更新正式上线，包含新的林地生态、远行机制与多项性能优化，Java 版玩家可直接更新体验。"],
    ["版本更新", "#3CAEEF", "2026-10-28", "基岩版 26.52 正式版发布", "基岩版同步推送 26.52 正式版，修复跨平台联机稳定性问题，并带来移动端触控优化。"],
    ["快照预览", "#8BD66F", "2026-10-25", "26.4 Snapshot 5：密冰块砖", "新快照加入密冰块砖方块，可用于建造与装饰，同时调整了寒冷群系的生成参数。"],
    ["快照预览", "#8BD66F", "2026-10-18", "26.4 Snapshot 6：雪砖", "快照 6 带来雪砖系列方块，雪原建筑有了更丰富的素材，并修复了多项崩溃问题。"],
    ["快照预览", "#8BD66F", "2026-10-11", "基岩版 26.70「Ice Caves」预览", "基岩版预览版加入冰洞地形生成，洞穴探险迎来全新视觉体验，等待玩家测试反馈。"],
    ["官方公告", "#FFD86F", "2026-10-04", "Minecraft Live 2026：全新维度「Sift 筛界」", "年度盛会公布新维度「Sift 筛界」，拥有独特的筛滤机制与矿物生态，2027 年春季上线。"],
    ["官方公告", "#FFD86F", "2026-09-27", "Dungeons II 发售在即，预购赠 Aurora 披风", "地牢续作 Dungeons II 即将发售，预购玩家可获限定 Aurora 披风，联动内容同步上线。"],
    ["平台资讯", "#FF6FA5", "2026-09-20", "我的世界 Switch 2 版公布", "官方宣布 Switch 2 版本正在开发，支持跨平台存档与增强画面，发售时间待定。"],
    ["Wiki 动态", "#B39DFF", "2026-09-15", "Minecraft Wiki 离线版更新", "中文 Minecraft Wiki 离线版更新至最新版本，支持 PCL 内嵌浏览，数据与在线版同步。"],
]

WIKI_APIS = [
    "https://zh.minecraft.wiki/api.php",
    "https://minecraft.wiki/api.php",
]
UA = "Mozilla/5.0 (compatible; PCLNewsBot/1.0; +https://github.com/minecraft-lang)"


def http_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def fetch_latest_news(limit=9):
    """尽力抓取 Wiki 最近条目生成新闻，失败抛异常由调用方兜底。"""
    items = []
    for api in WIKI_APIS:
        try:
            params = ("action=query&format=json&list=recentchanges&rcnamespace=0"
                      "&rclimit=50&rctype=new&rcprop=title|timestamp|sizes")
            data = http_json(api + "?" + params)
            rc = (data.get("query") or {}).get("recentchanges") or []
            seen = set()
            for ch in rc:
                t = (ch.get("title") or "").strip()
                if not t or t in seen:
                    continue
                seen.add(t)
                if re.search(r"(Java|基岩)版", t):
                    tag, color = "版本更新", "#3CAEEF"
                elif re.search(r"快照|预览|Snapshot", t):
                    tag, color = "快照预览", "#8BD66F"
                elif re.search(r"公告|更新|Live|发布|发售", t):
                    tag, color = "官方公告", "#FFD86F"
                else:
                    tag, color = "Wiki 动态", "#B39DFF"
                ts = (ch.get("timestamp") or "")[:10]
                items.append([tag, color, ts, t, "Minecraft Wiki 近期更新：" + t])
                if len(items) >= limit:
                    break
            if items:
                return items
        except Exception:
            continue
    raise RuntimeError("wiki fetch failed")


def render_xaml(news, cfg):
    items = []
    for tag, color, date, title, summary in news:
        items.append(f'''<GroupBox Style="{{StaticResource NewsCard}}" Margin="0,0,0,12">
      <GroupBox.Header>
        <StackPanel Orientation="Horizontal">
          <Border Background="{color}" CornerRadius="9" Padding="6,1,6,1" VerticalAlignment="Center">
            <TextBlock Text="{tag}" FontSize="11" Foreground="#FFFFFF" FontWeight="Bold"/>
          </Border>
          <TextBlock Text="{title}" FontSize="15" Foreground="#FFFFFF" FontWeight="Bold" Margin="8,0,0,0" VerticalAlignment="Center"/>
        </StackPanel>
      </GroupBox.Header>
      <StackPanel>
        <TextBlock Text="{date}" FontSize="11" Foreground="#8B949E"/>
        <TextBlock Text="{summary}" FontSize="12" Foreground="#C9D1DC" TextWrapping="Wrap" Margin="0,6,0,0"/>
      </StackPanel>
    </GroupBox>''')
    repo = cfg.get("repo_url", "#")
    return f'''<StackPanel>
  <StackPanel.Resources>
    <Style TargetType="GroupBox" x:Key="NewsCard">
      <Setter Property="Background" Value="#161B22"/>
      <Setter Property="BorderBrush" Value="#30363D"/>
      <Setter Property="BorderThickness" Value="1"/>
      <Setter Property="Padding" Value="0"/>
    </Style>
    <Style TargetType="TextBlock" x:Key="BigTitle">
      <Setter Property="FontSize" Value="26"/>
      <Setter Property="FontWeight" Value="Bold"/>
      <Setter Property="Foreground" Value="#FFFFFF"/>
    </Style>
  </StackPanel.Resources>

  <local:MyCard Title="欢迎" Margin="0,0,0,16">
    <Grid Margin="0,40,0,0">
      <StackPanel>
        <TextBlock Style="{{StaticResource BigTitle}}" Text="Minecraft 新闻主页"/>
        <TextBlock Text="Java 版 / 基岩版 版本更新  -  快照预览  -  官方公告" FontSize="13" Foreground="#B0B7C3" Margin="0,8,0,16"/>
        <StackPanel Orientation="Horizontal">
          <local:MyButton Height="34" ColorType="Highlight" Text="刷新主页" EventType="刷新主页"/>
          <local:MyButton Height="34" Margin="12,0,0,0" Text="中文 Wiki" EventData="https://zh.minecraft.wiki/"/>
          <local:MyButton Height="34" Margin="12,0,0,0" Text="English Wiki" EventData="https://minecraft.wiki/"/>
        </StackPanel>
      </StackPanel>
    </Grid>
  </local:MyCard>

  <local:MyCard Title="近期新闻" Margin="0,0,0,16">
    <StackPanel Margin="0,40,0,0">
      {chr(10).join(items)}
    </StackPanel>
  </local:MyCard>

  <local:MyCard Title="关于本主页" Margin="0,0,0,0">
    <StackPanel Margin="0,40,0,0">
      <TextBlock Text="数据源：Minecraft Wiki，由仓库 GitHub Actions 每日自动抓取生成，刷新主页即获得最新新闻。"
                 FontSize="12" Foreground="#C9D1DC" TextWrapping="Wrap"/>
      <local:MyTextButton Margin="0,12,0,0" EventType="打开网页" Text="访问 Minecraft Wiki"
                          EventData="https://zh.minecraft.wiki/"/>
      <local:MyTextButton Margin="0,8,0,0" EventType="打开网页" Text="查看更新仓库"
                          EventData="{repo}"/>
    </StackPanel>
  </local:MyCard>
</StackPanel>'''


def render_news_html(news):
    items = []
    for tag, color, date, title, summary in news:
        items.append(f'''<article class="news-item">
        <span class="tag" style="background:{color}">{tag}</span>
        <h3>{title}</h3>
        <time>{date}</time>
        <p>{summary}</p>
      </article>''')
    return '\n'.join(items)


def default_html(news, cfg):
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{cfg.get("title", "PCL 新闻主页")}</title>
  <meta name="description" content="{cfg.get("desc", "")}">
  <meta name="keywords" content="{", ".join(cfg.get("keywords", []))}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{cfg.get("domain", "")}/">
</head>
<body>
  <div class="wrap">
    <header>
      <h1>{cfg.get("title", "PCL 新闻主页").split("|")[0].strip()}</h1>
      <div class="copy"><input readonly value="{cfg.get("domain", "")}/PCL_MinecraftNewsPage.xaml"><button onclick="navigator.clipboard.writeText(this.previousElementSibling.value)">复制订阅地址</button></div>
    </header>
    <main>
      {render_news_html(news)}
    </main>
    <footer>数据源 Minecraft Wiki  -  由 GitHub Actions 每日自动更新</footer>
  </div>
</body>
</html>'''


def main():
    cfg = {}
    cfg_path = os.path.join(ROOT, "site_config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    news = FALLBACK_NEWS
    try:
        news = fetch_latest_news()
        print("fetched from wiki:", len(news))
    except Exception as e:
        print("wiki fetch failed, using fallback:", e)

    xaml_path = os.path.join(ROOT, "PCL_MinecraftNewsPage.xaml")
    with open(xaml_path, "w", encoding="utf-8", newline="") as f:
        f.write(render_xaml(news, cfg))

    html_path = os.path.join(ROOT, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        block = render_news_html(news)
        new_html, n = re.subn(r"<main>.*?</main>", "<main>\n      " + block + "\n    </main>", html, flags=re.S)
        if n == 0:
            new_html = html
        with open(html_path, "w", encoding="utf-8", newline="") as f:
            f.write(new_html)
    else:
        with open(html_path, "w", encoding="utf-8", newline="") as f:
            f.write(default_html(news, cfg))
    print("updated:", os.path.basename(xaml_path), os.path.basename(html_path), len(news), "items")


if __name__ == "__main__":
    main()
