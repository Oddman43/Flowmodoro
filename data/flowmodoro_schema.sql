CREATE TABLE daily_log (
    "id" INTEGER,
    "project_id" INTEGER,
    "started" TEXT,
    "ended" TEXT,
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
    "id" INTEGER,
    "break_level" INTEGER,
    PRIMARY KEY ("id")
);

CREATE INDEX "started" ON "daily_log" ("started_date");
INSERT INTO break_level (break_level) VALUES (2);