# from get_access_token import get_access_token, 
import time
import requests
from requests.auth import HTTPBasicAuth

from settings import Settings, Payload
from status_code_exception import StatusCodeException, Timeout, TimeoutException

from api_hello import post_data 


class TokenSteward(Settings):
    def __post_init__(self):
        super().__post_init__()
        self._t0 = 0
        
    @property
    def token(self):
        if self.remaining_time() <= 0: #equality on __init__
            self.refresh_token()
        return self._response["access_token"]

    @property
    def merit(self):
        """json of requests.post for token"""
        token_merit = {
            "url": self.token_url,
            "auth": HTTPBasicAuth(self.client_id, self.client_secret),
            "data": self.payload.dict(),
            "timeout": 10,
        }
        self._merit = token_merit  # noqa
        return token_merit

    def remaining_time(self):
        """int (s) of time remaining on token"""
        return self._response["expires_in"] - int((time.time() - self._t0))

    def refresh_token(self,timeout_requests:int=10):
        try:
            with Timeout(timeout_requests):
                response = requests.post(**self.merit)
                response.raise_for_status()
                self._t0 = time.time()
                self._response = response.json() # noqa
                return self._response["access_token"]
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to request token: {e}")
        except TimeoutException as e:
            raise RuntimeError(f"Request timed out: {e}")
        except StatusCodeException as e:
            raise RuntimeError(f"Status code exception: {e}")



if __name__ == "__main__":
    ts = token_steward = TokenSteward()
    try:
        token = token_steward.refresh_token()
        print("Access token obtained:", token)
    except RuntimeError as e:
        print(e)
        
    print(" begin post ")
    

hello_message = {
    "messages": [
        {"role": "user", "content": "What is the first letter of the alphabet?"}
    ]
}
result = post_data(ts.api.gpt4o, token, hello_message)

# print("Response from API:", result)

message_content = result["choices"][0]["message"]["content"]
print("Message Response:", message_content)