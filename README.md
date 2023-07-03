# Make TOR request with python
The goal if this repo is to document how to use [TOR](https://www.torproject.org/) with python3.


## Installation
You need `Python 3`.
Install python3 dependencies:
```bash
pip install -r requirements.txt
```
You need to install and enable TOR server.
```bash
sudo apt install tor
sudo service tor start
```

Then you need to activate the Tor Controler to be able to change ip on the fly.
First, create a password with:
```bash
tor --hash-password "YOUR_PASSWORD_HERE"
```
This should output something like: `16:E4E6B5F4E2B463F760A142078FE671D6FA2B522649E9420E830C36C895`. 

Keep that we will need it in the next step.

```bash
sudo vim /etc/tor/torrc
```

Change those 2 lines:

```
ControlPort 9051
# Change the value with the output of previous step.
HashedControlPassword 16:E4E6B5F4E2B463F760A142078FE671D6FA2B522649E9420E830C36C895
```

Then restart TOR:

```bash
sudo service tor restart
```

## Usage
### Without Docker
You can see a documented simple python usage of it in [simple.py](./simple.py).
In this version, your IP won't change once fixed.

You can see a documented example with ip renew each request in [ip_renew.py](./ip_renew.py).

### With Docker
You can also use docker to do that.

First change the TOR password in the Docker file. Use the output of: `tor --hash-password "your password here"`
```Dockerfile
ENV TOR_PASSWORD="16:6710B9B3468CA479608B0F46A6AF973EF7009ECD1698BD79F39283E2C4"
```

Then build the image and run the container.
```bash
docker build -t python_tor .;
docker run -t python_tor;
```


## Tor python module
If you would like to use this module in your own project, you can use the `Tor` class from the [tor_module.py](./tor_module.py) file.

```python
from tor_module import Tor

tor = Tor()

# Do your request like this
response = tor.get_request("https://api.ipify.org?format=json").text
print(response)

# Renew your ip like this
tor.renew_tor_ip()
response = tor.get_request("https://api.ipify.org?format=json").text
print(response)

# Check your ip like this
ip = tor.get_ip()
print(ip)
```

## Resources
- [StackOverflow demo](https://stackoverflow.com/questions/28035413/general-socks-server-failure-when-switching-identity-using-stem)
- [Step-by-step Blog post](https://sylvaindurand.org/use-tor-with-python/)