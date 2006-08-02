
-- $Id: trigger-fb.sql,v 1.4 2006/08/02 15:26:47 lightdruid Exp $

drop trigger sessions_tr;
drop trigger groups_tr;
drop trigger rooms_tr;
drop trigger users_tr;
drop trigger connect_history_tr;
 
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
        new.id = gen_id(gen_groups_id, 1);
end
!!

create or alter trigger rooms_tr for rooms
before insert
as
begin
    if (new.id is null) then
        new.id = gen_id(gen_rooms_id, 1);
end
!!
 
create or alter trigger users_tr for users
active before insert position 0
as
begin
    if (new.id is null) then
        new.id = gen_id(gen_users_id, 1);
end
!!


create or alter trigger connect_history_tr for connect_history
active before insert position 0
as
begin
    if (new.id is null) then
        new.id = gen_id(gen_connect_history_id, 1);
    if (new.last_connected is null) then
        new.last_connected = CURRENT_TIMESTAMP;
end
!!

SET TERM ; !! 

