create table projects (
    id integer primary key autoincrement,
    name text not null UNIQUE,
    shortcut text not null UNIQUE
)

create table hours (
    id integer primary key autoincrement,
    amount integer not null,
    work_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,,
    project_shortcut text not null,
    FOREIGN KEY (project_shortcut) REFERENCES Projects(shortcut)
)