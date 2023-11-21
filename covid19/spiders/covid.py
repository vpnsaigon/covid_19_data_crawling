import scrapy
import re

def no_accent_vietnamese(s):
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(r'[Đ]', 'D', s)
    s = re.sub(r'[đ]', 'd', s)

    marks_list = [u'\u0300', u'\u0301', u'\u0302', u'\u0303', u'\u0306',u'\u0309', u'\u0323']

    for mark in marks_list:
        s = s.replace(mark, '')

    return s

class CovidSpider(scrapy.Spider):
    name = "covid"
    allowed_domains = ["web.archive.org"]
    start_urls = ["https://web.archive.org/web/20210907023426/htttps://ncov.moh.gov.vn/vi/web/guest/dong-thoi-gian"]

    def parse(self, response):
        timeline = response.xpath('//div[contains(@class, "timeline-detail")]')
        next_link = response.xpath('//div[contains(@class, "clearfix lfr-pagination")]/ul/li[2]/a/@href').get()

        for case in timeline:
            # get time
            time = case.xpath('.//h3/text()').get()
            if not time:
                continue
            
            # get new_case
            new_case_text = case.xpath('.//p[2]/text()').get()
            if not new_case_text:
                continue

            new_case = re.findall('[0-9.]+', new_case_text)
            if not new_case:
                continue

            new_case = new_case[0]
            if '.' in new_case:
                new_case = new_case.replace('.', '')
            new_case = int(new_case)

            # get city and case
            city_case_text = case.xpath('.//div/p[3]/text()[1]').get()
            city_case_listdict = []

            if city_case_text:
                city_case_text = no_accent_vietnamese(city_case_text)
                if 'trong nuoc' in city_case_text: # .strip().startswith('Trong do')
                    city_case_list = city_case_text.split(',')
                    length_ccl = len(city_case_list)

                    for i in range(length_ccl):
                        city_case = city_case_list[i]
                        city = case = []

                        if i == 0:
                            city_case = city_case.split('tai')[-1]
                        if i == length_ccl - 1:
                            city_case = city_case.split('trong')[0]
                        
                        city = re.findall('\D+\s+', city_case)
                        case = re.findall('([0-9.]+)', city_case)

                        if city and case:
                            city = city[0]
                            city = city.strip()

                            case = case[-1]
                            if '.' in case:
                                case = case.replace('.', '')
                            if case:
                                case = int(case)
                        else:
                            continue

                        city_case_listdict.append({'city': city, 'case': case})

            # dataset
            yield {
                'time': time,
                'new_case': new_case,
                'city_case': city_case_listdict
            }
            
        try:
            yield scrapy.Request(url=next_link, callback=self.parse)
        except:
            pass

