
import cloudscraper
from CalendarNew.new import New
from bs4 import BeautifulSoup
from datetime import datetime, date
from dateutil import tz
from CalendarNew.impact import Impact

class CalendarNews: 
    
    def __init__(self, timezone ='GTM-5'):
        self.scraper = cloudscraper.create_scraper(delay=10, browser='chrome') 
        self.base_url = 'https://www.forexfactory.com/'
        self.today_param = 'calendar?day=today'
        self.fields = ['date', 'time', 'currency', 'impact', 'event', 'actual', 'forecast', 'previous']
        self.current_timezone = self.get_timezone()
        self.timezone = timezone

    def get_soup(self, url):
        content = self.scraper.get(self.base_url + url).text
        return BeautifulSoup(content, 'html.parser')

    def convert_time(self, date):
        to_zone = tz.gettz(self.timezone)
        d = date.replace(tzinfo=self.current_timezone)
        return d.astimezone(to_zone)
    
    def get_timezone(self):
        soup = self.get_soup('timezone')
        result = soup.find("select", id="timezone").find_all('option', selected=True)[0].text
        return tz.gettz(result)

    def get_impact_code(self, str):
        impact = Impact.NON
        if str == "High Impact Expected":
            impact = Impact.HIGH
        elif str == "Med Impact Expected":
            impact = Impact.MED
        elif str == "Low Impact Expected":
            impact = Impact.LOW
        elif str == "Non-Economic":
            impact = Impact.NON

        return impact

    def convert24(self,s):
        if str == "All Day":
            return date.today()
        if s.endswith('am') and s.startswith('12'):
            s = s.replace('12', '00')
        if s.endswith('pm') and not s.startswith('12'):
            time_s = s.split(':')
            time_s[0] = str(int(time_s[0]) + 12)
            s = ":".join(time_s)    
        return s.replace('am', '').replace('pm', '')

    def get_date(self, time):
        t24 = self.convert24(time)
        if t24 == "All Day":
            return None
        h,m = t24.split(":")
        d = datetime.today().replace(hour=int(h),minute=int(m),second=0,microsecond=0)
        return self.convert_time(d)

    def get_today(self):

        soup = self.get_soup(self.today_param)
        calendar_table = soup.find("table", class_="calendar__table")
        table_rows = calendar_table.select('tr.calendar__row.calendar_row')
        result = []

        for table_row in table_rows:
            time = datetime.today()
            allday= False
            currency, impact, event, actual, forecast, previous = '', '', '', '', '', ''
            for field in self.fields:
                data = table_row.select('td.calendar__cell.calendar__{0}.{0}'.format(field))[0]
                value = data.text.strip()
                if field == 'time':  
                    if value == '':
                        if len(result) >0:
                            time = result[-1].time
                            allday = result[-1].allday
                        else:
                            allday = False
                            time = None
                    
                    elif(value == 'All Day'):
                        allday = True
                        time = None
                    elif value != '' and value != 'All Day':
                        time = self.get_date(value)
                        allday = False
                elif field == 'currency':
                    currency = data.text.strip()
                elif field == 'impact':
                    impact = self.get_impact_code(data.find('span')['title'])
                elif field == 'event':
                    event = data.text.strip()
                elif field == 'actual':
                    actual = data.text.strip()
                elif field == 'forecast':
                    forecast = data.text.strip()
                elif field == 'previous':
                    previous = data.text.strip()
    
            result.append(New(time, currency, impact, event, actual, forecast, previous, allday))
        return result