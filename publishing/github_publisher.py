import base64,json,os,logging,re
from datetime import datetime,timezone
from typing import Any,Dict,List
from urllib.parse import quote
from html import escape
import requests

logger=logging.getLogger("NewsFactory.GitHubPublisher")

class GitHubPublisher:
    """Publish articles, static pages and sitemap to the Newsroom GitHub repository."""

    def __init__(self):
        self.name="GitHub Publisher"
        self.version="3.0.0"
        self.api_base="https://api.github.com"
        self.repository=os.getenv("GITHUB_REPOSITORY","").strip()
        self.token=os.getenv("GITHUB_TOKEN","").strip()
        self.branch=os.getenv("GITHUB_BRANCH","main").strip()
        self.articles_path=os.getenv("GITHUB_ARTICLES_PATH","data/articles.json").strip()
        self.sitemap_path=os.getenv("GITHUB_SITEMAP_PATH","sitemap.xml").strip()
        self.site_url=os.getenv("GITHUB_SITE_URL","").strip().rstrip("/")
        self.articles_dir="articles"
        self.timeout=30

    def status(self)->Dict[str,Any]:
        configured=bool(self.repository and self.token and self.site_url)
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY" if configured else "NOT_CONFIGURED",
            "configured":configured,
            "repository":self.repository,
            "branch":self.branch,
            "articles_path":self.articles_path,
            "sitemap_path":self.sitemap_path,
            "site_url":self.site_url,
        }

    def publish(self,article:Any,platform:str="website")->Dict[str,Any]:
        if not isinstance(article,dict):
            return self._fail("Article must be a dictionary.")
        if not self.repository or not self.token or not self.site_url:
            return self._fail("GitHub publisher is not configured.")
        normalized=self._normalize_article(article)
        if not normalized["title"]:
            return self._fail("Article title is missing.")
        if not normalized["slug"]:
            return self._fail("Article slug is missing.")
        if not normalized["content"]:
            return self._fail("Article content is missing.")

        try:
            articles=self._get_articles_file()
            existing=False
            for i,item in enumerate(articles):
                if isinstance(item,dict) and (
                    item.get("slug")==normalized["slug"] or
                    item.get("url")==normalized["url"]
                ):
                    articles[i]=normalized
                    existing=True
                    break
            if not existing:
                articles.append(normalized)

            articles.sort(
                key=lambda x:self._sort_date(x.get("published_at","")),
                reverse=True
            )

            commit_message=(
                f"Update article: {normalized['title']}"
                if existing else
                f"Publish article: {normalized['title']}"
            )

            json_result=self._put_file(
                self.articles_path,
                self._build_articles_json(articles),
                commit_message
            )
            if not json_result.get("success"):
                return self._fail(
                    json_result.get("error","Failed to publish articles.json.")
                )

            page_result=self._publish_article_page(normalized)
            sitemap_result=self._update_sitemap(articles)

            warnings=[]
            if not page_result.get("success"):
                warnings.append(
                    "Static article page update failed: "
                    +str(page_result.get("error","Unknown error"))
                )
            if not sitemap_result.get("success"):
                warnings.append(
                    "Sitemap update failed: "
                    +str(sitemap_result.get("error","Unknown error"))
                )

            status="PUBLISHED_WITH_WARNING" if warnings else "PUBLISHED"

            return {
                "status":status,
                "published":True,
                "platform":platform,
                "engine":self.name,
                "version":self.version,
                "title":normalized["title"],
                "slug":normalized["slug"],
                "url":normalized["url"],
                "static_url":normalized["static_url"],
                "article_page":page_result.get("path"),
                "sitemap":sitemap_result.get("path"),
                "github_url":json_result.get("html_url"),
                "commit_sha":json_result.get("commit_sha"),
                "file_sha":json_result.get("sha"),
                "warnings":warnings,
                "updated":existing,
            }

        except Exception as exc:
            logger.exception("GitHub publication failed")
            return self._fail(str(exc))

    def _normalize_article(self,article:Dict[str,Any])->Dict[str,Any]:
        title=self._text(
            article.get("title") or article.get("headline") or ""
        )
        slug=self._text(article.get("slug") or self._slug(title))
        content=self._text(
            article.get("content") or article.get("body") or ""
        )
        excerpt=self._text(
            article.get("excerpt") or article.get("lead") or content
        )
        category=self._text(article.get("category") or "general")
        published_at=self._text(
            article.get("published_at") or
            article.get("publication_date") or
            self._now()
        )
        modified_at=self._text(
            article.get("modified_at") or published_at
        )
        image_url=self._text(
            article.get("image_url") or
            article.get("image") or
            ""
        )
        source_url=self._text(
            article.get("source_url") or ""
        )
        source_name=self._text(
            article.get("source_name") or
            article.get("publisher") or
            ""
        )

        tags=article.get("tags",[])
        if isinstance(tags,str):
            tags=[tags]
        if not isinstance(tags,list):
            tags=[]

        sources=article.get("sources",[])
        if not isinstance(sources,list):
            sources=[]

        normalized=dict(article)
        normalized.update({
            "title":title,
            "headline":title,
            "slug":slug,
            "content":content,
            "body":content,
            "excerpt":excerpt[:300],
            "category":category,
            "published_at":published_at,
            "modified_at":modified_at,
            "image_url":image_url,
            "source_url":source_url,
            "source_name":source_name,
            "tags":self._clean_list(tags),
            "sources":sources,
            "url":self._article_url(slug),
            "static_url":self._static_article_url(slug),
        })
        return normalized

    def _get_articles_file(self)->List[Dict[str,Any]]:
        result=self._get_file(self.articles_path)
        if not result.get("success"):
            if result.get("status_code")==404:
                return []
            raise RuntimeError(
                result.get("error","Unable to read articles file.")
            )

        content=result.get("content","").strip()
        if not content:
            return []

        try:
            decoded=base64.b64decode(content).decode("utf-8")
            data=json.loads(decoded)
        except Exception as exc:
            raise RuntimeError(
                f"Invalid articles JSON: {exc}"
            ) from exc

        if isinstance(data,dict):
            data=data.get("articles",[])
        if not isinstance(data,list):
            raise RuntimeError("articles.json must contain a list.")

        return [x for x in data if isinstance(x,dict)]

    def _build_articles_json(self,articles:List[Dict[str,Any]])->str:
        return json.dumps(
            articles,
            ensure_ascii=False,
            indent=2
        )+"\n"

    def _publish_article_page(
        self,
        article:Dict[str,Any]
    )->Dict[str,Any]:
        path=f"{self.articles_dir}/{article['slug']}.html"
        html=self._build_article_page(article)
        return self._put_file(
            path,
            html,
            f"Publish article page: {article['title']}"
        )

    def _build_article_page(self,article:Dict[str,Any])->str:
        title=self._html(article.get("title"))
        excerpt=self._html(article.get("excerpt"))
        category=self._html(article.get("category"))
        image=self._html(article.get("image_url"))
        published=self._html(article.get("published_at"))
        modified=self._html(article.get("modified_at"))
        slug=self._html(article.get("slug"))
        canonical=self._html(article.get("static_url"))
        content=self._render_content(article.get("content",""))
        tags=self._render_tags(article.get("tags",[]))
        sources=self._render_sources(article.get("sources",[]))

        image_block=(
            f'<img class="hero-image" src="{image}" alt="{title}" loading="eager">'
            if image else ""
        )

        schema={
            "@context":"https://schema.org",
            "@type":"NewsArticle",
            "headline":article.get("title",""),
            "description":article.get("excerpt",""),
            "datePublished":article.get("published_at",""),
            "dateModified":article.get("modified_at",""),
            "mainEntityOfPage":{"@type":"WebPage","@id":article.get("static_url","")},
            "url":article.get("static_url",""),
            "articleSection":article.get("category",""),
            "image":[article.get("image_url","")] if article.get("image_url") else [],
            "author":{"@type":"Organization","name":"AI News Factory"},
            "publisher":{"@type":"Organization","name":"AI News Factory"},
        }

        schema_json=json.dumps(
            schema,
            ensure_ascii=False
        ).replace("</","<\\/")

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} | AI News Factory</title>
<meta name="description" content="{excerpt}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{excerpt}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="AI News Factory">
{f'<meta property="og:image" content="{image}">' if image else ''}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{excerpt}">
{f'<meta name="twitter:image" content="{image}">' if image else ''}
<script async src="https://www.googletagmanager.com/gtag/js?id=G-3W73D556F8"></script>
<script>
window.dataLayer=window.dataLayer||[];
function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());
gtag('config','G-3W73D556F8');
</script>
<script type="application/ld+json">{schema_json}</script>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#fff;color:#171717;font-family:Arial,Helvetica,sans-serif;line-height:1.7}}
main{{max-width:900px;margin:0 auto;padding:40px 22px 70px}}
.category{{font-size:13px;font-weight:700;text-transform:uppercase;color:#666;letter-spacing:.08em;margin-bottom:12px}}
h1{{font-size:clamp(34px,6vw,58px);line-height:1.08;margin:0 0 18px;color:#111}}
.excerpt{{font-size:20px;color:#555;margin:0 0 20px}}
.meta{{font-size:14px;color:#777;margin-bottom:28px}}
.hero-image{{width:100%;height:auto;display:block;border-radius:12px;margin:0 0 32px}}
.article-body{{font-size:18px}}
.article-body h2{{font-size:30px;line-height:1.2;margin:40px 0 14px}}
.article-body h3{{font-size:23px;margin:30px 0 10px}}
.article-body p{{margin:0 0 20px}}
.article-body a{{color:#1264d3}}
.tags{{display:flex;flex-wrap:wrap;gap:8px;margin:35px 0}}
.tag{{padding:6px 10px;background:#f1f1f1;border-radius:20px;font-size:13px}}
.sources{{border-top:1px solid #ddd;margin-top:45px;padding-top:25px}}
.sources h3{{margin-top:0}}
.sources a{{color:#1264d3}}
footer{{border-top:1px solid #ddd;margin-top:50px;padding-top:20px;color:#777;font-size:13px}}
</style>
</head>
<body>
<main>
<div class="category">{category}</div>
<h1>{title}</h1>
<p class="excerpt">{excerpt}</p>
<div class="meta">Published {published} · Updated {modified}</div>
{image_block}
<article class="article-body">
{content}
</article>
{tags}
{sources}
<footer>Published by AI News Factory</footer>
</main>
</body>
</html>'''
