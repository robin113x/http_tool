import argparse
import asyncio
from http_probe import HTTPProbe
from matchers_filters import MatchersFilters

def parse_args():
    parser = argparse.ArgumentParser(description="HTTP Probe Tool")
    parser.add_argument("-u", "--urls", nargs="+", required=True, help="Target URLs")
    parser.add_argument("-mc", "--match-code", type=int, nargs="*", help="Match status codes")
    parser.add_argument("-fc", "--filter-code", type=int, nargs="*", help="Filter status codes")
    return parser.parse_args()

async def main():
    args = parse_args()
    probe = HTTPProbe(urls=args.urls)
    responses = await probe.run()

    match_filter = MatchersFilters(
        matchers={"status_code": args.match_code},
        filters={"status_code": args.filter_code}
    )

    for response in responses:
        if match_filter.match(response) and match_filter.filter(response):
            print(response)

if __name__ == "__main__":
    asyncio.run(main())
