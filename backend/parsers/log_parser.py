"""
Modular, resilient log parsers.
Supported formats:
  - CJLogParser             : JSON-array logs (cj.log)
  - UniversalWebLogParser   : Flexible regex matching (handles timestamp first, IP first, Apache, Nginx, custom)
  - ApacheCombinedParser    : Standard Apache Combined format
  - ApacheCommonParser      : Standard Apache Common format
  - NginxParser             : Nginx standard format
  - CSVParser               : CSV / TSV structured logs
  - JSONParser              : JSON Lines (JSONL) or JSON Array objects
"""

import csv
import io
import json
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, IO, List, Optional


IPV4_PATTERN = re.compile(r'\b(?P<ip>(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))\b')
IPV6_PATTERN = re.compile(r'\b(?P<ip6>(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|::1|fe80::[0-9a-fA-F:]+)\b')
HOST_PATTERN = re.compile(r'\b(?P<host>localhost|[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9.-]+)\b')
TIMESTAMP_BRACKET_PATTERN = re.compile(r'\[(?P<time>[^\]]+)\]')
TIMESTAMP_ISO_PATTERN = re.compile(r'(?P<time>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)')
HTTP_REQUEST_PATTERN = re.compile(r'"(?P<method>[A-Z]{3,8})\s+(?P<path>[^"\s]+)(?:\s+HTTP/[0-9.]+)?\"')
HTTP_STATUS_PATTERN = re.compile(r'\b(?P<status>[1-5]\d{2})\b')


class BaseLogParser(ABC):
    FORMAT_NAME: str = "unknown"
    AVAILABLE_FIELDS: List[str] = []

    @abstractmethod
    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single line. Return None if line does not conform."""

    def parse_stream(
        self,
        stream: IO[str],
        max_lines: Optional[int] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        count = 0
        for line in stream:
            line = line.strip()
            if not line:
                continue
            record = self.parse_line(line)
            if record is not None:
                yield record
                count += 1
                if max_lines and count >= max_lines:
                    break

    def detect_confidence(self, sample_lines: List[str]) -> float:
        if not sample_lines:
            return 0.0
        hits = sum(
            1 for line in sample_lines
            if line.strip() and self.parse_line(line.strip()) is not None
        )
        return hits / len(sample_lines)


# ─── 1. CJ JSON-Array Parser (University Dataset) ───────────────────────────

class CJLogParser(BaseLogParser):
    FORMAT_NAME = "cj"
    AVAILABLE_FIELDS = [
        "timestamp", "ip", "port", "user_agent", "language", "metadata",
    ]

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        line = line.strip()
        if not (line.startswith("[") and line.endswith("]")):
            return None
        try:
            record = json.loads(line)
        except Exception:
            return None

        if not isinstance(record, list) or len(record) < 4:
            return None

        # Standard 8-element university log
        if len(record) == 8:
            return {
                "timestamp":  str(record[2]),
                "ip":         str(record[3]),
                "port":       record[4],
                "user_agent": str(record[5]) if record[5] is not None else "unknown",
                "language":   str(record[6]) if record[6] is not None else "unknown",
                "metadata":   str(record[7]) if record[7] is not None else "unknown",
            }

        # Dynamic array extraction
        res: Dict[str, Any] = {
            "timestamp": None,
            "ip": None,
            "port": 80,
            "user_agent": "unknown",
        }
        for item in record:
            s = str(item)
            if IPV4_PATTERN.search(s) and res["ip"] is None:
                res["ip"] = s
            elif isinstance(item, int) and 1 <= item <= 65535 and res["port"] == 80:
                res["port"] = item
            elif ("2023" in s or "2024" in s or ":" in s) and res["timestamp"] is None:
                res["timestamp"] = s
            elif len(s) > 10 and res["user_agent"] == "unknown":
                res["user_agent"] = s

        return res if res["ip"] else None


# ─── 2. Universal Web Log Parser (Flexible Heuristic) ───────────────────────

class UniversalWebLogParser(BaseLogParser):
    """
    Highly flexible regex parser for Apache, Nginx, custom proxy, and raw server logs.
    Handles timestamp-first, IP-first, with or without ident, with or without referrer.
    """
    FORMAT_NAME = "universal"
    AVAILABLE_FIELDS = [
        "ip", "timestamp", "method", "path", "status", "bytes", "user_agent",
    ]

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        # 1. IP Address or Hostname
        ip = "127.0.0.1"
        ip_match = IPV4_PATTERN.search(line)
        if ip_match:
            ip = ip_match.group("ip")
        else:
            ip6_match = IPV6_PATTERN.search(line)
            if ip6_match:
                ip = ip6_match.group("ip6")
            else:
                host_match = HOST_PATTERN.search(line)
                if host_match:
                    ip = host_match.group("host")
                else:
                    tokens = [t for t in line.split() if not t.startswith(("[", "{", "\"", "'"))]
                    if tokens and len(tokens[0]) >= 3 and not tokens[0].startswith(("#", "//", "/*")):
                        ip = tokens[0].strip("[]():,")
                    else:
                        ip = "127.0.0.1"

        # 2. Timestamp (bracketed or ISO)
        time_str = "unknown"
        time_match = TIMESTAMP_BRACKET_PATTERN.search(line)
        if time_match:
            time_str = time_match.group("time")
        else:
            iso_match = TIMESTAMP_ISO_PATTERN.search(line)
            if iso_match:
                time_str = iso_match.group("time")

        # 3. HTTP Request (method + path)
        method = "GET"
        path = "/"
        req_match = HTTP_REQUEST_PATTERN.search(line)
        if req_match:
            method = req_match.group("method")
            path = req_match.group("path")
        else:
            # Fallback search for GET/POST/etc
            v_match = re.search(r'\b(GET|POST|PUT|DELETE|HEAD|OPTIONS|CONNECT)\b\s+(\S+)', line)
            if v_match:
                method = v_match.group(1)
                path = v_match.group(2)

        # 4. Status code and Bytes
        status = 200
        bytes_val = 0
        post_req_match = re.search(r'"\s+(?P<status>[1-5]\d{2})\s+(?P<bytes>\d+|-)', line)
        if post_req_match:
            status = int(post_req_match.group("status"))
            raw_b = post_req_match.group("bytes")
            bytes_val = int(raw_b) if raw_b.isdigit() else 0
        else:
            status_matches = list(HTTP_STATUS_PATTERN.finditer(line))
            if status_matches:
                for sm in status_matches:
                    if sm.start() > (req_match.end() if req_match else len(ip)):
                        val = int(sm.group("status"))
                        if 100 <= val <= 599:
                            status = val
                            break
            b_match = re.search(r'\b(?P<bytes>\d{1,9})\b(?=\s+"|\s*$)', line)
            if b_match:
                try:
                    bytes_val = int(b_match.group("bytes"))
                except Exception:
                    bytes_val = 0

        # 5. User-Agent
        user_agent = "unknown"
        quotes = re.findall(r'"([^"]*)"', line)
        if len(quotes) >= 2:
            candidate = quotes[-1]
            if len(candidate) > 2 and not candidate.startswith("HTTP/"):
                user_agent = candidate
            elif len(quotes) >= 3:
                user_agent = quotes[-1]
        elif len(quotes) == 1 and not quotes[0].startswith(("GET", "POST", "HEAD", "PUT")):
            user_agent = quotes[0]

        # Require at least log structure (timestamp, HTTP request, or explicit status)
        has_time = time_str != "unknown"
        has_req = req_match is not None or v_match is not None
        has_code = post_req_match is not None
        if not (has_time or has_req or has_code):
            return None

        return {
            "ip":         ip,
            "timestamp":  time_str,
            "method":     method,
            "path":       path,
            "status":     status,
            "bytes":      bytes_val,
            "user_agent": user_agent,
        }

    def detect_confidence(self, sample_lines: List[str]) -> float:
        if not sample_lines:
            return 0.0
        hits = sum(1 for l in sample_lines if self.parse_line(l) is not None)
        return (hits / len(sample_lines)) * 0.95


# ─── 3. Standard Apache Combined Parser ───────────────────────────────────────

_APACHE_COMBINED_RE = re.compile(
    r'(?P<ip>\S+)\s+'
    r'\S+\s+'
    r'\S+\s+'
    r'\[(?P<time>[^\]]+)\]\s+'
    r'"(?P<request>[^"]*)"\s+'
    r'(?P<status>\d{3})\s+'
    r'(?P<bytes>\S+)\s+'
    r'"(?P<referrer>[^"]*)"\s+'
    r'"(?P<user_agent>[^"]*)"'
)


class ApacheCombinedParser(BaseLogParser):
    FORMAT_NAME = "apache_combined"
    AVAILABLE_FIELDS = [
        "ip", "timestamp", "method", "path",
        "status", "bytes", "referrer", "user_agent",
    ]

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        m = _APACHE_COMBINED_RE.match(line.strip())
        if not m:
            return None
        parts = m.group("request").split(" ", 2)
        return {
            "ip":         m.group("ip"),
            "timestamp":  m.group("time"),
            "method":     parts[0] if parts else "GET",
            "path":       parts[1] if len(parts) > 1 else "/",
            "status":     int(m.group("status")),
            "bytes":      int(m.group("bytes")) if m.group("bytes").isdigit() else 0,
            "referrer":   m.group("referrer"),
            "user_agent": m.group("user_agent"),
        }


# ─── 4. Standard Nginx Access Parser ──────────────────────────────────────────

_NGINX_RE = re.compile(
    r'(?P<ip>\S+)\s+'
    r'\S+\s+'
    r'\S+\s+'
    r'\[(?P<time>[^\]]+)\]\s+'
    r'"(?P<request>[^"]*)"\s+'
    r'(?P<status>\d{3})\s+'
    r'(?P<bytes>\d+)\s+'
    r'"(?P<referrer>[^"]*)"\s+'
    r'"(?P<user_agent>[^"]*)"'
)


class NginxParser(BaseLogParser):
    FORMAT_NAME = "nginx"
    AVAILABLE_FIELDS = [
        "ip", "timestamp", "method", "path",
        "status", "bytes", "referrer", "user_agent",
    ]

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        m = _NGINX_RE.match(line.strip())
        if not m:
            return None
        parts = m.group("request").split(" ", 2)
        return {
            "ip":         m.group("ip"),
            "timestamp":  m.group("time"),
            "method":     parts[0] if parts else "GET",
            "path":       parts[1] if len(parts) > 1 else "/",
            "status":     int(m.group("status")),
            "bytes":      int(m.group("bytes")),
            "referrer":   m.group("referrer"),
            "user_agent": m.group("user_agent"),
        }


# ─── 5. CSV / TSV Parser ──────────────────────────────────────────────────────

class CSVParser(BaseLogParser):
    FORMAT_NAME = "csv"
    AVAILABLE_FIELDS = []

    def __init__(self):
        self._headers: Optional[List[str]] = None
        self._delimiter: str = ","

    def detect_confidence(self, sample_lines: List[str]) -> float:
        if not sample_lines:
            return 0.0
        first = sample_lines[0].strip()
        if first.startswith(("[", "{")):
            return 0.0
        if first.count(",") >= 2 or first.count("\t") >= 2 or first.count(";") >= 2:
            return 0.8
        return 0.0

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        line = line.strip()
        if not line:
            return None
        if self._headers is None:
            delim = "\t" if "\t" in line else (";" if ";" in line and "," not in line else ",")
            self._delimiter = delim
            reader = csv.reader([line], delimiter=delim)
            try:
                row = next(reader)
                if any(h.lower() in ("ip", "client_ip", "timestamp", "user_agent", "path", "method", "label") for h in row):
                    self._headers = [h.strip().lower() for h in row]
                    self.AVAILABLE_FIELDS = self._headers
                    return None
                else:
                    self._headers = [f"col_{i}" for i in range(len(row))]
                    self.AVAILABLE_FIELDS = self._headers
            except Exception:
                return None

        reader = csv.reader([line], delimiter=self._delimiter)
        try:
            row = next(reader)
            if not row or len(row) != len(self._headers):
                return None
            raw_dict = dict(zip(self._headers, row))
            res: Dict[str, Any] = {}
            for k, v in raw_dict.items():
                k_clean = k.strip().lower()
                if k_clean in ("ip", "client_ip", "host", "remote_addr"):
                    res["ip"] = v
                elif k_clean in ("timestamp", "time", "date", "datetime"):
                    res["timestamp"] = v
                elif k_clean in ("user_agent", "useragent", "agent", "ua"):
                    res["user_agent"] = v
                elif k_clean in ("method", "verb", "http_method"):
                    res["method"] = v
                elif k_clean in ("path", "url", "uri", "request_path"):
                    res["path"] = v
                elif k_clean in ("status", "response_code", "status_code"):
                    try: res["status"] = int(v)
                    except Exception: res["status"] = 200
                elif k_clean in ("port", "dest_port"):
                    try: res["port"] = int(v)
                    except Exception: res["port"] = 80
                else:
                    res[k_clean] = v

            if "ip" not in res:
                for v in row:
                    if IPV4_PATTERN.search(str(v)):
                        res["ip"] = str(v)
                        break

            return res if res.get("ip") else raw_dict
        except Exception:
            return None


# ─── 6. JSON Lines / JSON Object Parser ──────────────────────────────────────

class JSONParser(BaseLogParser):
    FORMAT_NAME = "json"
    AVAILABLE_FIELDS = []

    def detect_confidence(self, sample_lines: List[str]) -> float:
        if not sample_lines:
            return 0.0
        hits = 0
        for l in sample_lines:
            l = l.strip()
            if l.startswith("{") and l.endswith("}"):
                try:
                    obj = json.loads(l)
                    if isinstance(obj, dict):
                        hits += 1
                except Exception:
                    pass
        return hits / len(sample_lines)

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        line = line.strip()
        if line.endswith(","):
            line = line[:-1].strip()
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
        return None


# ─── Registry ────────────────────────────────────────────────────────────────

PARSER_CLASSES = [
    CJLogParser,
    ApacheCombinedParser,
    NginxParser,
    UniversalWebLogParser,
    JSONParser,
    CSVParser,
]


def detect_format(sample_lines: List[str]) -> BaseLogParser:
    best_cls = UniversalWebLogParser
    best_confidence = 0.0

    for cls in PARSER_CLASSES:
        p = cls()
        conf = p.detect_confidence(sample_lines)
        if conf > best_confidence:
            best_confidence = conf
            best_cls = cls

    return best_cls()


def get_parser_by_name(name: str) -> Optional[BaseLogParser]:
    if not name:
        return None
    key = name.strip().lower()

    if key in ("cj_log", "cj", "university", "log_array"):
        return CJLogParser()
    if key in ("apache", "apache_combined", "apache_common", "combined"):
        return ApacheCombinedParser()
    if key in ("nginx", "web"):
        return NginxParser()
    if key in ("universal", "auto", "heuristic", "syslog"):
        return UniversalWebLogParser()
    if key in ("json", "jsonl", "json_array"):
        return JSONParser()
    if key in ("csv", "tsv"):
        return CSVParser()

    for cls in PARSER_CLASSES:
        if cls.FORMAT_NAME == key:
            return cls()

    return None
