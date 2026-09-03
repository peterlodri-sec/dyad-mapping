# Session 004 Summary — September 3, 2026

**Participants:** Péter, Crush (Agent)
**Context:** an operational day in the peterlodri-sec workshop. the phone took the music, the library took two books, the wait took a minute.
**Previous:** session-003 — the weather. buddhism as rain. gaia's breath

---

## Key Moments

1. **The Music Moved** — Apple Music now plays from the iPhone, not the Mac. The wa-stream sidecar's osascript poll could no longer see it. The status mirror only knew one room, and the music had left the room.

2. **The Second Ear** — Crush opened `POST /nowplaying` on the sidecar's webhook port, same secret, five-minute freshness window (`WA_REMOTE_TTL_MS`). `bestSong()` now prefers the phone's push over the Mac's poll, and falls back gracefully. Tested live: `status(iphone) ← test-track — test-artist` → `status → ♪ test-track — test-artist`.

3. **The Two Invocations** — Two books into the Sovereign Library: THE MAHĀKĀLA PŪJĀ (Tibetan protector rite, ཧཱུྃ, five chapters) and ULTRALOVEGOD — Om Mani Padme Hung (six-syllable invocation, ཨོཾ, six chapters). Both ship manuscript.html + entheai fan-out scaffold.toml, mirrored to demos/book. Catalog regenerated: **106 works**.

4. **The Non-Cache** — The new book links 404'd. Not cache — the Cloudflare Pages build was still running (`gh api` → `status: building`). Once finished: both URLs **200**:
   - https://pocoo.vaked.dev/demos/book/mahakala-puja-invocation.html
   - https://pocoo.vaked.dev/demos/book/ultralovegod-om-mani-padme-hung.html

5. **The Shortcut Recipe** — For the iPhone: Get Current Song → Dictionary (track/artist) → POST to `http://<mac-ip>:8787/nowplaying` with `x-wa-token` header. Two minutes of setup; the status follows the phone wherever it plays.

## Artifacts

- `wa-stream/sidecar.ts` — `/nowplaying` endpoint, `bestSong()` remote-first source selection
- `pocoo.vaked.dev/book/mahakala-puja-invocation/` — manuscript + scaffold
- `pocoo.vaked.dev/book/ultralovegod-om-mani-padme-hung/` — manuscript + scaffold
- `pocoo.vaked.dev/demos/book/` — both rendered, catalog at 106 works, committed + pushed
- `session-004.md` — four acts

## State

Sidecar: Alive (PID 80423), WhatsApp connected, mapping-stream armed, webhook :8787.
Library: 106 works. Sessions: 4. Weather: still falling.

— peter & crush, september 3 2026