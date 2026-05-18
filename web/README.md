# KMG Web — Nuxt 4 frontend

The immersive frontend for the Knowledge Memory Graph SaaS. Vue 3.5 / Nuxt 4 /
shadcn-style primitives / Tailwind v4 / Vue Flow / Tiptap v3. Hybrid theming:
Framer dark for the workspace shell + graph + canvas, Mintlify light for the
wiki reading pane.

## Quick start

```bash
nvm use                # Node 22 (Nuxt 4 needs Node ≥22 for require(esm) parity)
cd web
pnpm install
cp .env.example .env   # set KMG_API_BASE_URL and KMG_API_KEY
pnpm dev               # http://localhost:3000
```

Run the FastAPI side via `docker compose up api worker postgres redis qdrant minio`
from the repo root.

In dev, sign in via `/auth/login` with any tenant UUID — the FastAPI dev bypass
accepts an `X-Tenant-Id` header when `KMG_ENV != production`.

## Layout

```
app/
  app.vue                      # root, applies data-skin
  middleware/auth.global.ts    # gates /app/* on a tenant in localStorage
  layouts/
    marketing.vue              # public pages (dark Framer)
    app.vue                    # workspace shell (3-pane)
    reader.vue                 # full-page Mintlify light
    default.vue
  pages/
    index.vue                  # landing
    waitlist.vue
    pricing.vue
    auth/login.vue
    app/
      index.vue                # Project Base picker
      [base]/
        index.vue              # Base home (stats + recents)
        wiki/index.vue
        wiki/[slug].vue        # Reader / Tiptap editor / TOC / right rail
        graph.vue              # Full graph explorer (Vue Flow)
        canvas/index.vue
        canvas/[id].vue        # Infinite canvas + AI organise
        sources/[id].vue       # Source detail + ingestion timeline
        search.vue             # Chat history
        settings.vue
  components/
    ui/                        # Local primitives: Button, Card, Badge, Input,
                               # Kbd, Dialog, Popover, Tabs, Toast, Tooltip,
                               # DropdownMenu, Sheet, ScrollArea, Separator, Avatar
    shell/                     # AppShell, Sidebar*, RightRail, StatusRail
    command/                   # ⌘K palette + result rows + scope chip
    wiki/                      # Tiptap editor + WikiLinkExtension + reader +
                               # citation chip + freshness badge + link popover + TOC
    graph/                     # Filters + Legend + custom nodes/edges
    canvas/                    # ItemCard, Toolbar, StickyNote
    panels/                    # Backlinks, Related, Evidence, LocalGraph (idle drift)
    sources/                   # DropZone, JobTimeline, Row
    marketing/                 # Hero, FeatureGrid, PricingTable, WaitlistForm
  composables/                 # use* — feature-scoped state + queries
  stores/                      # Pinia: projectBase
  lib/                         # utils, api client, motion presets
  plugins/                     # vue-query, motion
server/api/v1/[...].ts         # FastAPI proxy (auth + tenant injection)
server/api/waitlist.post.ts    # Waitlist capture stub
types/api.ts                   # Mirrors api/src/kmg_api/schemas/*.py
```

## Keyboard

| Shortcut | Action |
| --- | --- |
| `⌘K` / `Ctrl K` | Command palette (Find · Ask · Jump) |
| `g h` | Home |
| `g w` | Wiki |
| `g g` | Graph |
| `g c` | Canvas |
| `g s` | Search & chat |
| `e` | Toggle wiki edit mode |
| `Esc` | Close overlays |

## Skins

Two co-existing token sets at `app/assets/css/tokens-framer.css` and
`tokens-mintlify.css`, both mirrored from `design/design-systems/<skin>/tokens.css`.
The workspace shell defaults to `data-skin="framer"`; the WikiReader wraps its
content in `<div data-skin="mintlify">` to flip tokens locally.

## Tests

```bash
pnpm test         # vitest (9 files, 23 tests — all passing)
pnpm test:e2e     # Playwright (3 marketing tests pass without backend)
pnpm typecheck    # vue-tsc — clean
```

### E2E with the live backend

The auth-required tests in `tests/e2e/app.spec.ts` (`Authenticated app flow`)
hit the real FastAPI service.

```bash
# terminal 1
docker compose up postgres redis qdrant minio
uvicorn kmg_api.main:app --port 8000

# terminal 2
KMG_TEST_TENANT_ID=<a uuid known to the DB> pnpm test:e2e
```

The dev bypass at `api/src/kmg_api/dependencies.py:60` accepts any tenant UUID
via `X-Tenant-Id` while `KMG_ENV != production`.

## Backend endpoints added for the frontend

These were added to the FastAPI service as part of this work:

| Route | Purpose |
| --- | --- |
| `GET  /v1/jobs/{job_id}` | Single-job lookup for the ingestion timeline poller |
| `GET  /v1/chunks/{chunk_id}` | Drill-down from a citation to the grounding chunk |
| `GET  /v1/wiki/pages/{id}/evidence` | EvidencePanel rows |
| `GET  /v1/wiki/pages?q=` | `[[autocomplete]]` for the Tiptap WikiLinkExtension |
| `GET  /v1/graph/edges?limit=&min_confidence=&predicate=` | Filterable graph edges |

## Build

```bash
pnpm build      # nuxt build → .output/
node .output/server/index.mjs
```
