# PSK.HR Platform Integration Prompt Addendum

Add the following requirements to the game asset delivery system prompt.

## PSK.HR integration is mandatory

The resulting asset delivery, test-site, loader, metrics, and validation system must be integratable with the PSK.HR platform. Treat PSK.HR as the target platform integration, while keeping the implementation adaptable to local development, staging, and production environments.

Do not hard-code credentials, private endpoints, tokens, or environment-specific URLs. All PSK.HR configuration must be supplied through validated runtime configuration or environment variables.

## PSK.HR game registration

Implement a PSK.HR-compatible game registration contract containing at least:

```json
{
  "gameId": "empire-of-gold",
  "gameVersion": "build-hash",
  "entryUrl": "https://test.example/game/index.html",
  "manifestUrl": "https://test.example/game/manifest.json",
  "engine": "pixijs",
  "locale": "en",
  "assetBaseUrl": "https://test.example/game/assets/",
  "environment": "test"
}
```

The system must support separate `local`, `test`, `staging`, and `production` configurations without changing game code.

## PSK.HR test-site launcher

Create a PSK.HR-compatible launcher that can load a registered game using a game identifier and version:

```text
/test-site/game.html?game=empire-of-gold&version=build-hash&locale=en
```

The launcher must:

- Resolve the game registration through a configurable PSK.HR platform endpoint.
- Validate the returned manifest before loading the game.
- Resolve all assets relative to the registered `assetBaseUrl`.
- Support local static-server URLs for development.
- Support staging and production asset URLs.
- Display Tier 1 loading progress.
- Emit first-frame and first-playable metrics.
- Report missing assets and failed requests clearly.
- Keep gameplay input disabled until Tier 1 dependencies are ready.
- Work when embedded in an iframe if PSK.HR uses iframe integration.
- Work when opened directly for local testing.

Do not assume that the launcher and game are hosted on the same origin.

## PSK.HR runtime bridge

Implement a small platform bridge with a stable internal API:

```javascript
const platform = createPSKHRBridge({
  gameId,
  gameVersion,
  environment,
  locale
});

platform.ready();
platform.reportMetric(name, value, details);
platform.reportError(error);
platform.requestConfig();
platform.getSession();
platform.onVisibilityChange(callback);
platform.onResize(callback);
platform.destroy();
```

The bridge must:

- Detect whether the game runs standalone, in an iframe, or inside a PSK.HR host shell.
- Use an adapter boundary so PSK.HR messaging can be implemented with `postMessage`, a host SDK, or HTTP APIs without changing the asset loader.
- Validate all messages and origins.
- Never expose secrets to the browser.
- Fail gracefully when no PSK.HR host is present.
- Preserve the standalone local-development mode.

## PSK.HR lifecycle events

Support these lifecycle events where the PSK.HR platform provides them:

- `game_init_start`
- `manifest_loaded`
- `tier0_complete`
- `tier1_start`
- `tier1_complete`
- `first_canvas`
- `first_visual_frame`
- `first_playable_frame`
- `tier2_start`
- `tier2_complete`
- `feature_load_start`
- `feature_load_complete`
- `game_ready`
- `game_paused`
- `game_resumed`
- `game_hidden`
- `game_visible`
- `game_error`
- `game_exit`

The game must not report `game_ready` until the first playable frame is available. It must not wait for Tier 2 or Tier 3 assets before reporting readiness.

## PSK.HR configuration

Support configuration supplied by the PSK.HR host, including:

- Game ID
- Game version
- Environment
- Locale
- Currency
- User/session identifier, without logging sensitive values
- Asset base URL
- Manifest URL
- Feature flags
- Device class
- Quality level
- Mobile/desktop resolution
- Audio enabled state
- Reduced-motion preference
- Authentication state, through opaque session references only

Validate configuration against a schema. Apply safe defaults for missing optional values. Stop with a clear error for missing required values.

## PSK.HR asset delivery contract

The asset system must support PSK.HR asset URLs with:

- Immutable build-hashed paths
- Versioned manifests
- Relative and absolute asset URLs
- Cache-busting through build hashes, not random query strings
- Range requests where useful
- Brotli-compressed text assets
- Long-lived immutable caching for hashed assets
- Short-lived caching for manifests
- CDN or object-storage URLs supplied by PSK.HR configuration

The game must remain functional on a simple local static server and must not require PSK.HR-specific server rewrites during development.

## PSK.HR security requirements

- Never put API secrets, signing keys, or private credentials in client-side files.
- Validate `postMessage` sender origins.
- Use an allowlist for approved PSK.HR host origins.
- Validate manifest schemas before loading.
- Reject manifests with path traversal, unsupported protocols, or unexpected origins.
- Do not inject untrusted configuration into HTML.
- Do not log session tokens, authentication headers, or personally identifiable information.
- Report only anonymized performance data unless PSK.HR explicitly requires otherwise.
- Enforce HTTPS outside local development.

## PSK.HR observability

Send performance metrics through a configurable PSK.HR telemetry adapter. Include:

- Game ID and version
- Engine type
- Environment
- Locale
- Device class
- Browser family
- Connection type when available
- Cold or warm cache state
- Tier 1 size
- Tier 1 duration
- First canvas time
- First visual frame time
- First playable frame time
- Tier 2 duration
- Total asset bytes
- Cache-hit ratio
- Failed asset count
- Missing asset names
- Loader errors

Do not block gameplay on telemetry. Queue metrics locally and send them asynchronously. If telemetry fails, the game must continue normally.

## PSK.HR failure behavior

If PSK.HR configuration, manifest lookup, telemetry, or host messaging fails:

- Show a user-safe loading/error state.
- Provide a diagnostic error code.
- Preserve the original error for developer diagnostics.
- Do not expose secrets or internal infrastructure details.
- Attempt standalone fallback only when explicitly enabled by configuration.
- Never silently load a different game or version.

If an optional Tier 2 or Tier 3 asset fails, gameplay must continue and the failure must be reported. If a Tier 1 asset fails, the game must not claim to be playable.

## PSK.HR acceptance tests

Add automated tests that verify:

1. A game can launch locally without PSK.HR.
2. A game can launch using a PSK.HR-style registration response.
3. The launcher resolves the configured manifest and asset base URL.
4. Cross-origin iframe messaging accepts only approved origins.
5. Invalid manifests fail before asset loading.
6. Tier 1 reaches playable state before Tier 2 completes.
7. Background audio does not block `game_ready`.
8. Missing Tier 1 assets prevent `game_ready`.
9. Missing Tier 2 assets do not break gameplay.
10. Metrics are emitted without delaying startup.
11. Session and configuration secrets are never logged.
12. Cold-cache and warm-cache metrics are generated separately.
13. Local, test, staging, and production configuration values remain isolated.
14. A PSK.HR iframe resize or visibility event does not break the game loop.

## PSK.HR deliverables

The implementation must produce:

- A PSK.HR integration adapter
- A standalone fallback adapter
- A registration/configuration schema
- A manifest schema
- A PSK.HR test-site launcher
- A secure runtime bridge
- Lifecycle and telemetry event definitions
- Local, test, staging, and production configuration examples using placeholder values
- End-to-end integration tests
- A Markdown report containing startup performance and PSK.HR integration status

The final system must allow any supported browser game to be uploaded, registered, validated, launched on the PSK.HR test site, measured under cold-cache conditions, and rejected before publication if it has missing assets or violates the Tier 1 performance budget.
