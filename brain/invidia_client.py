import os,logging,threading,requests

logger=logging.getLogger("NewsFactory.NVIDIA")

class NVIDIAClient:
    def __init__(self):
        self.name="NVIDIA Brain"
        self.base_url="https://integrate.api.nvidia.com/v1"
        self.model=os.getenv("NVIDIA_MODEL","nvidia/nemotron-3.5-lightning-30b-a3b")
        self.keys=[]
        for number in range(1,5):
            key=os.getenv(f"NVIDIA_API_KEY_{number}")
            if key:
                key=key.strip()
                if key:self.keys.append(key)
        if not self.keys:
            raise RuntimeError("No NVIDIA API keys found. Set NVIDIA_API_KEY_1 through NVIDIA_API_KEY_4 in Railway Variables.")
        self.current_key=0
        self.timeout=60
        self.lock=threading.Lock()
        self.total_requests=0
        self.total_failovers=0
        self.key_successes={index+1:0 for index in range(len(self.keys))}
        self.key_failures={index+1:0 for index in range(len(self.keys))}
        logger.info("NVIDIA Brain loaded with %s API keys using model %s.",len(self.keys),self.model)

    def ask(self,prompt,system="You are an AI newsroom assistant.",temperature=0.2,max_tokens=2000):
        return self.generate(
            messages=[
                {"role":"system","content":system},
                {"role":"user","content":prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

    def generate(self,messages,temperature=0.2,max_tokens=2000):
        total_keys=len(self.keys)
        if total_keys==0:raise RuntimeError("No NVIDIA API keys available.")
        with self.lock:
            start_index=self.current_key
            self.current_key=(self.current_key+1)%total_keys
            self.total_requests+=1
        logger.info("NVIDIA request starting with key %s/%s.",start_index+1,total_keys)
        last_error=None
        for attempt in range(total_keys):
            key_index=(start_index+attempt)%total_keys
            key=self.keys[key_index]
            logger.info("NVIDIA attempting key %s/%s.",key_index+1,total_keys)
            try:
                result=self._request(key,messages,temperature,max_tokens)
                self.key_successes[key_index+1]+=1
                logger.info("NVIDIA key %s succeeded.",key_index+1)
                return result
            except Exception as error:
                last_error=error
                self.key_failures[key_index+1]+=1
                logger.warning("NVIDIA key %s failed. Trying next key.",key_index+1)
                if attempt<total_keys-1:self.total_failovers+=1
        logger.error("All NVIDIA API keys failed.")
        raise RuntimeError(f"All NVIDIA API keys failed. Last error: {last_error}")

    def _request(self,key,messages,temperature,max_tokens):
        url=self.base_url+"/chat/completions"
        headers={
            "Authorization":f"Bearer {key}",
            "Content-Type":"application/json",
            "Accept":"application/json"
        }
        payload={
            "model":self.model,
            "messages":messages,
            "temperature":temperature,
            "max_tokens":max_tokens
        }
        response=requests.post(url,headers=headers,json=payload,timeout=self.timeout)
        if not response.ok:
            raise RuntimeError(f"NVIDIA HTTP {response.status_code}: {response.text[:300]}")
        data=response.json()
        choices=data.get("choices",[])
        if not choices:raise RuntimeError("NVIDIA returned no choices.")
        message=choices[0].get("message",{})
        content=message.get("content","")
        if not content:raise RuntimeError("NVIDIA returned empty content.")
        return content.strip()

    def status(self):
        return {
            "provider":"NVIDIA",
            "model":self.model,
            "keys_configured":len(self.keys),
            "active_key":self.current_key+1,
            "rotation":"ROUND_ROBIN",
            "failover":True,
            "total_requests":self.total_requests,
            "total_failovers":self.total_failovers,
            "key_successes":dict(self.key_successes),
            "key_failures":dict(self.key_failures),
            "status":"READY"
        }
