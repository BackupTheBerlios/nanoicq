
SNAC_GENERIC    = 0x0001    #  Generic service controls           
SNAC_LOCATION   = 0x0002    #  Location services          
SNAC_BUDDY_LIST = 0x0003    #  Buddy List management service          
SNAC_ICBM       = 0x0004    #  ICBM (messages) service            
SNAC_ADVERT     = 0x0005    #  Advertisements service         
SNAC_INVITE     = 0x0006    #  Invitation service         
SNAC_ADMIN      = 0x0007    #  Administrative service         
SNAC_POPUP      = 0x0008    #  Popup notices service          
SNAC_PRIV       = 0x0009    #  Privacy management service         
SNAC_LOOKUP     = 0x000a    #  User lookup service (not used any more)            
SNAC_USAGE      = 0x000b    #  Usage stats service            
SNAC_TRANSL     = 0x000c    #  Translation service            
SNAC_NAVIG      = 0x000d    #  Chat navigation service            
SNAC_CHAT       = 0x000e    #  Chat service           
SNAC_SEARCH     = 0x000f    #  Directory user search          
SNAC_SSBI       = 0x0010    #  Server-stored buddy icons (SSBI) service           
SNAC_SSI        = 0x0013    #  Server Side Information (SSI) service          
SNAC_EXT        = 0x0015    #  ICQ specific extensions service            
SNAC_AUTH       = 0x0017    #  Authorization/registration service         
SNAC_BROADCAST  = 0x0085    #  Broadcast service - IServerd extension

supported = {
    SNAC_GENERIC: 3,
    SNAC_LOCATION: 1, 
    SNAC_BUDDY_LIST: 1,
    SNAC_ICBM: 1,
    SNAC_INVITE: 1,
    SNAC_POPUP: 1,
    SNAC_PRIV: 1,
    SNAC_LOOKUP: 1,
    SNAC_USAGE: 1,
    SNAC_TRANSL: 1,
    SNAC_SSI: 3
}

# ---
