create table Projects (
    Id integer primary key autoincrement,
    Name text not null,
    Shortcut text not null,
    Hours integer
)

create table Hours (
    Id integer primary key autoincrement,
    Amount integer not null,
    FOREIGN KEY(Id) REFERENCES Projects(Id)
)

create table Days (
    Id integer primary key autoincrement,
    Work_day date not null
)