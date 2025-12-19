from .indexes import BM25Index
from .search import BM25SearchQuerySet


class BM25Searchable:
    """
    Mixin that adds BM25 full-text search to Django models.

    Usage:
        class Article(BM25Searchable, models.Model):
            title = models.CharField(max_length=255)
            content = models.TextField()

            class Meta:
                indexes = [
                    BM25Index(fields=['content'], name='article_content_bm25'),
                ]

        # Search
        results = Article.search("query")
        results = Article.search("query").filter(author="John")[:10]
    """

    @classmethod
    def _get_bm25_index(cls):
        """
        Find BM25Index from Meta.indexes.

        Returns:
            BM25Index instance

        Raises:
            ValueError: If no BM25Index found on model
        """
        for index in cls._meta.indexes:
            if isinstance(index, BM25Index):
                return index
        raise ValueError(
            f"No BM25Index found on {cls.__name__}. Add BM25Index to Meta.indexes."
        )

    @classmethod
    def search(cls, query):
        """
        Perform BM25 full-text search.

        Args:
            query: The search query string

        Returns:
            BM25SearchQuerySet ordered by relevance (lower score = better match)

        Example:
            Article.search("postgresql database")
            Article.search("django").filter(published=True)[:5]
        """
        if not query:
            return cls.objects.none()

        index = cls._get_bm25_index()
        field = index.fields[0]
        index_name = index.name

        return BM25SearchQuerySet(cls, query, field, index_name)
