
-- $Id: database.sql,v 1.7 2006/06/01 20:15:04 lightdruid Exp $

-- create database test;
-- create user postnuke identified by 'postnuke';
-- grant all on test.* to 'postnuke'@'%' identified by 'postnuke';

drop table sessions;
drop table groups;
drop table rooms;
drop table users;
 
create table sessions (
    id mediumint not null auto_increment,
    sesid char(255),
    created timestamp not null,
    userid mediumint not null,
    primary key (id) 
);

create table groups (
    id mediumint not null auto_increment,
    name char(255),
    mlevel int,
    primary key (id),
    unique name(name)
);

create table rooms (
    id mediumint not null auto_increment,
    name char(255),

    creatorid mediumint,
    operatorid mediumint,

    allowedUsers mediumint,
    languageid mediumint default 0,
    temporary mediumint default 1,
    passwordProtected mediumint default 0,

    moderationAllowed mediumint default 0,
    roomManagementLevel mediumint default 0,
    userManagementlevel mediumint default 0,

    numberOfUsers mediumint,
    numberOfSpectators mediumint,
 
    primary key (id),
    unique name(name)
);
   
create table users (
    id mediumint not null auto_increment,
    name char(255),
    password char(255),
    role int,
    gid mediumint,
    languageid mediumint default 0,
    isblocked mediumint default 0,
    primary key (id),
    unique name(name)
);

insert into groups (name, mlevel) values ('group 0', 0);
insert into groups (name, mlevel) values ('group 1', 1);
insert into groups (name, mlevel) values ('group 2', 2);

insert into rooms (
    name,

    creatorid,
    operatorid,

    allowedUsers,
    languageid,
    temporary,
    passwordProtected,

    moderationAllowed,
    roomManagementLevel,
    userManagementlevel,

    numberOfUsers,
    numberOfSpectators
    ) values (
        'room #1',

        0,
        0,

        0,
        0,
        0,
        0,

        0,
        0,
        0,

        0,
        0
    );
 
insert into rooms (
    name,

    creatorid,
    operatorid,

    allowedUsers,
    languageid,
    temporary,
    passwordProtected,

    moderationAllowed,
    roomManagementLevel,
    userManagementlevel,

    numberOfUsers,
    numberOfSpectators
    ) values (
        'room #2',

        0,
        0,

        0,
        0,
        0,
        0,

        0,
        0,
        0,

        0,
        0
    );
 
  
insert into users (name, password, role, gid, languageid, isblocked) values ('as', 'as', 0, 0, 0, 0);
insert into users (name, password, role, gid, languageid, isblocked) values ('ab', 'ab', 1, 1, 1, 0);
insert into users (name, password, role, gid, languageid, isblocked) values ('zz', 'zz', 1, 2, 1, 0);
insert into users (name, password, role, gid, languageid, isblocked) values ('test_0', 'pass_0', 0, 2, 1, 0);

--
