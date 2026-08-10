"""
AI NEWS FACTORY
DATABASE / STORAGE LAYER

Stores:
- collected stories
- processed stories
- published articles
- source records
- processing status
- publishing history

SQLite is used so the factory can start without requiring
a separate database server.

The storage layer is deliberately isolated from the AI brains
and publishing systems.
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class NewsDatabase:

    def __init__(
        self,
        database_path: str = "data/news_factory.db"
    ):

        self.database_path = Path(
            database_path
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize()

    # =====================================================
    # CONNECTION
    # =====================================================

    def _connect(self):

        connection = sqlite3.connect(
            str(
                self.database_path
            )
        )

        connection.row_factory = sqlite3.Row

        return connection

    # =====================================================
    # INITIALIZE
    # =====================================================

    def _initialize(self):

        with self._connect() as db:

            db.execute("""
                CREATE TABLE IF NOT EXISTS stories (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    source TEXT,
                    source_url TEXT,
                    category TEXT,
                    published_at TEXT,
                    image_url TEXT,
                    status TEXT DEFAULT 'collected',
                    data TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)

            db.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    story_id TEXT,
                    title TEXT NOT NULL,
                    slug TEXT UNIQUE,
                    content TEXT,
                    excerpt TEXT,
                    category TEXT,
                    tags TEXT,
                    image_url TEXT,
                    source_url TEXT,
                    status TEXT DEFAULT 'draft',
                    data TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)

            db.execute("""
                CREATE TABLE IF NOT EXISTS publications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id TEXT,
                    platform TEXT,
                    external_id TEXT,
                    url TEXT,
                    status TEXT,
                    response TEXT,
                    created_at REAL
                )
            """)

            db.execute("""
                CREATE TABLE IF NOT EXISTS processing_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    story_id TEXT,
                    stage TEXT,
                    status TEXT,
                    message TEXT,
                    data TEXT,
                    created_at REAL
                )
            """)

            db.commit()

    # =====================================================
    # STORY
    # =====================================================

    def save_story(
        self,
        story: Dict[str, Any],
        status: str = "collected"
    ) -> str:

        story_id = str(
            story.get(
                "id",
                ""
            )
        )

        if not story_id:

            raise ValueError(
                "Story must contain an id."
            )

        now = time.time()

        with self._connect() as db:

            db.execute("""
                INSERT INTO stories (
                    id,
                    title,
                    description,
                    source,
                    source_url,
                    category,
                    published_at,
                    image_url,
                    status,
                    data,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id)
                DO UPDATE SET
                    title = excluded.title,
                    description = excluded.description,
                    source = excluded.source,
                    source_url = excluded.source_url,
                    category = excluded.category,
                    published_at = excluded.published_at,
                    image_url = excluded.image_url,
                    status = excluded.status,
                    data = excluded.data,
                    updated_at = excluded.updated_at
            """, (

                story_id,

                story.get(
                    "title",
                    ""
                ),

                story.get(
                    "description",
                    ""
                ),

                story.get(
                    "source",
                    ""
                ),

                story.get(
                    "source_url",
                    ""
                ),

                story.get(
                    "category",
                    "general"
                ),

                story.get(
                    "published_at",
                    ""
                ),

                story.get(
                    "image_url",
                    ""
                ),

                status,

                self._json(
                    story
                ),

                now,

                now
            ))

            db.commit()

        return story_id

    # =====================================================
    # GET STORY
    # =====================================================

    def get_story(
        self,
        story_id: str
    ) -> Optional[Dict[str, Any]]:

        with self._connect() as db:

            row = db.execute("""
                SELECT *
                FROM stories
                WHERE id = ?
            """, (
                story_id,
            )).fetchone()

        if not row:

            return None

        return self._row_to_dict(
            row
        )

    # =====================================================
    # RECENT STORIES
    # =====================================================

    def recent_stories(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:

        with self._connect() as db:

            rows = db.execute("""
                SELECT *
                FROM stories
                ORDER BY created_at DESC
                LIMIT ?
            """, (
                limit,
            )).fetchall()

        return [
            self._row_to_dict(
                row
            )
            for row in rows
        ]

    # =====================================================
    # ARTICLE
    # =====================================================

    def save_article(
        self,
        article: Dict[str, Any],
        story_id: str = ""
    ) -> str:

        article_id = str(
            article.get(
                "id",
                ""
            )
        )

        if not article_id:

            article_id = self._make_id(
                article.get(
                    "slug",
                    article.get(
                        "title",
                        ""
                    )
                )
            )

        now = time.time()

        tags = article.get(
            "tags",
            []
        )

        with self._connect() as db:

            db.execute("""
                INSERT INTO articles (
                    id,
                    story_id,
                    title,
                    slug,
                    content,
                    excerpt,
                    category,
                    tags,
                    image_url,
                    source_url,
                    status,
                    data,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id)
                DO UPDATE SET
                    title = excluded.title,
                    slug = excluded.slug,
                    content = excluded.content,
                    excerpt = excluded.excerpt,
                    category = excluded.category,
                    tags = excluded.tags,
                    image_url = excluded.image_url,
                    source_url = excluded.source_url,
                    status = excluded.status,
                    data = excluded.data,
                    updated_at = excluded.updated_at
            """, (

                article_id,

                story_id,

                article.get(
                    "title",
                    ""
                ),

                article.get(
                    "slug",
                    ""
                ),

                article.get(
                    "content",
                    ""
                ),

                article.get(
                    "excerpt",
                    ""
                ),

                article.get(
                    "category",
                    "general"
                ),

                self._json(
                    tags
                ),

                article.get(
                    "image_url",
                    ""
                ),

                article.get(
                    "source_url",
                    ""
                ),

                article.get(
                    "status",
                    "draft"
                ),

                self._json(
                    article
                ),

                now,

                now
            ))

            db.commit()

        return article_id

    # =====================================================
    # GET ARTICLE
    # =====================================================

    def get_article(
        self,
        article_id: str
    ) -> Optional[Dict[str, Any]]:

        with self._connect() as db:

            row = db.execute("""
                SELECT *
                FROM articles
                WHERE id = ?
            """, (
                article_id,
            )).fetchone()

        if not row:

            return None

        return self._row_to_dict(
            row
        )

    # =====================================================
    # PUBLISHED ARTICLES
    # =====================================================

    def published_articles(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:

        with self._connect() as db:

            rows = db.execute("""
                SELECT *
                FROM articles
                WHERE status = 'published'
                ORDER BY updated_at DESC
                LIMIT ?
            """, (
                limit,
            )).fetchall()

        return [
            self._row_to_dict(
                row
            )
            for row in rows
        ]

    # =====================================================
    # PUBLICATION
    # =====================================================

    def save_publication(
        self,
        article_id: str,
        platform: str,
        status: str,
        external_id: str = "",
        url: str = "",
        response: Any = None
    ) -> int:

        with self._connect() as db:

            cursor = db.execute("""
                INSERT INTO publications (
                    article_id,
                    platform,
                    external_id,
                    url,
                    status,
                    response,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (

                article_id,

                platform,

                external_id,

                url,

                status,

                self._json(
                    response
                ),

                time.time()
            ))

            db.commit()

            return int(
                cursor.lastrowid
            )

    # =====================================================
    # PUBLICATION HISTORY
    # =====================================================

    def publication_history(
        self,
        article_id: str
    ) -> List[Dict[str, Any]]:

        with self._connect() as db:

            rows = db.execute("""
                SELECT *
                FROM publications
                WHERE article_id = ?
                ORDER BY created_at DESC
            """, (
                article_id,
            )).fetchall()

        return [
            dict(
                row
            )
            for row in rows
        ]

    # =====================================================
    # PROCESSING LOG
    # =====================================================

    def log(
        self,
        story_id: str,
        stage: str,
        status: str,
        message: str = "",
        data: Any = None
    ):

        with self._connect() as db:

            db.execute("""
                INSERT INTO processing_log (
                    story_id,
                    stage,
                    status,
                    message,
                    data,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (

                story_id,

                stage,

                status,

                message,

                self._json(
                    data
                ),

                time.time()
            ))

            db.commit()

    # =====================================================
    # DUPLICATE CHECK
    # =====================================================

    def story_exists(
        self,
        story_id: str
    ) -> bool:

        with self._connect() as db:

            row = db.execute("""
                SELECT 1
                FROM stories
                WHERE id = ?
                LIMIT 1
            """, (
                story_id,
            )).fetchone()

        return row is not None

    # =====================================================
    # ARTICLE BY SLUG
    # =====================================================

    def get_article_by_slug(
        self,
        slug: str
    ) -> Optional[Dict[str, Any]]:

        with self._connect() as db:

            row = db.execute("""
                SELECT *
                FROM articles
                WHERE slug = ?
                LIMIT 1
            """, (
                slug,
            )).fetchone()

        if not row:

            return None

        return self._row_to_dict(
            row
        )

    # =====================================================
    # UPDATE ARTICLE STATUS
    # =====================================================

    def update_article_status(
        self,
        article_id: str,
        status: str
    ) -> bool:

        with self._connect() as db:

            cursor = db.execute("""
                UPDATE articles
                SET status = ?,
                    updated_at = ?
                WHERE id = ?
            """, (

                status,

                time.time(),

                article_id
            ))

            db.commit()

            return cursor.rowcount > 0

    # =====================================================
    # UPDATE STORY STATUS
    # =====================================================

    def update_story_status(
        self,
        story_id: str,
        status: str
    ) -> bool:

        with self._connect() as db:

            cursor = db.execute("""
                UPDATE stories
                SET status = ?,
                    updated_at = ?
                WHERE id = ?
            """, (

                status,

                time.time(),

                story_id
            ))

            db.commit()

            return cursor.rowcount > 0

    # =====================================================
    # ROW CONVERSION
    # =====================================================

    def _row_to_dict(
        self,
        row
    ) -> Dict[str, Any]:

        result = dict(
            row
        )

        if "data" in result:

            result["data"] = self._from_json(
                result["data"]
            )

        if "tags" in result:

            result["tags"] = self._from_json(
                result["tags"]
            )

        return result

    # =====================================================
    # JSON
    # =====================================================

    def _json(
        self,
        value: Any
    ) -> str:

        try:

            return json.dumps(
                value,
                ensure_ascii=False,
                default=str
            )

        except Exception:

            return json.dumps(
                str(value)
            )

    # =====================================================
    # FROM JSON
    # =====================================================

    def _from_json(
        self,
        value: Any
    ) -> Any:

        if not value:

            return {}

        try:

            return json.loads(
                value
            )

        except Exception:

            return value

    # =====================================================
    # ID
    # =====================================================

    def _make_id(
        self,
        value: str
    ) -> str:

        import hashlib

        return hashlib.sha256(
            str(value).encode(
                "utf-8"
            )
        ).hexdigest()[:24]


# =========================================================
# HELPER
# =========================================================

def create_database(
    database_path: str = "data/news_factory.db"
) -> NewsDatabase:

    return NewsDatabase(
        database_path
      )
