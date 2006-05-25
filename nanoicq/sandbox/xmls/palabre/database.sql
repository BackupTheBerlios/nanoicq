
-- $Id: database.sql,v 1.2 2006/05/25 13:29:19 lightdruid Exp $

-- create database test;
-- create user postnuke identified by 'postnuke';
-- grant all on test.* to 'postnuke'@'%' identified by 'postnuke';

create table user (
    name char(100),
    password char(100),
    role int
);

insert into user values ('as', 'as', 0);
insert into user values ('ab', 'ab', 1);
insert into user values ('zz', 'zz', 1);
 
