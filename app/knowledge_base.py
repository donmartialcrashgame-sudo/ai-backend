import re

# Curated brain/knowledge layer for Game API AI.
# This teaches the assistant through retrieval; it does not change model weights.

KNOWLEDGE = [
    {
        "title": "Game API overview",
        "keywords": "game api gaming api game-api.online platform website crash gaming infrastructure developer",
        "content": "Game API is the gaming infrastructure platform at https://game-api.online. It is built around real-time gaming infrastructure, live WebSocket data, secure authentication, developer API features, and modular game services. The public site also provides information and a live crash monitor."
    },
    {
        "title": "What the public crash monitor does",
        "keywords": "crash game live monitor multiplier round betting stake cashout wager view only",
        "content": "The public crash monitor is view-only. It displays live round activity and multiplier updates received from the game server. It does not provide betting controls, stake inputs, wagers, or cash-out controls. The game/WebSocket server is the authority for round results."
    },
    {
        "title": "WebSocket architecture",
        "keywords": "websocket live realtime events connected game state round created betting open betting closed round started multiplier update round crashed",
        "content": "The frontend receives real-time crash-game events from the backend WebSocket. Known event types include CONNECTED, GAME_STATE, ROUND_CREATED, BETTING_OPEN, BETTING_CLOSED, ROUND_STARTED, MULTIPLIER_UPDATE, and ROUND_CRASHED. The frontend also uses /api/game for HTTP game state. The current backend host used by the frontend is don-martial-crash-game-backend.onrender.com."
    },
    {
        "title": "Authentication methods",
        "keywords": "authentication login signup account email password google github passkey email otp whatsapp otp totp authenticator recovery email verification",
        "content": "The platform describes Email + Password, Google, GitHub, Passkey, Email OTP, and WhatsApp OTP authentication. Additional account protection includes TOTP/authenticator verification, recovery codes, and email verification."
    },
    {
        "title": "Dashboard",
        "keywords": "dashboard player developer account settings security api tools",
        "content": "Game API includes an authenticated player/developer dashboard for account management, security settings, API features, and developer tools."
    },
    {
        "title": "API keys",
        "keywords": "api key keys generate developer key x-api-key authorization bearer mt_live plans me",
        "content": "The backend has API-key management routes including GET /api/v1/api-key/plans, GET /api/v1/api-key/me, and POST key-generation routes. API-key protected requests can use x-api-key or Authorization: Bearer <key>. Generated live keys use the mt_live_ prefix. Plaintext keys are not stored; SHA-256 hashes are stored instead. Never expose a secret API key in browser/frontend code."
    },
    {
        "title": "API key security",
        "keywords": "api key security secret credential frontend backend hash admin invalid key",
        "content": "API keys are secret credentials and should remain on the server. The backend hashes generated keys with SHA-256 rather than storing plaintext. Key creation requires an admin key. Invalid credentials are rejected."
    },
    {
        "title": "API plans and limits",
        "keywords": "starter premium enterprise ultimate plan plans rate limit requests per minute upcoming big odd",
        "content": "Current backend plans are Starter, Premium, Enterprise, and Ultimate. Starter provides current Big Odd and history, no upcoming Big Odd, and 60 requests/minute. Premium provides current and history, up to 3 upcoming Big Odds, and 300 requests/minute. Enterprise provides current and history, up to 5 upcoming Big Odds, and 1000 requests/minute. Ultimate provides current and history, up to 10 upcoming Big Odds, and 3000 requests/minute. These backend values may change in future releases."
    },
    {
        "title": "Big Odd API",
        "keywords": "big odd big-odd current next upcoming today history rest api endpoints",
        "content": "Big Odd is a REST publication layer around the existing WebSocket crash-game server. Current documented endpoints are /api/v1/big-odd/current, /api/v1/big-odd/next, /api/v1/big-odd/upcoming, /api/v1/big-odd/today, and /api/v1/big-odd/history. The documented version does not include a tomorrow endpoint."
    },
    {
        "title": "Big Odd rule",
        "keywords": "big odd 10x 10.00x threshold minimum multiplier",
        "content": "The current Big Odd definition is a crash multiplier of 10.00x or higher. The backend threshold is configurable with BIG_ODD_MINIMUM. The WebSocket/game server remains the authority for the actual game result; the Big Odd REST layer does not independently invent results."
    },
    {
        "title": "Big Odd status",
        "keywords": "big odd status running played null game status",
        "content": "A Big Odd record can have status running while its associated game is running, played after the associated game finishes, or null when no final status has been assigned."
    },
    {
        "title": "Big Odd authentication",
        "keywords": "big odd authentication x-api-key bearer authorization api key secret",
        "content": "The documented Big Odd API accepts x-api-key or Authorization: Bearer <secret> for API-key authentication. Secret keys must stay server-side and must not be embedded in frontend code."
    },
    {
        "title": "Server is the source of truth",
        "keywords": "source truth server authoritative result multiplier generated websocket frontend",
        "content": "The game server/WebSocket is the authoritative source for game state, round events, and crash results. The frontend renders received events; it does not create or predict the official result."
    },
    {
        "title": "Platform features",
        "keywords": "features real time secure authentication developer api live support documentation",
        "content": "The platform focuses on real-time gaming infrastructure, WebSocket event delivery, modern authentication, developer API access, player/developer dashboards, live support, and documentation."
    },
    {
        "title": "Future sections",
        "keywords": "football shadow future planned expansion games",
        "content": "The site describes future expansion areas including football experiences, a Shadow-style game presentation layer, and additional real-time services. These should be described as planned/future unless a current page explicitly says they are live."
    },
    {
        "title": "Support",
        "keywords": "support help assistance live chat customer support",
        "content": "The platform includes live support chat for users who need assistance while using or exploring the platform."
    },
]

# Words that strongly indicate the user is asking about this product/platform.
GAME_API_TERMS = {
    "game-api", "game api", "gameapi", "crash game", "big odd", "big-odd",
    "websocket", "api key", "api keys", "endpoint", "endpoints", "game-api.online",
    "game api online", "dashboard", "multiplier", "round", "starter", "premium",
    "enterprise", "ultimate", "x-api-key", "bearer", "mt_live", "betting_open",
    "round_crashed", "multiplier_update"
}


def is_game_api_question(query: str) -> bool:
    """Decide whether a message needs the Game API brain."""
    q = query.lower().strip()
    if any(term in q for term in GAME_API_TERMS):
        return True

    # Natural-language product questions that may not use exact product terms.
    product_patterns = (
        r"\bhow (does|do) .* (work|works)\b",
        r"\bwhat (is|are) .* (api|platform|plan|dashboard)\b",
        r"\bhow .* (connect|authenticate|login|sign up|signup)\b",
        r"\bwhere .* (documentation|docs|dashboard|key)\b",
    )
    return any(re.search(pattern, q) for pattern in product_patterns)


def search_knowledge(query: str, limit: int = 4, fallback: bool = True) -> str:
    """Return a small, relevant set of curated facts."""
    q = query.lower()
    terms = set(re.findall(r"[a-z0-9_./-]{2,}", q))
    scored = []

    for item in KNOWLEDGE:
        title = item["title"].lower()
        keywords = item["keywords"].lower()
        content = item["content"].lower()
        score = 0
        for term in terms:
            if term in title:
                score += 5
            elif term in keywords:
                score += 3
            elif term in content:
                score += 1
        if q and q in content:
            score += 6
        scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    selected = [item for score, item in scored if score > 0][:limit]
    if not selected and fallback:
        selected = [item for _, item in scored[:2]]

    return "\n\n".join(
        f"[{item['title']}]\n{item['content']}" for item in selected
    )
