import scrapy
import re

BASE_URL = 'http://en.wikipedia.org'

class NWinnerItemBio(scrapy.Item):
    link = scrapy.Field()
    name = scrapy.Field()
    mini_bio = scrapy.Field()
    image_urls = scrapy.Field()
    bio_image = scrapy.Field()
    images = scrapy.Field()

class NWinnerSpiderBio(scrapy.Spider):

    name = 'nwinners_minibio'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ["http://en.wikipedia.org/wiki/List_of_Nobel_laureates_by_country"]

    custom_settings = {
        'ITEM_PIPELINES': {'nobel_winners.pipelines.NobelImagesPipeline': 1}
    }
    def parse(self, response):
        filename = response.url.split('/')[-1]
        h3s = response.xpath('//h3')
        for h3 in list(h3s):
            country = h3.xpath('span[@class="mw-headline"]/text()').extract()
            if country:
                winners = h3.xpath('following-sibling::ol[1]')
                for w in winners.xpath('li'):
                    wdata = {}
                    wdata['link'] = BASE_URL + w.xpath('a/@href').extract()[0]
                    # Process the winner's bio page with the get_mini_bio method
                    request = scrapy.Request(wdata['link'],
                        callback=self.get_mini_bio)
                    request.meta['item'] = NWinnerItemBio(**wdata)
                    yield request
    
    def get_mini_bio(self, response):
        """ Get the winner's bio-text and photo """

        BASE_URL_ESCAPED = 'http:\/\/en.wikipedia.org'
        item = response.meta['item']
        item['image_urls'] = []
        img_src = response.xpath('//table[contains(@class, "infobox")]//img/@src')
        if img_src:
            item['image_urls'] = ['http:' + img_src[0].extract()]
        mini_bio = ''
        paras = response.xpath('//*[@id="mw-content-text"]/p[text() or ' \
                            'normalize-space(.)=""]').extract()

        for p in paras:
            if p == '<p></p>': # the bio-intros stop-point
                break
            mini_bio += p
        
        # correct for wiki-links
        mini_bio = mini_bio.replace('href="/wiki', 'href="' + BASE_URL + '/wiki')
        mini_bio = mini_bio.replace('href="#', item['link'] + '#')
        item['mini_bio'] = mini_bio
        yield item



