drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  delay integer not null,
  time text not null,
  client_ip text not null,
  user_agent text not null
);
drop table if exists download_summary;
create table download_summary (
  id integer primary key autoincrement,
  file_name text not null,
  count integer not null
);
