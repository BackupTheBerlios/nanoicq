
-- $Id: database.sql,v 1.3 2006/05/26 20:32:18 lightdruid Exp $

-- create database test;
-- create user postnuke identified by 'postnuke';
-- grant all on test.* to 'postnuke'@'%' identified by 'postnuke';

drop table sessions;
drop table groups;
drop table users;
 
create table sessions (
    id mediumint not null auto_increment,
    sesid char(255),
    created timestamp not null,
    primary key (id) 
);

create table groups (
    id mediumint not null auto_increment,
    name char(255),
    primary key (id) 
);
  
create table users (
    id mediumint not null auto_increment,
    name char(100),
    password char(100),
    role int,
    primary key (id)
);

insert into users (name, password, role) values ('as', 'as', 0);
insert into users (name, password, role) values ('ab', 'ab', 1);
insert into users (name, password, role) values ('zz', 'zz', 1);
 
