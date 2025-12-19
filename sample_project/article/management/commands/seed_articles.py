# ruff: noqa: E501
from django.core.management.base import BaseCommand

from article.models import Article

# Realistic content for Elasticsearch replacement demo
# Common use cases: e-commerce, documentation, support tickets, blog posts
SAMPLE_ARTICLES = [
    # E-commerce product descriptions
    {
        "title": "MacBook Pro 16-inch M3 Max",
        "content": """The MacBook Pro 16-inch with M3 Max chip delivers exceptional performance for professional workflows. Features include up to 128GB unified memory, 8TB SSD storage, and a stunning Liquid Retina XDR display with ProMotion technology. The M3 Max chip provides up to 16-core CPU and 40-core GPU, making it ideal for video editing, 3D rendering, and software development. Battery life extends up to 22 hours, and the laptop includes a 140W USB-C power adapter with MagSafe 3 charging. Available in Space Black and Silver finishes. Perfect for developers, video editors, and creative professionals who need desktop-class performance in a portable form factor.""",
        "author": "Product Team",
    },
    {
        "title": "Sony WH-1000XM5 Wireless Headphones",
        "content": """Industry-leading noise cancellation headphones with exceptional sound quality. The WH-1000XM5 features two processors controlling 8 microphones for unprecedented noise cancellation. With 30-hour battery life and quick charging (3 minutes for 3 hours playback), these headphones are perfect for travel and commuting. The new synthetic leather design is lighter and more comfortable than previous generations. Multipoint connection allows pairing with two devices simultaneously. Speak-to-Chat automatically pauses music when you start talking. LDAC codec support delivers Hi-Res Audio wirelessly. Includes carrying case, USB-C cable, and audio cable for wired listening.""",
        "author": "Product Team",
    },
    {
        "title": "Herman Miller Aeron Chair Remastered",
        "content": """The iconic ergonomic office chair redesigned for modern workspaces. Features 8Z Pellicle suspension material that provides cooling comfort and eliminates pressure points. PostureFit SL supports the natural S-shape of your spine with adjustable sacral and lumbar pads. Tilt limiter with seat angle adjustment lets you customize your recline range. Available in three sizes (A, B, C) to fit different body types. Graphite, Carbon, and Mineral color options. 12-year warranty covers all moving parts. Assembly required but straightforward with included tools. Ideal for programmers, designers, and anyone spending long hours at a desk.""",
        "author": "Product Team",
    },
    # Technical documentation
    {
        "title": "Getting Started with Kubernetes Deployments",
        "content": """This guide covers deploying applications to Kubernetes clusters. A Deployment provides declarative updates for Pods and ReplicaSets. You describe a desired state in a Deployment, and the Deployment Controller changes the actual state to the desired state at a controlled rate. Use kubectl create deployment to create a new deployment, or kubectl apply -f deployment.yaml for declarative configuration. Key fields include replicas (number of pod instances), selector (how the deployment finds pods to manage), and template (pod specification). Rolling updates allow zero-downtime deployments by gradually replacing old pods with new ones. Rollback to previous versions using kubectl rollout undo. Monitor deployment status with kubectl rollout status.""",
        "author": "DevOps Team",
    },
    {
        "title": "PostgreSQL Performance Tuning Guide",
        "content": """Optimize your PostgreSQL database for production workloads. Start with shared_buffers, typically set to 25% of available RAM. Configure effective_cache_size to 50-75% of total memory. Enable huge_pages for databases over 8GB. Use pg_stat_statements extension to identify slow queries. Create indexes strategically - B-tree for equality and range queries, GIN for full-text search and JSONB, BRIN for large sequential data. Analyze query plans with EXPLAIN ANALYZE to understand execution paths. Configure autovacuum aggressively for write-heavy workloads. Use connection pooling with PgBouncer for applications with many short-lived connections. Monitor with pg_stat_activity and set appropriate statement_timeout values.""",
        "author": "Database Team",
    },
    {
        "title": "React Server Components Architecture",
        "content": """React Server Components (RSC) enable rendering components on the server, reducing client-side JavaScript bundle size. Server Components can directly access backend resources like databases and filesystems without API endpoints. They cannot use state, effects, or browser-only APIs. Client Components handle interactivity and are marked with 'use client' directive. The boundary between server and client components is flexible - server components can import client components but not vice versa. Data fetching in server components uses async/await directly. Streaming with Suspense enables progressive rendering. Next.js App Router implements RSC by default. Benefits include improved initial page load, better SEO, and reduced client bundle size.""",
        "author": "Frontend Team",
    },
    # Support tickets / Issues
    {
        "title": "URGENT: Production database connection timeout errors",
        "content": """Since deploying version 2.4.1, we're seeing intermittent database connection timeouts in production. Error message: "FATAL: too many connections for role postgres". Current connection pool size is 20, max_connections in PostgreSQL is 100. Application logs show connections not being released properly after transactions. Suspect the new ORM upgrade introduced a connection leak. Temporary workaround: restarting application pods every 4 hours. Need to investigate connection lifecycle in the updated database driver. Affecting approximately 5% of API requests during peak hours. Customer impact: intermittent 500 errors on checkout flow. Priority: P1. Assigned to backend team for immediate investigation.""",
        "author": "SRE Team",
    },
    {
        "title": "Feature Request: Export dashboard data to CSV",
        "content": """Multiple enterprise customers have requested the ability to export dashboard analytics data to CSV format. Current workaround requires using the API directly which is not accessible to non-technical users. Requested features: 1) Export button on each dashboard widget, 2) Bulk export for entire dashboard, 3) Scheduled exports via email, 4) Custom date range selection for exports. Business justification: Three Fortune 500 clients have this as a blocker for contract renewal. Estimated revenue impact: $450K ARR. Competitor analysis shows Datadog and Grafana both offer this functionality. Proposed timeline: MVP with basic export in Q2, scheduled exports in Q3. Requires backend API endpoints and frontend UI components.""",
        "author": "Product Manager",
    },
    {
        "title": "Bug: Search results not updating after content edit",
        "content": """Users report that after editing article content, search results still show old content snippets. Steps to reproduce: 1) Create new article with specific keywords, 2) Verify article appears in search results, 3) Edit article to change keywords, 4) Search for new keywords - article not found, 5) Search for old keywords - article still appears with old snippet. Expected: Search index should update within 5 minutes of content change. Actual: Index appears stale for up to 24 hours. Environment: Production, affects all tenants. Root cause: Elasticsearch index refresh interval set to 24h instead of 5m. Related to commit abc123 that modified index settings. Fix: Update refresh_interval in index template and reindex existing documents.""",
        "author": "QA Team",
    },
    # Blog posts / Content
    {
        "title": "Why We Migrated from Elasticsearch to PostgreSQL Full-Text Search",
        "content": """After running Elasticsearch for 3 years, we decided to migrate our search infrastructure to PostgreSQL's native full-text search capabilities. The primary drivers were operational complexity and cost. Our Elasticsearch cluster required dedicated DevOps attention, frequent version upgrades, and careful capacity planning. With pg_textsearch extension on PostgreSQL 17, we achieved comparable search quality with BM25 ranking while eliminating an entire infrastructure component. Migration took 6 weeks including testing. Search latency improved from 150ms to 45ms for 90th percentile queries. Cost savings of approximately $2,400/month in infrastructure plus reduced on-call burden. Trade-offs: lost some advanced features like fuzzy matching and aggregations, but these weren't critical for our use case.""",
        "author": "Engineering Blog",
    },
    {
        "title": "Building a Real-Time Notification System with WebSockets",
        "content": """This post walks through implementing a scalable real-time notification system. Architecture overview: Django Channels for WebSocket handling, Redis for pub/sub messaging, PostgreSQL for notification persistence. Each user establishes a WebSocket connection on login. Notifications are published to Redis channels and broadcast to connected clients. Offline users receive notifications on next login via database query. Scaling considerations: Redis Cluster for horizontal scaling, sticky sessions for WebSocket connections, connection state management. Code examples include consumer classes, routing configuration, and frontend JavaScript client. Performance testing showed support for 10,000 concurrent connections per server instance. Deployment on Kubernetes with Nginx Ingress for WebSocket termination.""",
        "author": "Engineering Blog",
    },
    {
        "title": "Implementing Authentication with OAuth 2.0 and OpenID Connect",
        "content": """Comprehensive guide to implementing secure authentication in modern web applications. OAuth 2.0 provides authorization framework while OpenID Connect adds identity layer. Key concepts: authorization code flow for server-side apps, PKCE extension for mobile and SPA clients, refresh token rotation for security. Implementation steps: register application with identity provider, configure redirect URIs, implement token exchange endpoint, validate ID tokens using JWKS. Security best practices: always use HTTPS, validate state parameter to prevent CSRF, store tokens securely (httpOnly cookies for web, secure storage for mobile), implement token revocation on logout. Popular providers: Auth0, Okta, Google, Azure AD. Libraries: authlib for Python, passport.js for Node.""",
        "author": "Security Team",
    },
    # Knowledge base
    {
        "title": "Troubleshooting: Application crashes on startup",
        "content": """Common causes and solutions for application startup failures. Error: 'ModuleNotFoundError' - Ensure all dependencies are installed with pip install -r requirements.txt. Check virtual environment is activated. Error: 'Connection refused' to database - Verify database server is running, check connection string in environment variables, confirm network connectivity and firewall rules. Error: 'Permission denied' - Check file permissions on log directories, verify user has access to required ports (use ports > 1024 for non-root). Error: 'Address already in use' - Another process using the port, find with lsof -i :8000, kill or change port. Memory errors - Increase container memory limits, check for memory leaks in application code. Enable debug logging with DEBUG=true for detailed startup information.""",
        "author": "Support Team",
    },
    {
        "title": "API Rate Limiting and Throttling Best Practices",
        "content": """Protect your API from abuse while ensuring good user experience. Rate limiting strategies: fixed window (simple but allows bursts), sliding window (smoother distribution), token bucket (allows controlled bursts), leaky bucket (constant rate). Implementation: use Redis for distributed rate limiting across multiple server instances. Response headers: include X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset. Return 429 Too Many Requests with Retry-After header when limit exceeded. Differentiate limits by authentication level - higher limits for paid tiers. Consider separate limits for different endpoint categories (reads vs writes). Implement gradual backoff for repeated violations. Monitor rate limit hits to adjust thresholds. Client SDKs should implement automatic retry with exponential backoff.""",
        "author": "API Team",
    },
    {
        "title": "Data Backup and Disaster Recovery Procedures",
        "content": """Comprehensive backup strategy for production systems. Database backups: daily full backups with pg_dump, continuous WAL archiving for point-in-time recovery, test restores monthly. File storage: incremental backups to S3 with versioning enabled, cross-region replication for critical assets. Configuration: infrastructure as code in Git, secrets in HashiCorp Vault with regular rotation. Recovery objectives: RPO (Recovery Point Objective) of 1 hour, RTO (Recovery Time Objective) of 4 hours. Disaster recovery runbook: 1) Assess incident scope, 2) Notify stakeholders, 3) Provision recovery environment, 4) Restore from latest backup, 5) Verify data integrity, 6) Update DNS/load balancers, 7) Post-incident review. Annual DR drills required for SOC 2 compliance.""",
        "author": "Infrastructure Team",
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample articles for search demo"

    def handle(self, *args, **options):
        self.stdout.write("Deleting existing articles...")
        Article.objects.all().delete()

        self.stdout.write("Creating sample articles...")
        for article_data in SAMPLE_ARTICLES:
            Article.objects.create(**article_data)
            self.stdout.write(f"  Created: {article_data['title']}")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(SAMPLE_ARTICLES)} articles")
        )
