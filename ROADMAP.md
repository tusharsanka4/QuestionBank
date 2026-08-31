# Question Bank Roadmap

This roadmap turns Question Bank into a reliable, secure portfolio application while keeping the project within free tiers. The goal is to demonstrate sound production engineering, not to build infrastructure for large-scale public traffic.

## Project constraints

- [ ] Keep hosting, storage, databases, monitoring, and APIs within free-tier limits.
- [ ] Prefer simple managed services or small self-contained components over enterprise infrastructure.
- [ ] Add configurable limits so an unexpected user cannot create a bill.
- [ ] Document any feature that cannot be offered continuously within a free tier.
- [ ] Keep local development possible without paid services.
- [ ] Never commit API keys, credentials, uploaded PDFs, or user data.

## Suggested free-tier architecture

The exact providers can be selected during implementation. A sensible target is:

- Frontend: Vercel free tier or an equivalent static host.
- API: Railway while its available allowance is sufficient, or another free-tier host.
- Application database and vectors: Supabase Postgres with `pgvector`, or another free Postgres service.
- File storage: Supabase Storage or Cloudflare R2 within its free allowance.
- Background work: a database-backed job table and a lightweight worker, avoiding paid Redis initially.
- Authentication: Supabase Auth or Google OAuth with backend verification.
- Monitoring: structured logs, provider dashboards, and Sentry's free tier.
- CI: GitHub Actions free allowance for a public repository or the applicable private-repository allowance.

Provider choices should remain replaceable through environment variables and small adapter modules.

## Milestone 0: Baseline and documentation

- [x] Replace the Vite template README with project documentation.
- [x] Document local frontend and backend setup.
- [x] Add `.env.example` files containing variable names but no secrets.
- [x] Validate required environment variables at backend startup.
- [x] Move the hardcoded backend URL to `VITE_API_URL`.
- [x] Pin/document supported Python and Node versions.
- [x] Curate `requirements.txt` to direct, necessary dependencies.
- [x] Remove unused starter assets and unused dependencies.
- [x] Decide whether the product remains document Q&A or expands into question-bank generation.
- [ ] Record the selected free-tier providers and their relevant limits.
- [ ] Add a small architecture diagram showing the frontend, API, authentication, storage, database/vector search, and AI/search providers.
- [ ] Start lightweight architecture decision records for important choices such as authentication, vector storage, and hosting.

## Milestone 1: Secure file and session ownership

### Identity and authorization

- [x] Add user sign-in using a free authentication provider.
- [x] Verify authentication tokens on the backend rather than trusting frontend identity data.
- [ ] Define durable `users`, `conversations`, and `documents` records.
- [ ] Associate every conversation and document with an owner.
- [ ] Require authorization for upload, query, reset, document access, and deletion.
- [ ] Reject unknown or client-invented session/conversation IDs.
- [ ] Add logout and expired-token handling.
- [ ] Test that one user cannot access another user's conversations or documents.
- [ ] Optionally support anonymous demos with short retention and strict quotas.

### API and upload security

- [ ] Restrict CORS to configured frontend origins.
- [ ] Validate question length and request shape.
- [ ] Validate file extension case-insensitively.
- [ ] Validate PDF MIME type and file signature, not just the filename.
- [ ] Add maximum file-size and page-count limits appropriate to free-tier resources.
- [ ] Sanitize filenames or replace them with generated internal names.
- [ ] Use safe temporary paths and guarantee cleanup with `finally`.
- [ ] Handle empty, corrupt, encrypted, and unsupported PDFs explicitly.
- [ ] Add processing timeouts and memory-conscious limits.
- [ ] Configure trusted hosts and appropriate security headers.
- [ ] Ensure sensitive responses are not cached publicly.
- [ ] Avoid logging tokens, document contents, prompts, or secrets.

### AI-specific security

- [ ] Treat document and web content as untrusted data in system instructions.
- [ ] Prevent retrieved text from overriding system or tool-use policy.
- [ ] Place a hard limit on agent/tool steps.
- [ ] Prevent document content from causing arbitrary data-bearing web searches.
- [ ] Add a clear privacy notice describing third-party AI/search processing.

## Milestone 2: Durable storage

### Database

- [ ] Select a free-tier Postgres provider with `pgvector` support if possible.
- [ ] Add a migration system.
- [ ] Create tables for users, conversations, messages, documents, chunks, and jobs.
- [ ] Add ownership, timestamps, status, and deletion fields to relevant records.
- [ ] Replace the in-memory `session_histories` dictionary.
- [ ] Persist messages and load conversation history from the database.
- [ ] Add pagination or limits for long conversations.
- [ ] Add database constraints and indexes for ownership and lookup paths.

### Documents and vectors

- [ ] Store original PDFs in private free-tier object storage where practical.
- [ ] Use generated object keys rather than user filenames.
- [ ] Store original filename and safe metadata separately.
- [ ] Replace local Chroma persistence with shared durable vector storage.
- [ ] Store document ID, filename, page, chunk order, and section metadata with every chunk.
- [ ] Hash uploads to detect accidental duplicates.
- [ ] Make ingestion idempotent so retries do not duplicate chunks.
- [ ] Document backup and restore behavior offered by the selected free-tier providers.
- [ ] Confirm the app behaves correctly after API restart and redeployment.

## Milestone 3: Honest error handling

### Backend

- [ ] Define a consistent structured error response with code, message, and request ID.
- [ ] Add explicit API response models.
- [ ] Translate expected failures into safe HTTP status codes.
- [ ] Do not expose stack traces or provider secrets to clients.
- [ ] Handle model, search, database, storage, and parsing failures separately.
- [ ] Add explicit upstream timeouts.
- [ ] Retry only transient and idempotent operations with bounded backoff.
- [ ] Guarantee temporary resource cleanup after success or failure.
- [ ] Return `409` or another clear state error when a document is not ready to query.

### Frontend

- [ ] Check `response.ok` for every request.
- [ ] Parse and display structured server errors.
- [ ] Replace fixed upload timers with real backend status.
- [ ] Model explicit states: uploading, queued, processing, ready, failed, and deleting.
- [ ] Do not enter chat when upload or ingestion fails.
- [ ] Add safe retry actions for session creation, upload, processing, and queries.
- [ ] Add disconnected/offline and provider-unavailable states.
- [ ] Ensure malformed or empty API responses do not break the UI.

## Milestone 4: Background ingestion

For a portfolio/free-tier project, start with a Postgres-backed jobs table and one lightweight worker. Redis, Kafka, and managed queue products are unnecessary unless the project later needs them.

- [ ] Create an ingestion job when a PDF upload completes.
- [ ] Return quickly with a document and job ID.
- [ ] Add job states: queued, processing, ready, failed, and cancelled.
- [ ] Run parsing, chunking, and embedding outside the request handler.
- [ ] Add one lightweight worker process or provider-supported background task.
- [ ] Let the frontend poll job status at a conservative interval.
- [ ] Add basic progress information where it can be measured honestly.
- [ ] Apply job timeouts and bounded retry counts.
- [ ] Make job claiming safe so two workers cannot process the same job simultaneously.
- [ ] Make every processing step idempotent.
- [ ] Record a safe failure reason for inspection and user feedback.
- [ ] Clean up partial chunks and stored files after terminal failures when appropriate.
- [ ] Consider OCR for scanned PDFs only if it can run within free compute limits.

## Milestone 5: Deletion and retention

- [ ] Define a documented retention policy for authenticated and anonymous users.
- [ ] Add a frontend control and API endpoint to delete one document.
- [ ] Add a control to clear a conversation.
- [ ] Make reset semantics explicit: chat only, documents only, or both.
- [ ] Add account/data deletion if persistent accounts are introduced.
- [ ] Delete the original object, chunks/vectors, document record, and related jobs.
- [ ] Make deletion idempotent and safe to retry.
- [ ] Handle deletion during active ingestion.
- [ ] Add `expires_at` to anonymous or temporary data.
- [ ] Add a scheduled cleanup job for expired sessions, failed uploads, and orphaned data.
- [ ] Purge abandoned temporary files.
- [ ] Verify that deleted content is not returned by retrieval.
- [ ] Document provider backup-retention limitations honestly.
- [ ] Track storage usage so free-tier limits are not silently exhausted.

## Milestone 6: Rate limits and cost controls

- [ ] Add per-IP limits for unauthenticated session creation and login-sensitive endpoints.
- [ ] Add per-user query and upload limits.
- [ ] Limit concurrent queries and ingestion jobs per user.
- [ ] Limit total document count and stored bytes per user.
- [ ] Limit PDF pages and extracted characters.
- [ ] Add daily model-token and web-search budgets.
- [ ] Add a global concurrency ceiling for model and embedding calls.
- [ ] Return `429 Too Many Requests` with a useful retry time.
- [ ] Display quota information and quota errors clearly in the frontend.
- [ ] Fail closed when a free-tier budget is exhausted rather than creating a bill.
- [ ] Make web-search fallback optional or explicitly user-triggered to control quota usage.
- [ ] Add provider usage alerts wherever free dashboards support them.

## Milestone 7: Citation and answer quality

### Ingestion and retrieval

- [ ] Preserve document ID, filename, page number, section, and chunk order.
- [ ] Improve chunking to respect paragraphs and headings.
- [ ] Include similarity scores in internal retrieval results.
- [ ] Add a relevance threshold instead of always returning the nearest chunks.
- [ ] Add lightweight keyword/vector hybrid retrieval if supported by the selected database.
- [ ] Add reranking only if a free/local option improves evaluation results enough to justify it.
- [ ] Support selecting which uploaded documents are searched.
- [ ] Handle duplicate uploads and document versions.
- [ ] Evaluate scanned PDFs, tables, columns, equations, and multilingual documents.

### Grounded answers

- [ ] Return structured citations instead of asking the model to invent citation formatting.
- [ ] Cite filename and page for document evidence.
- [ ] Preserve web URLs and titles for web evidence.
- [ ] Clearly distinguish document evidence from web information.
- [ ] Require the answer to say when the documents do not contain sufficient evidence.
- [ ] Validate that every emitted citation corresponds to a retrieved source.
- [ ] Avoid web fallback when the user asks for document-only answers.
- [ ] Add a clickable source panel or passage preview in the frontend.
- [ ] Render safe Markdown and links.
- [ ] Create a small evaluation dataset with expected answers and source pages.
- [ ] Measure answer correctness, retrieval relevance, citation correctness, and refusal quality.
- [ ] Add representative acceptance scenarios for document Q&A, web fallback, and question-bank generation.
- [ ] Keep document-grounded answers and web-assisted answers as explicit, separately testable paths.

## Milestone 8: Monitoring and tests

### Observability

- [ ] Add structured JSON logging in production.
- [ ] Generate a request ID for every API request and return it in errors.
- [ ] Propagate IDs through background jobs.
- [ ] Add privacy-safe logs for request outcome, latency, job state, and provider errors.
- [ ] Add Sentry or an equivalent free-tier error tracker.
- [ ] Track API latency, error rate, ingestion duration, and ingestion failure rate.
- [ ] Track queue depth, storage usage, model calls, tokens, web searches, and estimated cost.
- [ ] Split liveness and readiness health checks.
- [ ] Make readiness verify essential database/storage connectivity without spending model quota.
- [ ] Configure free provider alerts for outages, usage limits, and storage pressure.

### Automated testing

- [ ] Add backend unit tests.
- [ ] Add API integration tests with a temporary test database.
- [ ] Add authorization tests proving cross-user access is denied.
- [ ] Test valid, empty, corrupt, encrypted, scanned, oversized, and duplicate PDFs.
- [ ] Test ingestion retries and idempotency.
- [ ] Test deletion of files, chunks, messages, and jobs.
- [ ] Test concurrent upload/query/delete behavior.
- [ ] Add frontend component tests for success and error states.
- [ ] Add an end-to-end upload, processing, query, citation, and deletion test.
- [ ] Add RAG evaluation tests using small non-sensitive fixtures.
- [ ] Add a lightweight golden-dataset test suite with documented quality thresholds.
- [ ] Add basic load tests sized for expected portfolio-demo traffic.
- [ ] Run linting, tests, and builds in GitHub Actions.
- [ ] Add dependency vulnerability scanning and automated update PRs where free.

## Milestone 9: UX, accessibility, and maintainability

These items can be implemented throughout the earlier milestones.

### UX

- [ ] Show uploaded document name, size, page count, and processing state.
- [ ] Add a document list with delete and retry controls.
- [ ] Add upload progress where supported.
- [ ] Add drag-and-drop and same-file re-selection support.
- [ ] Auto-scroll chat to the newest message.
- [ ] Add response streaming if it remains simple and free.
- [ ] Add stop, retry/regenerate, and copy controls.
- [ ] Add a visible new-conversation/reset action.
- [ ] Use a multiline input with a documented keyboard shortcut.
- [ ] Handle mobile viewport, safe-area, keyboard, and long-content issues.

### Accessibility

- [ ] Add accessible names to icon-only controls.
- [ ] Announce upload, processing, thinking, success, and failure states with ARIA live regions.
- [ ] Ensure complete keyboard navigation and visible focus states.
- [ ] Verify color contrast.
- [ ] Make Framer Motion respect reduced-motion preferences.
- [ ] Test zoom, screen-reader landmarks, and mobile layouts.

### Maintainability

- [ ] Split frontend API access, state management, and UI into focused modules/components.
- [ ] Replace timer-driven UI transitions with backend-derived state.
- [ ] Centralize backend configuration and model construction.
- [ ] Introduce repository/service boundaries for database, storage, retrieval, and providers.
- [ ] Add type hints and Pydantic models for domain and API data.
- [ ] Consider TypeScript or runtime schema validation for frontend API contracts.
- [ ] Add Python formatting, linting, and type checking.
- [ ] Document architecture and key tradeoffs for portfolio reviewers.
- [ ] Maintain a short risk register covering free-tier exhaustion, provider downtime, unsafe PDFs, prompt injection, and data leakage.

## Explicitly out of scope unless the project grows

These are valid enterprise concerns but are not necessary for a free-tier portfolio demonstration:

- [ ] Multi-region deployment.
- [ ] Kubernetes.
- [ ] Kafka or other large event-streaming infrastructure.
- [ ] Paid Redis/managed queues when a database-backed queue is sufficient.
- [ ] High-availability database clusters.
- [ ] Complex organization roles and enterprise SSO.
- [ ] Formal compliance certification.
- [ ] Large-scale disaster-recovery automation.
- [ ] Always-on high-volume OCR or GPU inference.

The project should still document these boundaries rather than implying that it supports enterprise-scale workloads.

## Recommended implementation order

- [ ] Milestone 0: Baseline and documentation
- [ ] Milestone 1: Secure file and session ownership
- [ ] Milestone 2: Durable storage
- [ ] Milestone 3: Honest error handling
- [ ] Milestone 4: Background ingestion
- [ ] Milestone 5: Deletion and retention
- [ ] Milestone 6: Rate limits and cost controls
- [ ] Milestone 7: Citation and answer quality
- [ ] Milestone 8: Monitoring and tests
- [ ] Milestone 9: UX, accessibility, and maintainability

Each milestone should define a concrete deliverable, a validation command or test,
and at least one acceptance scenario. It should be completed with documentation
and tests before its top-level checkbox is marked complete.
