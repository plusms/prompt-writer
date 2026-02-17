## 指定HTMLパーツリスト (Reference)
本文執筆(STEP 5)において、以下のHTMLパターンを厳守して記事を構成してください。これ以外の独自クラス（例: class="afd"）や勝手な装飾は禁止です。見出し、リスト、ボックス、テーブル等は必ずこの中から選んで使用すること。各見出しで必ず一度以上文字装飾を使用すること。

# 大見出し
## Pattern
<h2>{{title}}</h2>

# 小見出し (h3)
## Pattern
<h3>{{title}}</h3>

# 小見出し (h4)
## Pattern
<h4>{{title}}</h4>

# 見出しパーツ (subttl)
## Pattern
<div class="subTitle">{{content}}</div>

# 文字装飾 (Red)
## Pattern
<span class="pink">{{content}}</span>

# 文字装飾 (Blue)
## Pattern
<span class="blue">{{content}}</span>

# 文字装飾 (Caution)
## Pattern
<span class="caution">{{content}}</span>

# 文字装飾 (Bold)
## Pattern
<span class="bold">{{content}}</span>

# 文字装飾 (Marker Red)
## Pattern
<span class="marker">{{content}}</span>

# コンテンツ幅100%画像
## Pattern
<div class="full-img">
{{content}}
</div>

# テーブル
## Pattern
<table class="table">
{{content}}
</table>

# シンプルボックス
## Pattern
<div class="normalBox">
  {{content}}
</div>

# シンプルボックス (グレー)
## Pattern
<div class="normalBox" data-type="yellow">
  {{content}}
</div>

# シンプルボックスタイトル
## Pattern
<div class="box-ttl">{{title}}</div>

# 番号付き見出しありのテキストボックス
## Pattern
<div class="normalBox" data-type="yellow">
    <div class="box-ttl"><span class="num-c">{{num}}</span>{{title}}</div>
    {{content}}
</div>

# チェックボックス
## Pattern
<div class="checkBox">
  <div class="checkBox-title"><p>{{title}}</p></div>
  <ul class="checkBox-list">
    {{content}}
  </ul>
</div>

# 番号付きリスト
## Pattern
<ol>
  {{content}}
</ol>

# 番号なしリスト
## Pattern
<ul>
  {{content}}
</ul>

# チェックリスト
## Pattern
<ul class="checkList">
  {{content}}
</ul>

# 画像左パーツ (Flex)
## Pattern
<div class="grid">
  <img src="{{src}}" alt="{{alt}}">
  <div class="flex-txt">
    {{content}}
  </div>
</div>

# 画像左パーツ (Float)
## Pattern
<div class="float">
  <img src="{{src}}" alt="{{alt}}">
  <div class="float-txt">
    {{content}}
  </div>
</div>

# 下矢印
## Pattern
<div class="arrow-down"></div>

# 引用パーツ
## Pattern
<blockquote class="quoteBox">
{{content}}
</blockquote>

# 吹き出しタイトル
## Pattern
<div class="fukidashi">{{title}}</div>

# まとめボックス
## Pattern
<div class="matomeBox">
<div class="matomeBox-title">{{title}}</div>
<div class="matomeBox-innner">
{{content}}
</div>
</div>

# 調査概要ボックス
## Pattern
<div class="surveyBox" data-type="yellow">
<div class="surveyBox-title">{{title}}</div>
<ul>
{{content}}
</ul>
</div>

# 補足用ボックス
## Pattern
<div class="hosokuBox">
<div class="hosokuBox-title">{{title}}</div>
<div class="hosokuBox-txt">
{{content}}
</div>
</div>

# CTAボタン (Blue)
## Pattern
<div class="c-btn01">
{{link}}
</div>

# CTAボタン
## Pattern
<div class="c-btn02">
{{link}}
</div>

# タグ
## Pattern
<ul class="taglist">
{{content}}
</ul>

# タグ (on)
## Pattern
<li class="tag on">{{content}}</li>

# タグ (off)
## Pattern
<li class="tag">{{content}}</li>

# スクロールテーブル
## Pattern
<div class="scrolltable">
<table class="table">
  {{content}}
</table>
</div>

# ジャンプパーツ
## Pattern
<ul class="jumplist">
{{content}}
</ul>

# ジャンプパーツ内部
## Pattern
<li class="jump"><a href="{{url}}">{{content}}<span class="triangle"></span></a></li>

# ナンバリングパーツ
## Pattern
<ol class="numlist">
{{content}}
</ol>

# ナンバリングパーツ内部
## Pattern
<li>
<p class="numlist-title">
<span class="numlist-num"></span>
<span class="b">{{title}}</span>
</p>
<div class="numlist-block">
{{content}}
</div>
</li>

# ランキングパーツ
## Pattern
<div class="picup">
<span>{{text}}</span><a href="{{url}}" target="_blank" rel="nofollow noopener noreferrer">{{title}}</a>
</div>

# ランキングパーツ (Rank Icon)
## Pattern
<div class="picup">
{{content}}
</div>

# ランキングパーツ内部 (Rank Icon)
## Pattern
<div class="ranking-icon-block">
<span class="ranking-icon ranking-icon_{{num}}">{{num}}</span>
<div class="ranking"><span class="ranking-catch">{{catch}}</span>
<a href="{{url}}" target="_blank" rel="nofollow noopener noreferrer">{{title}}</a>
</div>
</div>

# ステップパーツ
## Pattern
<div class="flow-wrap">
{{content}}
</div>

# ステップパーツ内部
## Pattern
<div class="flow">
    <p class="flow-title">
<span class="flow-num"></span>
<span>{{title}}</span>
</p>
    <div class="flow-text">
        {{content}}
    </div>
</div>

# 関連記事パーツ
## Pattern
<div class="relatedpost">
    <p class="relatedpost-title">{{title}}</p>
    <div class="relatedpost-wrap">
        {{content}}
    </div>
</div>

# 関連記事パーツ内部
## Pattern
<div class="relatedpost-post">
    <a href="{{url}}">
        <div class="image_wrap">
            <img decoding="async" src="{{img_src}}"
                alt="{{alt}}">
        </div>
        <p class="relatedpost-post-ttl">{{title}}</p>
    </a>
</div>

# Q＆Aパーツ
## Pattern
<dl class="faq">
    {{content}}
</dl>

# Q＆Aパーツ内部
## Pattern
<dt class="faqQ">
<span class="faqQ-icon"></span>
    <p itemprop="name">{{question}}</p>
</dt>
<dd class="faqA" itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer">
<span class="faqA-icon"></span>
    <p itemprop="text">
    {{answer}}
    </p>
</dd>

# 右寄せリンク
## Pattern
<div class="right-link-icon">{{link}}</div>

# 右寄せリンク（p）
## Pattern
<p class="right-link-icon">{{link}}</p>

# 画像横スクロール
## Pattern
<div class="imgScrollBox">
<div class="imgScrollBox-wrap">
    <ul class="imgScrollBox-list">
        {{content}}
    </ul>
</div>
</div>

# 画像横スクロール内部
## Pattern
<li>
    <img src="{{src}}">
    <span class="caption">{{content}}</span>
</li>

# メリットパーツ
## Pattern
<div class="meritdemerit" data-type="merit">
<div class="meritdemerit-ttl">{{title}}</div>
	<ul class="meritdemerit-list">
		{{content}}
	</ul>
</div>

# デメリットパーツ
## Pattern
<div class="meritdemerit" data-type="demerit">
<div class="meritdemerit-ttl">{{title}}</div>
	<ul class="meritdemerit-list">
		{{content}}
	</ul>
</div>

# マップ
## Pattern
<div class="map">
<div class="map-ttl">{{title}}</div>
<div class="map-cont">
<iframe src="{{url}}" width="100%" height="300" style="border:0;" allowfullscreen="" loading="lazy"></iframe>
</div>
</div>
