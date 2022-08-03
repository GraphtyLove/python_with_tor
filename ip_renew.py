import requests
from stem import Signal
from stem.control import Controller

# Connect to TOR controller
controller = Controller.from_port(port=9051)

# Service that return your IP
url = 'https://ipof.me/ip'

# Set proxies to send the request to TOR
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}



def renew_tor():
    """Function that renew your TOR ip."""
    # Set your password with the password you defined during installation (See README.md)
    controller.authenticate("YOUR_PASSWORD_HERE:q")
    controller.signal(Signal.NEWNYM)


def send_request():
    renew_tor()
    
    # Request with the procies (so using tor)
    tor_ip = requests.get(url, proxies=proxies).text
    # Request without the prixies
    local_ip = requests.get(url).text

    # Print results
    print("Local ip: ", local_ip)
    print("tor ip:   ", tor_ip)


# Do the request 5 times.
for i in range(5):
    send_request()