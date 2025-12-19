"""
Integration tests for BM25 search using pg_textsearch.
Requires PostgreSQL 17+ with pg_textsearch extension.
"""

import pytest
from django.db import connection

from django_hawkeye import BM25Score
from tests.models import Article


@pytest.mark.django_db
class TestBM25Search:
    """Integration tests for BM25 search."""

    @pytest.fixture(autouse=True)
    def setup_articles(self, db):
        """Create test articles."""
        Article.objects.create(
            title="Introduction to PostgreSQL",
            content="PostgreSQL is a powerful open source relational database system.",
        )
        Article.objects.create(
            title="Django Web Framework",
            content="Django is a high-level Python web framework for rapid development.",
        )
        Article.objects.create(
            title="Full-Text Search Guide",
            content="Full-text search enables searching for documents based on content.",
        )
        Article.objects.create(
            title="Database Performance",
            content="Optimizing database queries improves application performance.",
        )

    def test_search_basic(self):
        """Test basic BM25 search."""
        results = Article.search("postgresql")

        assert results.count() >= 1
        # Results ordered by ascending score (lower = better)
        first = results.first()
        assert first.bm25_score < 0  # Negative scores

    def test_search_with_limit(self):
        """Test BM25 search with limit."""
        results = Article.search("database")[:2]

        assert len(list(results)) <= 2

    def test_search_empty_query(self):
        """Test BM25 search with empty query returns nothing."""
        results = Article.search("")

        assert results.count() == 0

    def test_search_nonexistent_term(self):
        """Test BM25 search with non-matching term still returns results.

        BM25 ranking doesn't filter - it scores all documents.
        Non-matching documents get score 0 but are still returned.
        Use filter with threshold to exclude non-matches.
        """
        results = list(Article.search("nonexistentterm12345"))

        # All documents returned (BM25 ranks, doesn't filter)
        assert len(results) == 4
        # Scores should be 0 for non-matching terms
        for article in results:
            assert article.bm25_score == 0

    def test_search_with_threshold_filter(self):
        """Test BM25 search with threshold filter returns matching documents."""
        results = Article.search("database").filter(bm25_score__lt=-0.5)

        # Should return documents matching the threshold
        assert results.exists()
        assert results.count() >= 1

    def test_search_threshold_excludes_nonmatching(self):
        """Test threshold filter excludes non-matching documents.

        Non-matching documents have score 0, which doesn't pass threshold < -0.5.
        """
        results = Article.search("nonexistentterm12345").filter(bm25_score__lt=-0.5)

        # No documents match - score 0 doesn't pass threshold < -0.5
        assert results.count() == 0

    def test_search_stricter_threshold(self):
        """Test stricter threshold returns fewer results."""
        # Relaxed threshold - more results
        relaxed = Article.search("database").filter(bm25_score__lt=-0.1)

        # Stricter threshold - fewer results
        strict = Article.search("database").filter(bm25_score__lt=-5.0)

        # Stricter threshold should return same or fewer results
        assert strict.count() <= relaxed.count()

    def test_search_chainable_with_filter(self):
        """Test search is chainable with Django filter."""
        results = Article.search("database").filter(title__icontains="performance")

        assert results.count() >= 1
        for article in results:
            assert "performance" in article.title.lower()

    def test_search_chainable_with_exclude(self):
        """Test search is chainable with Django exclude."""
        all_results = Article.search("database")
        filtered = Article.search("database").exclude(title__icontains="performance")

        assert filtered.count() < all_results.count()


@pytest.mark.django_db
class TestBM25Score:
    """Integration tests for BM25Score expression."""

    @pytest.fixture(autouse=True)
    def setup_articles(self, db):
        """Create test articles."""
        Article.objects.create(
            title="PostgreSQL Tutorial",
            content="Learn PostgreSQL database management and optimization.",
        )
        Article.objects.create(
            title="MySQL Guide",
            content="MySQL is another popular database system.",
        )

    def test_bm25_score_annotation(self):
        """Test BM25Score annotation."""
        results = Article.objects.annotate(
            score=BM25Score("content", "postgresql", index_name="article_content_bm25")
        ).order_by("score")

        assert results.count() >= 1
        first = results.first()
        assert hasattr(first, "score")
        assert first.score < 0  # Negative score


@pytest.mark.django_db
class TestPostgreSQLVersion:
    """Tests for PostgreSQL version checking."""

    def test_postgresql_is_17_or_higher(self):
        """Verify PostgreSQL version is 17+."""
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version_num")
            version_num = int(cursor.fetchone()[0])
            major_version = version_num // 10000

        assert major_version >= 17, f"PostgreSQL {major_version} found, need 17+"


@pytest.mark.django_db
class TestPgTextsearchExtension:
    """Tests for pg_textsearch extension availability."""

    def test_pg_textsearch_installed(self):
        """Verify pg_textsearch extension is installed."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_textsearch')"
            )
            installed = cursor.fetchone()[0]

        assert installed, "pg_textsearch extension not installed"

    def test_bm25_index_method_exists(self):
        """Verify bm25 index access method exists."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_am WHERE amname = 'bm25')")
            exists = cursor.fetchone()[0]

        assert exists, "bm25 index access method not available"
