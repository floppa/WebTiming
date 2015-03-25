# WebTiming
Check Navigation Timing API from the terminal through selenium &amp; chromedriver

## Prerequisites

- Python
- Selenium ```pip install selenium```
- ChromeDriver ```brew install cromedriver```

## Usage

- Get single value ```./web_timings.py -u=http://domain.url```
- Get values multiple sites ```./web_timings.py -u=http://domain.url, http://domain.url```
- Get all values ```./web_timings.py -u=http://domain.url -v=responseTime```
- Get details ```./web_timings.py -u=http://domain.url -d=true```
- Get output as csv ```./web_timings.py -u=http://domain.url -c=true```

You can of course combine these to what you want.

## Boring
Not headless on osx 

