from django.db import models

from django_hawkeye import BM25Index, BM25Searchable


class Article(BM25Searchable, models.Model):
    """Article model with BM25 full-text search."""

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            BM25Index(fields=["content"], name="article_content_bm25"),
        ]

    def __str__(self):
        return self.title
