CREATE TABLE IF NOT EXISTS eventos (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(50) UNIQUE,
    country VARCHAR(5),
    city VARCHAR(100),
    type VARCHAR(50),
    subtype VARCHAR(50),
    street VARCHAR(200),
    speed INTEGER,
    confidence INTEGER,
    reliability INTEGER,
    reportRating INTEGER,
    roadType INTEGER,
    magvar INTEGER,
    x FLOAT,
    y FLOAT,
    reportBy VARCHAR(100),
    pubMillis BIGINT,
    reportMood INTEGER
);

CREATE TABLE IF NOT EXISTS comentarios (
    id SERIAL PRIMARY KEY,
    evento_uuid VARCHAR(50) REFERENCES eventos(uuid),
    reportMillis BIGINT,
    isThumbsUp BOOLEAN,
    text TEXT
);
