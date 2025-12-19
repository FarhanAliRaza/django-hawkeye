from .expressions import BM25Score


class BM25SearchQuerySet:
    """
    A QuerySet-like wrapper for BM25 search results.

    Provides a chainable interface similar to Django QuerySet,
    with automatic BM25 scoring and ordering.

    Usage:
        results = Article.search("query")
        results = Article.search("query").filter(author="John")[:10]
    """

    def __init__(self, model, query, field, index_name):
        self.model = model
        self.query = query
        self.field = field
        self.index_name = index_name
        self._qs = None

    @property
    def _queryset(self):
        """Lazy-build the annotated queryset."""
        if self._qs is None:
            self._qs = self.model.objects.annotate(
                bm25_score=BM25Score(self.field, self.query, index_name=self.index_name)
            ).order_by("bm25_score")
        return self._qs

    def _clone(self):
        """Create a copy of this search queryset."""
        clone = BM25SearchQuerySet(self.model, self.query, self.field, self.index_name)
        if self._qs is not None:
            clone._qs = self._qs.all()
        return clone

    # Chainable methods
    def filter(self, *args, **kwargs):
        """Filter results - chainable."""
        clone = self._clone()
        clone._qs = clone._queryset.filter(*args, **kwargs)
        return clone

    def exclude(self, *args, **kwargs):
        """Exclude results - chainable."""
        clone = self._clone()
        clone._qs = clone._queryset.exclude(*args, **kwargs)
        return clone

    def select_related(self, *args):
        """Add select_related - chainable."""
        clone = self._clone()
        clone._qs = clone._queryset.select_related(*args)
        return clone

    def prefetch_related(self, *args):
        """Add prefetch_related - chainable."""
        clone = self._clone()
        clone._qs = clone._queryset.prefetch_related(*args)
        return clone

    def only(self, *fields):
        """Limit fields - chainable."""
        clone = self._clone()
        clone._qs = clone._queryset.only(*fields)
        return clone

    def defer(self, *fields):
        """Defer fields - chainable."""
        clone = self._clone()
        clone._qs = clone._queryset.defer(*fields)
        return clone

    # QuerySet interface - iteration and access
    def __iter__(self):
        return iter(self._queryset)

    def __len__(self):
        return len(self._queryset)

    def __getitem__(self, k):
        return self._queryset[k]

    def __bool__(self):
        return self._queryset.exists()

    def __repr__(self):
        return f"<BM25SearchQuerySet for {self.model.__name__}: '{self.query}'>"

    # QuerySet methods
    def count(self):
        """Return the count of results."""
        return self._queryset.count()

    def first(self):
        """Return the first result."""
        return self._queryset.first()

    def last(self):
        """Return the last result."""
        return self._queryset.last()

    def exists(self):
        """Check if any results exist."""
        return self._queryset.exists()

    def values(self, *fields):
        """Return values dict."""
        return self._queryset.values(*fields)

    def values_list(self, *fields, **kwargs):
        """Return values list."""
        return self._queryset.values_list(*fields, **kwargs)

    def all(self):
        """Return a clone of this queryset."""
        return self._clone()

    def none(self):
        """Return an empty queryset."""
        clone = self._clone()
        clone._qs = self.model.objects.none()
        return clone
