# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from Zhihu.items import ZhihuItem, RelationItem
from Zhihu.database import session, UserInfo, Relation


class ZhihuPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, ZhihuItem):
            tmp_res = item['user']
            res = {}
            res['user_id'] = tmp_res['id']
            res['url_token'] = tmp_res['url_token']
            res['name'] = tmp_res['name']
            res['headline'] = tmp_res['headline']
            res['answer_count'] = tmp_res['answer_count']
            res['question_count'] = tmp_res['question_count']
            res['articles_count'] = tmp_res['articles_count']
            res['columns_count'] = tmp_res['columns_count']
            res['voteup_count'] = tmp_res['voteup_count']
            res['thanked_count'] = tmp_res['thanked_count']
            res['favorited_count'] = tmp_res['favorited_count']
            res['following_count'] = tmp_res['following_count']
            res['follower_count'] = tmp_res['follower_count']
            res['text'] = json.dumps(tmp_res)
            try:
                res['location'] = tmp_res['locations'][0]['name']
            except:
                res['location'] = None
            try:
                res['industry'] = tmp_res['business']['name']
            except:
                res['industry'] = None
            try:
                res['school'] = tmp_res['educations'][0]['school']['name']
            except:
                res['school'] = None
            try:
                res['major'] = tmp_res['educations'][0]['major']['name']
            except:
                res['major'] = None
            
            try:
                data = UserInfo(**res)
                session.add(data)
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()
            else:
                print('入库成功: %s'%tmp_res['id'])


        elif isinstance(item, RelationItem):
            try:
                data = Relation(**item['rela'])
                session.add(data)
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()

        return item
