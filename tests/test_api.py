import http
import json
import http.client

conn = http.client.HTTPSConnection("kg-api.cloud")
headers = {
   'Accept': 'application/json',
   'Authorization': 'Bearer sk-C7IhUgedVR5bHhTTCdD88aC122484690B0974a86E150D7Fe',
   'Content-Type': 'application/json'
}

payload = json.dumps({
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "who are you"
        }
    ]
})
#conn.request("POST", "https//kg-api.cloud/v1/chat/completions", payload, headers)
conn.request("POST", "/v1/chat/completions", payload, headers)
res = conn.getresponse()
data = res.read()
res = data.decode("utf-8")
msg = json.loads(res)
message = msg["choices"][0]["message"]["content"]
print(message)