class MatchersFilters:
    def __init__(self, matchers=None, filters=None):
        self.matchers = matchers or {}
        self.filters = filters or {}

    def match(self, response):
        if "status_code" in self.matchers:
            if response.get("status_code") not in self.matchers["status_code"]:
                return False
        if "content_length" in self.matchers:
            if len(response.get("content", "")) not in self.matchers["content_length"]:
                return False
        return True

    def filter(self, response):
        if "status_code" in self.filters:
            if response.get("status_code") in self.filters["status_code"]:
                return False
        return True
