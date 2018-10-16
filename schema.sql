drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title string not null,
  text string not null
  photo string
);

create table photos (
    id integer  primary key  autoincrement ,
    photo string notnull
);