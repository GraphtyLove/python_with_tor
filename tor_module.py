from typing import Dict, Any

import requests
import os
import time
from stem import Signal, CircStatus
from stem.control import Controller


class Tor:
	"""Class that handle TOR connection."""

	# Set proxies to send the request to TOR
	_proxies = {
		'http': 'socks5h://127.0.0.1:9050',
		'https': 'socks5h://127.0.0.1:9050'
	}
	# API that return your IP
	_get_ip_url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=get_user_info_data"

	def __init__(
			self,
			tor_password: str = os.environ.get("TOR_PASSWORD", "YOUR_PASSWORD_HERE"),
			headers: Dict[str, str] | None = None
	):
		self._tor_password = tor_password
		self.headers = headers
		# Connect to TOR controller
		self._controller = Controller.from_port(port=9051)
		# Create a new session to optimize the request's speed
		self._session = requests.Session()
		self._session.proxies = self._proxies
		self._session.headers = headers

		self.ip_history = []

	def _merge_headers(self, new_headers: Dict[str, str]) -> Dict[str, str]:
		"""Helper method to merge the base headers with request-specific headers."""
		return self.headers if new_headers is None else new_headers.update(self.headers)

	def _close_all_circuits(self) -> None:
		"""
		Function that close all circuits.

		This is used to ensure tor will use the new IP after renewal.
		"""
		for circuit in self._controller.get_circuits():
			if circuit.status != CircStatus.BUILT:
				continue

			for entry in self._controller.get_network_statuses():
				if entry.address in circuit.path:
					self._controller.close_circuit(circuit.id)

	def renew_tor_ip(self, max_retries=5) -> None:
		"""
		Function that renew your TOR ip.

		:param max_retries: Max number of ip renew retries.
		"""
		for _ in range(max_retries):
			# Store the current ip in history
			tor_current_ip = self.get_ip()
			self.ip_history.append(tor_current_ip)
			self._controller.authenticate(password=self._tor_password)
			# Renew the ip
			self._controller.signal(Signal.NEWNYM)
			# Wait for the newnym to be available
			time.sleep(self._controller.get_newnym_wait())
			# Close all circuits
			self._close_all_circuits()
			new_ip = self.get_ip()
			if new_ip != tor_current_ip:
				return
			print("Renewing IP failed, retrying...")
		print(f"Failed to renew IP after {max_retries} retries.")

	def get_request(self, url: str, headers: Dict[str, str] | None = None) -> requests.Response:
		"""Send a GET request via TOR network."""
		headers = self._merge_headers(headers)
		response = self._session.get(url, proxies=self._proxies, headers=headers)
		return response

	def post_request(
			self,
			url: str,
			headers: Dict[str, str] | None = None,
			request_body: Dict[str, Any] | None = None
	) -> requests.Response:
		"""Send a POST request via TOR network."""
		headers = self._merge_headers(headers)
		response = self._session.post(
			url,
			proxies=self._proxies,
			headers=headers,
			json=request_body if request_body is not None else {}
		)
		return response

	def get_ip(self, get_tor_ip: bool = True) -> str:
		"""
		Helper method to get the current IP (TOR or local).
		:param get_tor_ip: If True, return the TOR ip, else return the local ip.
		:return: The current IP (TOR or local).
		"""
		local_ip = requests.get(self._get_ip_url).json().get("ip")
		
		if get_tor_ip:
			tor_ip = self.get_request(self._get_ip_url).json().get("ip")
			if local_ip == tor_ip:
				print("Your IP is not protected!")
			return tor_ip
		else:
			return local_ip


def test_ip_renew(tor_instance: Tor) -> str:
	tor_instance.renew_tor_ip()
	# Request with the proxies (so using tor)
	tor_ip = tor_instance.get_ip()
	# Request without the proxies
	local_ip = tor_instance.get_ip(get_tor_ip=False)
	# Print results
	print("Local ip: ", local_ip)
	print("tor ip:   ", tor_ip)
	return tor_ip


if __name__ == '__main__':
	"""Test if Tor is working"""
	tor = Tor()
	# Do the request 5 times.
	ips = [test_ip_renew(tor) for i in range(5)]
	# Ensure that the IP is different each time.
	assert len(set(ips)) == 5, "Your IP should change each time you renew it."
