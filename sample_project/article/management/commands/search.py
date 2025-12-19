from django.core.management.base import BaseCommand

from article.models import Article


class Command(BaseCommand):
    help = "Search articles using BM25 full-text search"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="Search query")
        parser.add_argument("--limit", type=int, default=5, help="Maximum number of results")
        parser.add_argument(
            "--threshold",
            type=float,
            default=None,
            help="Score threshold for filtering (e.g., -1.0)",
        )

    def handle(self, *args, **options):
        query = options["query"]
        limit = options["limit"]
        threshold = options["threshold"]

        self.stdout.write(f"\nSearching for: '{query}'\n")
        self.stdout.write("-" * 60)

        # Use new simple API
        results = Article.search(query)

        # Apply threshold filter if specified
        if threshold is not None:
            self.stdout.write(f"Using threshold: {threshold}\n")
            results = results.filter(bm25_score__lt=threshold)

        # Apply limit
        results = results[:limit]

        if not results:
            self.stdout.write(self.style.WARNING("No results found"))
            return

        count = 0
        for i, article in enumerate(results, 1):
            score = getattr(article, "bm25_score", "N/A")
            self.stdout.write(f"\n{i}. {article.title}")
            self.stdout.write(f"   Author: {article.author}")
            self.stdout.write(f"   Score: {score}")
            self.stdout.write(f"   Content: {article.content[:100]}...")
            count += 1

        self.stdout.write("\n" + "-" * 60)
        self.stdout.write(self.style.SUCCESS(f"Found {count} results"))
