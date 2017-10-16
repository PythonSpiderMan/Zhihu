# -*- coding: utf-8 -*-

import json
import scrapy
from scrapy_redis.spiders import RedisSpider
from Zhihu.items import ZhihuItem, RelationItem



class ZhihuUserSpider(RedisSpider):

    name = 'zhihu_user'
    allowed_domains = ['www.zhihu.com']

    headers = {
        'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    }

    user_info_url = 'https://www.zhihu.com/api/v4/members/{}?include=locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    user_followees_url = 'https://www.zhihu.com/api/v4/members/{}/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'
    user_followers_url = 'https://www.zhihu.com/api/v4/members/{}/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'


    def start_requests(self):
        url_tokens = [
            'gejinyuban',       # 葛斤
            'zhang-jia-wei',    # 张佳玮
            'feifeimao',        # 肥肥猫
            'sizhuren',         # 寺主人
            'tang-que',         # 唐缺
            'cai-tong',         # 采铜
            'zhu-xuan-86',      # 朱炫
            'liangbianyao',     # 梁边妖
            'banfoxianren',     # 半佛仙人
            'xiepanda',         # 谢熊猫君
            'ma-qian-zu',       # 马前卒
            'mali',             # 马力
            'minmin.gong',      # 叛逆者
            'excited-vczh',     # 轮子哥
        ]

        return [scrapy.Request(
            self.user_info_url.format(url_token),
            headers=self.headers,
            priority=20,
            callback=self.user_parse,
        ) for url_token in url_tokens]



    def user_parse(self, response):
        """
        解析用户个人信息
        """
        infos = json.loads(response.body)
        url_token = infos['url_token']

        user_item = ZhihuItem()
        user_item['user'] = infos
        yield user_item

        # 判断关注和粉丝
        user_id = infos['id']    # 当前用户id

        # 请求关注的人
        following_count = infos['following_count']
        if following_count > 0:
            yield scrapy.Request(
                self.user_followees_url.format(url_token),
                headers=self.headers,
                priority=10,
                callback=self.following_parse,
                meta={
                    'children_user_id': user_id
                }
            )

        # 请求粉丝
        follower_count = infos['follower_count']
        if follower_count > 0:
            yield scrapy.Request(
                self.user_followers_url.format(url_token),
                headers=self.headers,
                priority=5,
                callback=self.followers_parse,
                meta={
                    'parent_user_id': user_id,
                }
            )


    def following_parse(self, response):
        """
        关注信息
        """
        children_user_id = response.meta['children_user_id']
        infos = json.loads(response.body)
        users = infos['data']
        # 请求关注的人的详细信息
        for user in users:
            url_token = user['url_token']

            rela_item = RelationItem()
            rela = {}
            rela['parent_user_id'] = user['id']
            rela['children_user_id'] = children_user_id
            rela_item['rela'] = rela
            yield rela_item

            yield scrapy.Request(
                self.user_info_url.format(url_token),
                headers=self.headers,
                callback=self.user_parse,
                priority=18,
            )

        # 翻页
        if not infos['paging']['is_end']:
            next_page = infos['paging']['next']
            yield scrapy.Request(
                next_page,
                headers=self.headers,
                priority=20,
                callback=self.following_parse,
                meta={'children_user_id': children_user_id}
            )


    def followers_parse(self, response):
        """
        粉丝信息
        """
        parent_user_id = response.meta['parent_user_id']
        infos = json.loads(response.body)
        users = infos['data']
        # 请求关注的人的详细信息
        for user in users:
            url_token = user['url_token']

            rela_item = RelationItem()
            rela = {}
            rela['parent_user_id'] = parent_user_id
            rela['children_user_id'] = user['id']
            rela_item['rela'] = rela
            yield rela_item

            yield scrapy.Request(
                self.user_info_url.format(url_token),
                headers=self.headers,
                priority=14,
                callback=self.user_parse,
            )

        # 翻页
        if not infos['paging']['is_end']:
            next_page = infos['paging']['next']
            yield scrapy.Request(
                next_page,
                headers=self.headers,
                priority=16,
                callback=self.followers_parse,
                meta={'parent_user_id': parent_user_id}
            )




