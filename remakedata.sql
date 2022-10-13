drop table if exists laptops;
drop table if exists brands;
drop table if exists processor;
drop table if exists ram_type;
drop table if exists disk_type;
drop table if exists os;
drop table if exists weight;
drop table if exists processor_brand;

create table brands (
    id integer primary key unique,
    name varchar(20)
);

create table processor_brand(
    id integer primary key unique,
    brand varchar(20)
);

create table processor (
    id integer primary key unique,
    brand_id integer,
    model varchar(20),
    foreign key(brand_id) references processor_brand(id)
);

create table ram_type (
    id integer primary key unique,
    type varchar(20)
);

create table disk_type (
    id integer primary key unique,
    ssd int,
    hdd int
);

create table os (
    id integer primary key unique,
    name varchar(20)
);

create table weight (
    id integer primary key unique,
    type varchar(20)
);

create table laptops (
    id integer primary key unique,
    brand_id integer,
    model varchar(20),
    processor_id integer,
    processor_generation int,
    ram int,
    ram_type_id integer,
    disk_type_id integer,
    os_id integer,
    os_bit int,
    graphic_card_gb int,
    weight_id integer,
    display_size float,
    touchscreen int,
    price int,
    rating float,
    foreign key(brand_id) references brands(id),
    foreign key(processor_id) references processor(id),
    foreign key(ram_type_id) references ram_type(id),
    foreign key(disk_type_id) references disk_type(id),
    foreign key(os_id) references os(id),
    foreign key(weight_id) references weight(id)
);
