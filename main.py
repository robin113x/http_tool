import argparse
import requests
from requests.exceptions import RequestException
import mmh3
import hashlib
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Utility Functions
def calculate_hash(content, hash_type="md5"):
    """Calculate hash of given content based on hash_type."""
    if hash_type == "mmh3":
        return mmh3.hash(content)
    try:
        hasher = getattr(hashlib, hash_type)
        return hasher(content).hexdigest()
    except AttributeError:
        raise ValueError(f"Unsupported hash type: {hash_type}")


def fetch_url(url, headers=None):
    """Fetch the URL with requests and return the response."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except RequestException as e:
        print(f"[Error] {e}")
        return None


def detect_cdn(response):
    """Detect if the target URL is using a CDN."""
    cdn_headers = {
        "Server": ["cloudflare", "akamai", "fastly"],
        "X-CDN": ["cache", "akamai", "cloudflare"],
    }
    for header, values in cdn_headers.items():
        if header in response.headers:
            if any(value.lower() in response.headers[header].lower() for value in values):
                return True
    return False


def detect_waf(response):
    """Detect if the target URL is behind a Web Application Firewall (WAF)."""
    waf_indicators = ["x-sucuri-id", "x-firewall", "cloudflare"]
    for header in response.headers:
        if any(indicator in header.lower() for indicator in waf_indicators):
            return True
    return False


# Main Probing Function
def probe_url(url, args):
    """Probe a URL and print relevant information based on user flags."""
    print(f"\n[Probing] {url}")
    response = fetch_url(url, headers={"User-Agent": "HTTP-Probe-Tool"})
    if not response:
        return

    output = {"url": url, "status_code": response.status_code}

    # Basic Probes
    if args.status_code:
        output["status_code"] = response.status_code
    if args.content_length:
        output["content_length"] = len(response.content)
    if args.title:
        soup = BeautifulSoup(response.text, "html.parser")
        output["title"] = soup.title.string if soup.title else "N/A"
    if args.favicon:
        favicon_url = urlparse(url)._replace(path="/favicon.ico").geturl()
        favicon_response = fetch_url(favicon_url)
        if favicon_response:
            output["favicon_hash"] = calculate_hash(favicon_response.content, "mmh3")

    # CDN and WAF Detection
    if args.cdn:
        output["cdn_detected"] = detect_cdn(response)
    if args.waf:
        output["waf_detected"] = detect_waf(response)

    # Print or Save Output
    print(json.dumps(output, indent=2))


# Main Function
def main():
    parser = argparse.ArgumentParser(description="HTTP Probe Tool")
    parser.add_argument("-t", "--target", type=str, help="Target URL to probe")
    parser.add_argument("-l", "--list", type=str, help="File containing list of URLs")
    parser.add_argument("--status-code", action="store_true", help="Display response status code")
    parser.add_argument("--content-length", action="store_true", help="Display response content length")
    parser.add_argument("--title", action="store_true", help="Display page title")
    parser.add_argument("--favicon", action="store_true", help="Display favicon mmh3 hash")
    parser.add_argument("--cdn", action="store_true", help="Detect if CDN is used")
    parser.add_argument("--waf", action="store_true", help="Detect if WAF is used")

    args = parser.parse_args()

    # Load targets
    targets = []
    if args.target:
        targets.append(args.target)
    elif args.list:
        with open(args.list, "r") as file:
            targets = [line.strip() for line in file.readlines()]

    if not targets:
        print("[Error] No targets specified.")
        return

    for target in targets:
        probe_url(target, args)


if __name__ == "__main__":
    main()
