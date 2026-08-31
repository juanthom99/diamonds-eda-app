create table diamonds (
    id bigint generated always as identity primary key,
    carat float,
    cut text,
    color text,
    clarity text,
    depth float,
    "table" float,
    price integer,
    x float,
    y float,
    z float
);

alter table diamonds enable row level security;

create policy "Allow public read access"
on diamonds
for select
using (true);