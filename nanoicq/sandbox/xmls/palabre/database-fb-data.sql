
-- $Id: database-fb-data.sql,v 1.2 2006/07/12 14:59:56 lightdruid Exp $

delete from users;
delete from rooms;
delete from sessions;
delete from groups;

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

    pvtPassword,
    publicPassword,

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

        '',
        '',

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

    pvtPassword,
    publicPassword,

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

        '',
        '',

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
