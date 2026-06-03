import re
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle, SimpleRateThrottle

class CustomThrottleMixin(SimpleRateThrottle):
    """
    Mixin that supports rate parsing of custom periods like '300/15m'.
    """
    def parse_rate(self, rate):
        if not rate:
            return None, None
        
        match = re.match(r"^(\d+)/(\d*)([smhd])$", rate)
        if not match:
            return super().parse_rate(rate)
            
        num, multiplier, period = match.groups()
        num_requests = int(num)
        mult = int(multiplier) if multiplier else 1
        
        duration_unit = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400
        }[period]
        
        return num_requests, mult * duration_unit

class CustomAnonRateThrottle(CustomThrottleMixin, AnonRateThrottle):
    scope = "anon"

class CustomUserRateThrottle(CustomThrottleMixin, UserRateThrottle):
    scope = "user"
