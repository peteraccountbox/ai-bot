import requests

response = requests.get(
    "https://agilecrm.com.com/robots.txt",
    proxies={
        scheme: "https://YOUR_API_KEY:@api.zyte.com:8014"
        for scheme in ("http", "https")
    },
)
http_response_body: bytes = response.content
print(http_response_body.decode())