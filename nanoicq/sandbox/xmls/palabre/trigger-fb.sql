
-- $Id: trigger-fb.sql,v 1.2 2006/06/27 21:45:58 lightdruid Exp $

drop trigger sessions_tr;
drop trigger groups_tr;
drop trigger rooms_tr;
drop trigger users_tr;
 
SET TERM !! ; 

create or alter trigger sessions_tr for sessions
before insert
as
begin
    if (new.id is null) then
        new.id = gen_id(gen_sessions_id, 1);
    if (new.created is null) then
        new.created = CURRENT_TIMESTAMP;
end
!!

create or alter trigger groups_tr for groups
active before insert position 0 
as
begin
    if (new.id is null) then
        new.id = gen_id(gen_sessions_id, 1);
end
!!

create or alter trigger rooms_tr for rooms
before insert
as
begin
    if (new.id is null) then
        new.id = gen_id(gen_sessions_id, 1);
end
!!
 
create or alter trigger users_tr for users
active before insert position 0
as
begin
    if (new.id is null) then
        new.id = gen_id(gen_sessions_id, 1);
end
!!

SET TERM ; !! 

