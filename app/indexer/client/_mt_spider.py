import base64
import json
import re
from typing import Tuple, List

from ruamel.yaml import CommentedMap

from app.conf import SystemConfig
from app.media.tmdbv3api.tmdb import logger
from app.utils import StringUtils, RequestUtils
from app.utils.types import MediaType
from config import Config


class MTorrentSpider:
    """
    mTorrent API，需要缓存ApiKey
    """
    _indexerid = None
    _systemconfig = None
    _domain = None
    _name = ""
    _proxy = None
    _cookie = None
    _ua = None
    _size = 100
    _searchurl = "%sapi/torrent/search"
    _downloadurl = "%sapi/torrent/genDlToken"
    _pageurl = "%sdetail/%s"

    # 电影分类
    _movie_category = ['401', '419', '420', '421', '439', '405', '404']
    _tv_category = ['403', '402', '435', '438', '404', '405']

    # API KEY
    _apikey = None

    # 标签
    _labels = {
        "0": "",
        "1": "DIY",
        "2": "国配",
        "3": "DIY 国配",
        "4": "中字",
        "5": "DIY 中字",
        "6": "国配 中字",
        "7": "DIY 国配 中字"
    }

    def __init__(self, indexer):
        if indexer:
            self._indexerid = indexer.id
            self._domain = indexer.domain
            self._searchurl = self._searchurl % self._domain
            self._name = indexer.name
            if indexer.proxy:
                self._proxy = indexer.proxy
            self._cookie = indexer.cookie
            self._ua = indexer.ua or Config().get_ua()
            self.systemconfig = SystemConfig()

    def __get_apikey(self) -> str:
        """
        获取ApiKey
        """
        domain_host = StringUtils.get_url_host(self._domain)
        self._apikey = self.systemconfig.get(f"site.{domain_host}.apikey")
        if not self._apikey:
            try:
                res = RequestUtils(
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": f"{self._ua}"
                    },
                    cookies=self._cookie,
                    proxies=self._proxy,
                    referer=f"{self._domain}usercp?tab=laboratory",
                    timeout=15
                ).post_res(url=f"{self._domain}api/apikey/getKeyList")
                if res and res.status_code == 200:
                    api_keys = res.json().get('data')
                    if api_keys:
                        logger.info(f"{self._name} 获取ApiKey成功")
                        # 按lastModifiedDate倒序排序
                        api_keys.sort(key=lambda x: x.get('lastModifiedDate'), reverse=True)
                        self._apikey = api_keys[0].get('apiKey')
                        self.systemconfig.set(f"site.{domain_host}.apikey", self._apikey)
                    else:
                        logger.warn(f"{self._name} 获取ApiKey失败，请先在`控制台`->`实验室`建立存取令牌")
                else:
                    logger.warn(f"{self._name} 获取ApiKey失败，请检查Cookie是否有效")
            except Exception as e:
                logger.error(f"{self._name} 获取ApiKey出错：{e}")
        return self._apikey

    def search(self, keyword: str, mtype: MediaType = None, page: int = 0) -> Tuple[bool, List[dict]]:
        """
        搜索
        """
        # 检查ApiKey
        self.__get_apikey()

        if not self._apikey:
            return True, []

        if not mtype:
            categories = []
        elif mtype == MediaType.TV:
            categories = self._tv_category
        else:
            categories = self._movie_category
        params = {
            "keyword": keyword,
            "categories": categories,
            "pageNumber": int(page) + 1,
            "pageSize": self._size,
            "visible": 1
        }
        res = RequestUtils(
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"{self._ua}",
                "x-api-key": self._apikey
            },
            proxies=self._proxy,
            referer=f"{self._domain}browse",
            timeout=15
        ).post_res(url=self._searchurl, json=params)
        torrents = []
        if res and res.status_code == 200:
            if len(res.json().get('data', {})) == 0:
                return True, []
            results = res.json().get('data', {}).get("data") or []
            for result in results:
                category_value = result.get('category')
                if category_value in self._tv_category \
                        and category_value not in self._movie_category:
                    category = MediaType.TV.value
                elif category_value in self._movie_category:
                    category = MediaType.MOVIE.value
                else:
                    category = MediaType.UNKNOWN.value
                labels = self._labels.get(result.get('labels') or "0") or ""

                torrent = {
                    'title': result.get('name'),
                    'description': result.get('smallDescr'),
                    'enclosure': self.__get_download_url(result.get('id')),
                    'pubdate': result.get('createdDate'),
                    'size': int(result.get('size') or '0'),
                    'seeders': int(result.get('status', {}).get("seeders") or '0'),
                    'peers': int(result.get('status', {}).get("leechers") or '0'),
                    'grabs': int(result.get('status', {}).get("timesCompleted") or '0'),
                    'downloadvolumefactor': self.__get_downloadvolumefactor(result.get('status', {}).get("discount")),
                    'uploadvolumefactor': self.__get_uploadvolumefactor(result.get('status', {}).get("discount")),
                    'page_url': self._pageurl % (self._domain, result.get('id')),
                    'imdbid': self.__find_imdbid(result.get('imdb')),
                    'labels': labels,
                    'category': category
                }
                torrents.append(torrent)
        elif res is not None:
            logger.warn(f"{self._name} 搜索失败，错误码：{res.status_code}")
            return True, []
        else:
            logger.warn(f"{self._name} 搜索失败，无法连接 {self._domain}")
            return True, []
        return False, torrents

    @staticmethod
    def __find_imdbid(imdb: str) -> str:
        """
        从imdb链接中提取imdbid
        """
        if imdb:
            m = re.search(r"tt\d+", imdb)
            if m:
                return m.group(0)
        return ""

    @staticmethod
    def __get_downloadvolumefactor(discount: str) -> float:
        """
        获取下载系数
        """
        discount_dict = {
            "FREE": 0,
            "PERCENT_50": 0.5,
            "PERCENT_70": 0.3,
            "_2X_FREE": 0,
            "_2X_PERCENT_50": 0.5
        }
        if discount:
            return discount_dict.get(discount, 1)
        return 1

    @staticmethod
    def __get_uploadvolumefactor(discount: str) -> float:
        """
        获取上传系数
        """
        uploadvolumefactor_dict = {
            "_2X": 2.0,
            "_2X_FREE": 2.0,
            "_2X_PERCENT_50": 2.0
        }
        if discount:
            return uploadvolumefactor_dict.get(discount, 1)
        return 1

    def __get_download_url(self, torrent_id: str) -> str:
        """
        获取下载链接，返回base64编码的json字符串及URL
        """
        url = self._downloadurl % self._domain
        params = {
            'method': 'post',
            'cookie': False,
            'params': {
                'id': torrent_id
            },
            'header': {
                'Content-Type': 'application/json',
                'User-Agent': f'{self._ua}',
                'Accept': 'application/json, text/plain, */*',
                'x-api-key': self._apikey
            },
            'result': 'data'
        }
        # base64编码
        base64_str = base64.b64encode(json.dumps(params).encode('utf-8')).decode('utf-8')
        return f"[{base64_str}]{url}"