from typing import Dict, Tuple
import os
from fastapi_socketio import SocketManager

from modules.auth.services import decode_token

DEBUG = True if os.getenv("MODE") == "DEBUG" else False

async def JWT_VERIFY_SOCKET(jwt: str):
    try:
        if DEBUG:
            print("JWT: ", jwt)
            return True
        if not jwt:
            raise ValueError("JWT not found")
        payload = decode_token(jwt)
        if not payload:
            raise ValueError("JWT invalid")
        return True
    except ValueError as e:
        print(e)
        return False
    

def wrap_init_connect(sio: SocketManager):
    async def init_connect(sid: str, _, auth: Dict[str, str]):
        jwt = getattr(auth, "auth")

        try:
            if DEBUG:
                print("JWT: ", jwt)
                return True

            if not auth:
                return False
            
            is_auth = await JWT_VERIFY_SOCKET(jwt)
                    
            if is_auth: 
                sio.session(sid)
                return True
            
        except ValueError as e:
            print(e)
        
        return False
    return init_connect