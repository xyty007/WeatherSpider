# WeatherSpider

This project is used to crawl realtime weather data of certain point every fixed time interval or the history weather of all cities in China.

### Data source  
**realtime data:** 彩云天气api  
**history data:*** 天气911  

### Environment  
**System:** windows 10  
**python:** 2.7  
Use scrapy to crawl the history weather

### Usage  
**For history:** run start.py, data will saved in /Files/HistoryWeather sorted by province/city  
**For realtime:** run /RealtimeSpider/realtime_aps.py, data will saved in ./real_time_weather.csv  
realtime.py use threading.Timer to schedule crawls  
`time_interval = timeout + time_to_create_a_new_thread`  
so, the crawl interval is always longer than time_out setted.
