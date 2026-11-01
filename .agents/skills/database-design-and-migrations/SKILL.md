---
name: database-design-and-migrations
description: Database schema design, relational/NoSQL modeling, indexing, query optimization, and safe zero-downtime migrations. Use when creating schemas, writing SQL/ORM migrations (Prisma, Drizzle, Alembic), diagnosing slow queries, or resolving N+1 issues.
---

# Database Design and Migrations

Use this skill when designing database schemas, planning data migrations, indexing tables, and optimizing queries.

## 1. Schema Modeling & Design
- **Normalize first, denormalize deliberately:** Aim for 3NF for transactional tables (OLTP). Denormalize only when verified read bottlenecks justify the cost of data synchronization.
- **Data Types & Constraints:**
  - Always enforce integrity at the engine level: `NOT NULL`, `FOREIGN KEY ... ON DELETE RESTRICT/CASCADE`, `CHECK` constraints, and `UNIQUE` constraints.
  - Choose exact types: UUIDv7 or BigInt for primary keys; `TIMESTAMPTZ` for timestamps; avoid unbounded `VARCHAR` or generic JSON blobs for structured relational data.
- **Naming Conventions:** Consistent snake_case for tables and columns (`created_at`, `user_id`, `orders`). Use singular or plural consistently across the project.

## 2. Indexing Strategy
- **Index foreign keys:** Every foreign key column that participates in joins should have an index.
- **Composite Index Order (ESR Rule):**
  1. **Equality** columns first.
  2. **Sort** columns second.
  3. **Range** columns last.
- **Partial & Covering Indexes:** Use partial indexes (`WHERE deleted_at IS NULL` or `WHERE status = 'active'`) to keep index size minimal and hot cache hit rates high.
- **Avoid Over-indexing:** Every index adds write latency on INSERT/UPDATE/DELETE. Monitor index usage and drop unused indexes.

## 3. Safe Migrations (Zero Downtime)
- **Expand / Contract Pattern:**
  1. **Phase 1 (Expand):** Add the new column or table as nullable. Do not remove old columns yet.
  2. **Phase 2 (Dual-write / Backfill):** Update application code to write to both or backfill in small batches (`LIMIT 1000`).
  3. **Phase 3 (Contract):** Point application code entirely to the new schema, then drop old columns/tables in a separate migration.
- **Locking & Concurrency:**
  - In PostgreSQL, create indexes concurrently: `CREATE INDEX CONCURRENTLY`.
  - Avoid setting default values on large existing tables without careful locking considerations.
  - Set tight lock timeouts: `SET lock_timeout = '3s';` before running schema modifications on production.

## 4. Query Optimization & Diagnostics
- **N+1 Detection:** Watch for ORM queries executing in loops. Always use eager loading (`include`, `with`, `select_related`, `joinedload`) or batch DataLoader.
- **Execution Plan Analysis:**
  - Always run `EXPLAIN (ANALYZE, BUFFERS)` in Postgres or `EXPLAIN FORMAT=JSON` in MySQL.
  - Hunt for **Seq Scan** on large tables, costly disk spill sorts, and high buffer hit counts.
