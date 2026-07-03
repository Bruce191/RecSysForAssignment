from pydantic import BaseModel
from typing import Optional

###################################### Normal Users #################################################################################

class UserRegister(BaseModel):
    name: str
    password: str
    is_child: bool
    #preferences: List[str] # list for preferences which rohini wil get from backendfunctionroutes to display

#so we generate a user id and thenr eturn to user once created user,
class UserResponse(BaseModel):
    user_id: str
    name: str

#user interactions
class UserInteraction(BaseModel):
    interaction_type: str
    content_id: str

###################################### Normal Users #################################################################################


###################################### Token JWT Verifications #######################################################################

# Response schema for JWT token returned after login.
class Token(BaseModel):
    access_token: str
    token_type: str

# Token data (used internally when decoding a JWT token to extract info like the username).
class TokenData(BaseModel):
    username: Optional[str] = None

    
###################################### Token JWT Verifications #######################################################################