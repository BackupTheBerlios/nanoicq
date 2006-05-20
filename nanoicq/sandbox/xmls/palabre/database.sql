
-- $Id: database.sql,v 1.1 2006/05/20 23:19:43 lightdruid Exp $

create table user (
    name char(100),
    password char(100),
    role int
);

insert into user values ('as', 'as', 0);
insert into user values ('ab', 'ab', 1);
insert into user values ('zz', 'zz', 1);
 
