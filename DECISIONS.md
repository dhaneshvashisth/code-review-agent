# Architectural Decisions

## Why LangGraph over plain LangChain?
LangGraph enables stateful multi-agent graphs with parallel execution and
conditional routing. Plain LangChain chains are sequential only.

## Why parallel agent execution?
Bug detection, quality checking, and security analysis are independent.
Running them in parallel reduces review time by ~66%.

## Why Pydantic for config?
pydantic-settings validates all env variables at startup. Missing or
wrong-type variables cause immediate startup failure with clear error messages
rather than silent runtime failures.

## Why each agent returns only its own key, not full state?
Returning {**state, result} from parallel nodes causes all agents to
overwrite every key simultaneously — including keys owned by other agents.
Each agent returns only the single key it owns, preventing write conflicts.

## Why SHA256 for caching?
Comparing full code text for duplicates is slow on large submissions.
SHA256 produces a fixed 64-char hash — comparison is O(1) regardless of code size.

## Why SHA256 over MD5 for code hashing?
MD5 has known collision vulnerabilities — two different inputs can produce
the same hash. SHA256 is cryptographically stronger with no known collisions,
making it reliable for cache key generation.

## Why UUID primary keys?
UUIDs are globally unique and don't expose record counts to users.
Auto-increment integers let users guess other review IDs.

## Why asyncpg over psycopg2?
asyncpg is a native async PostgreSQL driver. psycopg2 is sync and would
block the FastAPI event loop on every DB call.

## Why tenacity for retries?
OpenAI API has rate limits and occasional timeouts. Tenacity handles
exponential backoff automatically — 3 retries with 2s, 4s, 8s delays.

## Why Annotated reducers in LangGraph state?
When multiple agents run in parallel, all of them try to write to the shared
state simultaneously. Without Annotated reducers, LangGraph throws
InvalidUpdateError. The keep_last reducer tells LangGraph to accept the
most recent write when parallel agents update the same key.


