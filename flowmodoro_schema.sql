CREATE TABLE daily_log (
    "id" INTEGER,
    "project_id" INTEGER,
    "started_date" TEXT,
    "started_time" TEXT,
    "ended_date" TEXT,
    "ended_time" TEXT,
    "mins_worked" INTEGER,
    "accomplished" TEXT,
    PRIMARY KEY ("id"),
    FOREIGN KEY("project_id") REFERENCES "projects"("id")
);

CREATE TABLE projects (
    "id" INTEGER,
    "project" TEXT NOT NULL,
    "status" INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY ("id")
);

CREATE TABLE break_level (
    "bl" INTEGER NOT NULL DEFAULT 2
)

CREATE INDEX "started" ON "daily_log" ("started_date")