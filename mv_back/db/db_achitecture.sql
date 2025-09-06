-- Теги
CREATE TABLE Tag (
    id   varchar(128) NOT NULL,
    [name] nvarchar(200) NOT NULL
);

-- База
CREATE TABLE Media (
    id             varchar(128) NOT NULL,
    [title]        nvarchar(500) NOT NULL,
    [path]         nvarchar(1000) NULL,
    auto_added     bit NOT NULL DEFAULT 1,
    primary_tag_id varchar(128) NULL,
    crD  datetime2 NULL,
    modD datetime2 NULL,
    delD datetime2 NULL
);

-- Підтипи
CREATE TABLE Movie (
    media_id varchar(128) NOT NULL
);

CREATE TABLE Series (
    media_id varchar(128) NOT NULL
);

-- Колекції фільмів
CREATE TABLE MovieItem (
    id            varchar(128) NOT NULL,
    collection_id varchar(128) NOT NULL,
    position      int NULL,
    [title]       nvarchar(500) NOT NULL,
    [path]        nvarchar(1000) NULL,
    note          nvarchar(500) NULL,
    media_id      varchar(128) NULL
);

-- Серіали
CREATE TABLE Season (
    id            varchar(128) NOT NULL,
    series_id     varchar(128) NOT NULL,
    season_number int NULL,
    [title]       nvarchar(500) NULL,
    [path]        nvarchar(1000) NULL
);

CREATE TABLE Episode (
    id             varchar(128) NOT NULL,
    season_id      varchar(128) NOT NULL,
    episode_number int NULL,
    [title]        nvarchar(500) NOT NULL,
    file_path      nvarchar(1000) NULL,
    duration_sec   int NULL
);

-- Набір/профіль пропусків
CREATE TABLE SkipSet (
    id         varchar(128) NOT NULL,
    episode_id varchar(128) NOT NULL,
    [name]     nvarchar(100) NULL,
    [source]   nvarchar(100) NULL,
    [priority] int NOT NULL DEFAULT 0,
    is_active  bit NOT NULL DEFAULT 1,
    created_at datetime2 NOT NULL DEFAULT sysutcdatetime()
);

-- Інтервали у межах профілю
CREATE TABLE SkipRange (
    id          varchar(128) NOT NULL,
    skip_set_id varchar(128) NOT NULL,
    start_time_ms int NOT NULL,
    end_time_ms   int NOT NULL,
    [label]       nvarchar(50) NULL
);

-- Зв’язок теги <-> медіа
CREATE TABLE Xref_Tag2Media (
    media_id varchar(128) NOT NULL,
    tag_id   varchar(128) NOT NULL
);
