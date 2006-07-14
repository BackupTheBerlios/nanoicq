
-- $Id: database-fb.sql,v 1.9 2006/07/14 10:24:20 lightdruid Exp $

-- create database test;
-- create user postnuke identified by 'postnuke';
-- grant all on test.* to 'postnuke'@'%' identified by 'postnuke';

drop table sessions;
drop table groups;
drop table rooms;
drop table users;
drop table users_rooms;
drop table users_groups;

drop generator gen_groups_id;
drop generator gen_sessions_id;
drop generator gen_rooms_id;
drop generator gen_users_id;
  
create table sessions (
    id int not null,
    sesid char(250),
    created timestamp not null,
    userid int not null,
    ip char(16),
    primary key (id) 
);

CREATE GENERATOR gen_sessions_id;
SET GENERATOR gen_sessions_id TO 0;

create table groups (
    id int not null,
    name char(250),
    mlevel int default 0,
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

    pvtPassword char(250),
    publicPassword char(250),

    moderationAllowed int default 0,
    roomManagementLevel int default 0,
    userManagementlevel int default 0,

    numberOfUsers int,
    numberOfSpectators int,

    lastUpdateUserId int,
 
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
    roomManagementLevel int default -1,
    userManagementLevel int default -1,
    moderationLevel int default -1,
    lastIP char(16),
    primary key (id)
);

create unique index users_ux1 on users(name);
 
CREATE GENERATOR gen_users_id;
SET GENERATOR gen_users_id TO 0;

create table users_rooms (
    users_id int not null,
    rooms_id int not null
); 

create table users_groups (
    users_id int not null,
    groups_id int not null
);

--
