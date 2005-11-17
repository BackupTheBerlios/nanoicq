
AIM_VOICE =    "094613414C7F11D18222444553540000"  
# Client supports voice chat. Currently used only by AIM service and AIM clients.     

AIM_DIRECT =    "094613424C7F11D18222444553540000"  
# Client supports direct play service. This capability currently used by AIM service and AIM clients.     
  
AIM_SENDFILE =      "094613434C7F11D18222444553540000"  
# Client supports file transfer (can send files). Currently used only by AIM service and AIM clients.     
  
ICQ =      "094613444C7F11D18222444553540000"  
# Something called "route finder". Currently used only by ICQ2K clients.  
  
AIM_IMAGE =      "094613454C7F11D18222444553540000"  
# Client supports DirectIM/IMImage. This capability currently used by AIM service and AIM clients.    
  
AIM_AVATAR =      "094613464C7F11D18222444553540000"  
# Client supports avatar service. This capability currently used by AIM service and AIM clients.  
  
AIM_STOCKS =      "094613474C7F11D18222444553540000"  
# Client supports stocks (addins). This capability currently used by AIM service and AIM clients.    
  
AIM_GETFILE =      "094613484C7F11D18222444553540000"  
# Client supports filetransfers (can receive files). This capability currently used by AIM service and AIM clients.   

RELAY =    "094613494C7F11D18222444553540000"  
# Client supports channel 2 extended, TLV(0x2711) based messages. Currently used only by ICQ clients. ICQ clients and clones use this GUID as message format sign. Trillian client use another GUID in channel 2 messages to implement its own message format (trillian doesn't use TLV(x2711) in SecureIM channel 2 messages!).  
  
AIM_GAMES =      "0946134A4C7F11D18222444553540000"  
# Client supports games. This capability currently used by AIM service and AIM clients.   
  
AIM_GAMES2 =      "0946134A4C7F11D12282444553540000"  
# Indeed, there are two of games caps. The previous appears to be correct, but in some versions of winaim, this one is set. Either they forgot to fix endianness, or they made a typo. It really doesn't matter which because the meaning of them is the same.    
  
AIM_BUDDY =      "0946134B4C7F11D18222444553540000"  
# Client supports buddy lists transfer. This capability currently used by AIM service and AIM clients.    
  
AIM_ICQGATE =      "0946134D4C7F11D18222444553540000"  
# Setting this lets AIM users receive messages from ICQ users, and ICQ users receive messages from AIM users. It also lets ICQ users show up in buddy lists for AIM users, and AIM users show up in buddy lists for ICQ users. And ICQ privacy/invisibility acts like AIM privacy, in that if you add a user to your deny list, you will not be able to see them as online (previous you could still see them, but they couldn't see you.     
  
UTF8 =      "0946134E4C7F11D18222444553540000"  
# Client supports UTF8 messages. This capability currently used by AIM service and AIM clients.  
  
RTF =      "97B12751243C4334AD22D6ABF73F1492"  
# Client supports RTF messages. This capability currently used by ICQ service and ICQ clients.    
  
ICQ20012 =      "A0E93F374C7F11D18222444553540000"  
# Unknown capability This capability currently used only by ICQ2001/ICQ2002 clients.  
  
ICQ2002 =      "10CF40D14C7F11D18222444553540000"  
# Unknown capability This capability currently used only by ICQ2002 client.   
  
ICQ2001 =     "2E7A6475FADF4DC8886FEA3595FDB6DF"  
# Unknown capability This capability currently used only by ICQ2001 client.   
  
WEB =      "563FC8090B6f41BD9F79422609DFA2F3"  
# Unknown capability This capability currently used only by ICQLite/ICQ2Go clients.   
  
AIM_CHAT =      "748F2420628711D18222444553540000"  
# Client supports chat service. This capability currently used by AIM service and AIM clients.    
  
TRILL_CRYPT =      "F2E7C7F4FEAD4DFBB23536798BDF0000"  
# Client supports trillian SecureIM channel2 messages. This capability currently used by Trillian clients.   

TRILL_UNK =   "97B12751243C4334AD22D6ABF73F14xx"  
# This is not cpability at all. This GUID used by SIM/Kopete clients to detect same clients version.

# 
