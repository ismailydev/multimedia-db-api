-- Drop table if it exists
DROP TABLE IF EXISTS media_t;

-- Create media table
CREATE TABLE media_t (
    media_id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_name TEXT,
    media_obj BLOB,
    locations TEXT, -- Comma-separated or JSON string of locations
    tags TEXT,      -- Comma-separated or JSON string of tags
    date_created DATE,
    description TEXT
);

-- Sample insert into media_t table
INSERT INTO media_t (
    media_name, media_obj, locations, tags, date_created, description
) VALUES (
    'trip.mp4',
    NULL,
    '4kilo,bole,mexico',
    'sheger,ethiopia,addis ababa',
    '2021-08-31',
    'video of visiting places in addis ababa (4kilo, bole, and mexico)'
);

-- View all medias from media table
SELECT media_id, media_name, description, date_created FROM media_t;

-- Select statement to get media locations and tags
SELECT media_id, media_name, locations, tags, description FROM media_t;