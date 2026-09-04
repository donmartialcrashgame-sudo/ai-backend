# Curated knowledge for Game API AI.
# This is retrieval knowledge, not model-weight fine-tuning.

KNOWLEDGE = [
    {
        "title": "What is Game API",
        "keywords": "game api gaming api platform crash game real time infrastructure",
        "content": "Game API is the gaming infrastructure platform at https://game-api.online. It is designed for real-time gaming experiences, secure authentication, live WebSocket data, developer API features, and modular game services. The public homepage is an informational/live-monitor page and is not a betting interface."
    },
    {
        "title": "Live crash game",
        "keywords": "crash game live crash multiplier round websocket game state",
        "content": "The public live crash monitor displays round events received from the live WebSocket server. The page does not generate or invent the multiplier or round result. The WebSocket/game server is the authoritative source. The public homepage monitor is view-only and has no betting controls, stake inputs, or cash-out actions."
    },
    {
        "title": "WebSocket game events",
        "keywords": "websocket events connected game state round created betting open betting closed round started multiplier update round crashed",
        "content": "The frontend connects to the game backend WebSocket. Known event types in the current backend frontend include CONNECTED, GAME_STATE, ROUND_CREATED, BETTING_OPEN, BETTING_CLOSED, ROUND_STARTED, MULTIPLIER_UPDATE, and ROUND_CRASHED. The HTTP game-state endpoint used by the frontend is /api/game. The public backend host currently used by the frontend is don-martial-crash-game-backend.onrender.com."
    },
    {
        "title": "Authentication",
        "keywords": "login signup authentication email password google github passkey email otp whatsapp otp totp recovery codes",
        "content": "The Game API platform describes multiple authentication methods: Email + Password, Google, GitHub, Passkey, Email OTP, and WhatsApp OTP. Additional account protection includes TOTP/authenticator verification, recovery codes, and email verification. Sensitive authentication work is intended to remain on the backend."
    },
    {
        "title": "Player dashboard",
        "keywords": "dashboard account security settings api features developer tools",
        "content": "The platform includes a secure authenticated player/developer dashboard for account management, security settings, API features, and future developer tools."
    },
    {
        "title": "API keys",
        "keywords": "api key api-key generate key manager x-api-key bearer authorization developer key",
        "content": "The current backend has API-key management routes: GET /api/v1/api-key/plans, GET /api/v1/api-key/me, and POST /api/v1/api-key or /api/v1/api-key/generate. Key-protected requests can use the x-api-key header or Authorization: Bearer <key>. Generated keys use the mt_live_ prefix. Plaintext keys are not stored; the backend stores a SHA-256 hash. Key records have an owner userId, plan, status, createdAt, lastUsedAt, and requestCount. API keys must not be exposed in frontend code."
    },
    {
        "title": "API key security",
        "keywords": "api key security secret frontend backend hash invalid key admin key",
        "content": "API keys are sensitive credentials. Do not put a secret API key in browser/frontend code. The backend hashes generated keys with SHA-256 instead of storing plaintext. The API-key creation route requires a valid admin key. Invalid keys return an INVALID_API_KEY response from the /api/v1/api-key/me route."
    },
    {
        "title": "API plans",
        "keywords": "starter premium enterprise ultimate plans rate limit upcoming big odd",
        "content": "Current API plans in the backend are Starter, Premium, Enterprise, and Ultimate. Starter: current Big Odd and history, no upcoming Big Odd, 60 requests/minute. Premium: current Big Odd and history, up to 3 upcoming Big Odds, 300 requests/minute. Enterprise: current Big Odd and history, up to 5 upcoming Big Odds, 1000 requests/minute. Ultimate: current Big Odd and history, up to 10 upcoming Big Odds, 3000 requests/minute. These values come from the current backend plan manager and can change in future releases."
    },
    {
        "title": "Big Odd API",
        "keywords": "big odd big-odd current next upcoming today history endpoint",
        "content": "The Big Odd API is a publication layer around the existing WebSocket crash-game server. Current documented REST endpoints are /api/v1/big-odd/current, /api/v1/big-odd/next, /api/v1/big-odd/upcoming, /api/v1/big-odd/today, and /api/v1/big-odd/history. There is intentionally no tomorrow endpoint in the documented version."
    },
    {
        "title": "Big Odd definition",
        "keywords": "big odd 10x 10.00x minimum multiplier",
        "content": "The current Big Odd rule treats a crash multiplier of 10.00x or higher as a BIG ODD. The threshold is configurable on the backend with BIG_ODD_MINIMUM. The WebSocket/game server remains the authority that generates the game result; the Big Odd REST layer does not independently invent a result."
    },
    {
        "title": "Big Odd status",
        "keywords": "big odd status running played null",
        "content": "A Big Odd record can have status running when its associated game is currently running, played when the associated game has finished, or null when no final status has been assigned yet."
    },
    {
        "title": "Big Odd API authentication",
        "keywords": "big odd api authentication x-api-key bearer token api key",
        "content": "The documented Big Odd API accepts either x-api-key or Authorization: Bearer <secret> for API-key authentication. The secret should be kept server-side and never embedded in a frontend application."
    },
    {
        "title": "How the live platform works",
        "keywords": "connect receive display expand architecture round events server source truth",
        "content": "The public platform flow is: Connect to the configured WebSocket, receive JSON game events, display round state/multiplier updates, and expand the platform with additional modules without exposing private credentials. Server data remains the source of truth."
    },
    {
        "title": "Future platform sections",
        "keywords": "football shadow future game sections developer documentation",
        "content": "The public Game API site describes future expansion areas including football experiences, a Shadow-style game presentation layer, developer documentation, and additional real-time services. Treat these as planned/future features unless a current page explicitly says they are live."
    },
    {
        "title": "Support",
        "keywords": "support live support chat help assistance",
        "content": "The public platform includes integrated live support chat so users can get assistance while exploring the platform."
    },
]


def search_knowledge(query: str, limit: int = 4) -> str:
    """Return the most relevant curated facts for a user question."""
    import re

    q = query.lower()
    terms = set(re.findall(r"[a-z0-9]{2,}", q))
    scored = []
    for item in KNOWLEDGE:
        haystack = (item["title"] + " " + item["keywords"] + " " + item["content"]).lower()
        score = sum(1 for term in terms if term in haystack)
        if q.strip() and q.strip() in haystack:
            score += 5
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [item for score, item in scored if score > 0][:limit]
    if not selected:
        selected = [item for _, item in scored[:2]]

    return "\n\n".join(
        f"[{item['title']}]\n{item['content']}" for item in selected
    )
