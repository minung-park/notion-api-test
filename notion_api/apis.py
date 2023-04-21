import requests
from notion_api.errors import *
import pandas as pd
import logging


logging.basicConfig(
    format='%(asctime)s %(levelname)s %(lineno)3s: %(message)s',
    level=logging.INFO
)


class NotionApi:
    def __init__(self, auth=None):
        # self.auth = auth
        self.base_url = 'https://api.notion.com/v1'
        self.header = {
            'Notion-Version': '2022-06-28',
            'Authorization': f'Bearer {auth}'
        }
        self.item_type = {
            "paragraph": "paragraph",
            "heading_1": "heading_1",
            "heading_2": "heading_2",
            "heading_3": "heading_3",
            "bulleted_list_item": "bulleted_list_item",
            "numbered_list_item": "numbered_list_item",
            "to_do": "to_do",
            "toggle": "toggle",
            "child_page": "child_page",
            "child_database": "child_database",
            "embed": "embed",
            "image": "image",
            "video": "video",
            "file": "file",
            "pdf": "pdf",
            "bookmark": "bookmark",
            "callout": "callout",
            "quote": "quote",
            "equation": "equation",
            "divider": "divider",
            "table_of_contents": "table_of_contents",
            "column": "column",
            "column_list": "column_list",
            "link_preview": "link_preview",
            "synced_block": "synced_block",
            "template": "template",
            "link_to_page": "link_to_page",
            "table": "table",
            "table_row": "table_row",
            "unsupported": "unsupported"
        }
        self.prop_type = {
            "title": "title",
            "rich_text": "rich_text",
            "number": "number",
            "select": "select",
            "multi_select": "multi_select",
            "date": "date",
            "people": "people",
            "files": "files",
            "checkbox": "checkbox",
            "url": "url",
            "email": "email",
            "phone_number": "phone_number",
            "formula": "formula",
            "relation": "relation",
            "rollup": "rollup",
            "created_time": "created_time",
            "created_by": "created_by",
            "last_edited_time": "last_edited_time",
            "last_edited_by": "last_edited_by",
            "status": "status"
        }

    def get_all_items(self, _id=None, item_type=None):
        try:
            if not _id:
                raise RequiredParamNull

            url = f'{self.base_url}/blocks/{_id}/children'
            resp = requests.get(url=url, headers=self.header)
            resp_data = resp.json()
            if resp.status_code != 200:
                raise ApiError(f'{resp_data.get("code")}: {resp_data.get("message")}')

            results = resp_data.get('results')
            if item_type and self.item_type.get(item_type):
                results = list(filter(lambda x: x.get('type') == item_type, results))

            return results

        except RequiredParamNull as e:
            logging.error(e)
        except ApiError as e:
            logging.error(e)

    def get_databases(self, _id=None):
        try:
            if not _id:
                raise RequiredParamNull

            url = f'{self.base_url}/databases/{_id}'
            resp = requests.get(url=url, headers=self.header)
            resp_data = resp.json()
            if resp.status_code != 200:
                raise ApiError(f'{resp_data.get("code")}: {resp_data.get("message")}')

            return resp_data

        except RequiredParamNull as e:
            logging.error(e)
        except ApiError as e:
            logging.error(e)

    def get_db_obj_ids(self, _id=None):
        try:
            if not _id:
                raise RequiredParamNull

            url = f'{self.base_url}/databases/{_id}/query'
            resp = requests.post(url=url, headers=self.header,
                                 data={
                                     "sorts": [{
                                         "property": "created_time",
                                         "direction": "ascending"
                                     }]
                                 })

            resp_data = resp.json()
            if resp.status_code != 200:
                raise ApiError(f'{resp_data.get("code")}: {resp_data.get("message")}')

            results = resp_data.get('results')
            obj_page_ids = list(map(lambda x: x.get('id'), results))
            return obj_page_ids

        except RequiredParamNull as e:
            logging.error(e)
        except ApiError as e:
            logging.error(e)

    def get_property_value(self, page_id=None, prop_id=None):
        try:
            if not page_id or not prop_id:
                raise RequiredParamNull

            url = f'{self.base_url}/pages/{page_id}/properties/{prop_id}'
            resp = requests.get(url=url, headers=self.header)
            resp_data = resp.json()
            if resp.status_code != 200:
                raise ApiError(f'{resp_data.get("code")}: {resp_data.get("message")}')

            return resp_data

        except RequiredParamNull as e:
            logging.error(e)
        except ApiError as e:
            logging.error(e)

    def get_user_info(self, _id=None, info_type=None):
        try:
            if not _id:
                raise RequiredParamNull

            url = f'{self.base_url}/users/{_id}'
            resp = requests.get(url=url, headers=self.header)
            resp_data = resp.json()
            if resp.status_code != 200:
                raise ApiError(f'{resp_data.get("code")}: {resp_data.get("message")}')

            if info_type == 'name':
                return resp_data.get(info_type)
            elif info_type == 'email':
                _p = resp_data.get('person')
                return _p.get('email') if _p else None

            return resp_data

        except RequiredParamNull as e:
            logging.error(e)
        except ApiError as e:
            logging.error(e)

    def return_prop_val(self, prop_item):
        logging.debug(prop_item)
        try:
            val = None
            prop_type = prop_item.get('type')
            if prop_type != 'checkbox' and not prop_item.get(prop_type):
                return None

            if prop_type == 'multi_select':
                val = ', '.join(list(map(lambda x: x['name'], prop_item.get(prop_type))))
            elif prop_type == 'select' or prop_type == 'status':
                val = prop_item[prop_type]['name']
            elif prop_type == 'rich_text' or prop_type == 'title':
                val = prop_item[prop_type]['text']['content']
            elif prop_type == 'date':
                val = prop_item[prop_type]['start']
            elif prop_type == 'formula':
                f_type = prop_item[prop_type]['type']
                val = prop_item[prop_type][f_type]
            elif prop_type == 'people':
                val = self.get_user_info(prop_item[prop_type]['id'], info_type='name')
            else:
                val = prop_item[prop_type]
        except Exception as e:
            logging.error(e)
            logging.error(prop_item)
        finally:
            return val

    def convert_db_to_df(self, _id=None):
        try:
            df_list = []
            databases = self.get_all_items(_id, item_type='child_database')
            db_ids = list(map(lambda x: x['id'], databases))

            for did in db_ids:
                db_data = self.get_databases(did)
                columns = db_data.get('properties').keys()
                idx_key = list(filter(lambda x: db_data['properties'][x]['id'] == 'title', columns))[0]
                obj_page_ids = self.get_db_obj_ids(did)

                df_data = []
                for obj_p_id in obj_page_ids:
                    obj = {}
                    for c in columns:
                        prop_id = db_data['properties'][c]['id']
                        _d = self.get_property_value(page_id=obj_p_id, prop_id=prop_id)
                        obj_type = _d.get('object')
                        if obj_type == 'list':
                            _d_list = _d.get('results')
                            _v_list = []
                            for _d in _d_list:
                                _v = self.return_prop_val(prop_item=_d) if _d else None
                                _v_list.append(_v)
                            obj[c] = ' '.join(_v_list)
                        else:
                            _v = self.return_prop_val(prop_item=_d) if _d else None
                            obj[c] = _v

                    df_data.append(obj)
                df = pd.DataFrame(df_data, index=list(map(lambda x: x.get(idx_key), df_data)))
                df_list.append(df)

        except Exception as e:
            logging.error(e)
            logging.error(_id)
        finally:
            return df_list
