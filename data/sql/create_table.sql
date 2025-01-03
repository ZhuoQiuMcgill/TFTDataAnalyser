CREATE TABLE IF NOT EXISTS match_cache (
    match_id TEXT PRIMARY KEY,
    cache_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS player_info (
    gameName TEXT NOT NULL,
    tagLine TEXT NOT NULL,
    puuid TEXT NOT NULL,
    PRIMARY KEY (gameName, tagLine)
);

SELECT * FROM match_cache;