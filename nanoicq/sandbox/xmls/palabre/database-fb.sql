
-- $Id: database-fb.sql,v 1.2 2006/06/27 21:45:58 lightdruid Exp $

-- create database test;
-- create user postnuke identified by 'postnuke';
-- grant all on test.* to 'postnuke'@'%' identified by 'postnuke';

drop table sessions;
drop table groups;
drop table rooms;
drop table users;

drop generator gen_groups_id;
drop generator gen_sessions_id;
drop generator gen_rooms_id;
drop generator gen_users_id;
  
create table sessions (
    id int not null,
    sesid char(250),
    created timestamp not null,
    userid int not null,
    primary key (id) 
);

CREATE GENERATOR gen_sessions_id;
SET GENERATOR gen_sessions_id TO 0;

create table groups (
    id int not null,
    name char(250),
    mlevel int,
    primary key (id)
);

create unique index groups_ux1 on groups(name);

CREATE GENERATOR gen_groups_id;
SET GENERATOR gen_groups_id TO 0;
 
create table rooms (
    id int not null,
    name char(250),

    creatorid int,
    operatorid int,

    allowedUsers int,
    languageid int default 0,
    temporary int default 1,
    passwordProtected int default 0,

    moderationAllowed int default 0,
    roomManagementLevel int default 0,
    userManagementlevel int default 0,

    numberOfUsers int,
    numberOfSpectators int,
 
    primary key (id)
);

create unique index rooms_ux1 on rooms(name);
 
CREATE GENERATOR gen_rooms_id;
SET GENERATOR gen_rooms_id TO 0;
    
create table users (
    id int not null,
    name char(250),
    upassword char(250),
    urole int,
    gid int,
    languageid int default 0,
    isblocked int default 0,
    primary key (id)
);

create unique index users_ux1 on users(name);
 
CREATE GENERATOR gen_users_id;
SET GENERATOR gen_users_id TO 0;
 
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
 
  
insert into users (name, upassword, urole, gid, languageid, isblocked) values ('as', 'as', 0, 0, 0, 0);
insert into users (name, upassword, urole, gid, languageid, isblocked) values ('ab', 'ab', 1, 1, 1, 0);
insert into users (name, upassword, urole, gid, languageid, isblocked) values ('zz', 'zz', 1, 2, 1, 0);
insert into users (name, upassword, urole, gid, languageid, isblocked) values ('test_0', 'pass_0', 0, 2, 1, 0);

--
