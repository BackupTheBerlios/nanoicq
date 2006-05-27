
-- $Id: database.sql,v 1.4 2006/05/27 00:03:23 lightdruid Exp $

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
    mlevel int,
    primary key (id),
    unique name(name)
);
  
create table users (
    id mediumint not null auto_increment,
    name char(100),
    password char(100),
    role int,
    primary key (id),
    unique name(name)
);

insert into groups (name, mlevel) values ('group 0', 0);
insert into groups (name, mlevel) values ('group 1', 1);
insert into groups (name, mlevel) values ('group 2', 2);
 
insert into users (name, password, role) values ('as', 'as', 0);
insert into users (name, password, role) values ('ab', 'ab', 1);
insert into users (name, password, role) values ('zz', 'zz', 1);
insert into users (name, password, role) values ('test_0', 'pass_0', 0);

--
