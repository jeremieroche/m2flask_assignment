drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  delay integer not null,
  time text not null,
  client_ip text not null
);
