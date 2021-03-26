create table projects (
    project_id integer primary key autoincrement,
    name text not null UNIQUE,
    shortcut text not null UNIQUE,
)

create table hours (
    hours_id integer primary key autoincrement,
    amount integer not null,
    work_date integer not null,
    FOREIGN KEY(project_id) REFERENCES Projects(project_id)
)