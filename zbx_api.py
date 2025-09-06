import requests

class ZabbixAPI:
    def __init__(self, url, user, password, verify_ssl=True, timeout=30):
        self.url = url
        self.user = user
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self._auth = None
        self._id = 0

    def _rpc(self, method, params=None, auth=True):
        self._id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._id,
        }
        if auth and self._auth:
            payload["auth"] = self._auth
        resp = requests.post(self.url, json=payload, timeout=self.timeout, verify=self.verify_ssl)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"Zabbix API error: {data['error']}")
        return data["result"]

    def login(self):
        res = self._rpc("user.login", {"user": self.user, "password": self.password}, auth=False)
        self._auth = res
        return True

    def event_get(self, time_from, time_till, severities=None, value=1):
        params = {
            "output": ["eventid", "clock", "severity", "name", "r_eventid", "acknowledged"],
            "selectHosts": ["hostid", "host"],
            "select_acknowledges": "extend",
            "time_from": time_from,
            "time_till": time_till,
            "value": value,
            "sortfield": ["clock"],
            "sortorder": "ASC",
        }
        if severities:
            params["severities"] = severities
        return self._rpc("event.get", params)

    def event_ack(self, eventids, message="Auto-ack by zbx-digest"):
        return self._rpc("event.acknowledge", {"eventids": eventids, "action": 6, "message": message})
