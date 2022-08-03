import requests

# Service that return your IP
url = 'https://ipof.me/ip'



# Set proxies to send the request to TOR
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# Request with the procies (so using tor)
tor_ip = requests.get(url, proxies=proxies).text
# Request without the prixies
local_ip = requests.get(url).text

# Print results
print("Local ip: ", local_ip)
print("tor ip:   ", tor_ip)