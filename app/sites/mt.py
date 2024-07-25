import base64
import json

from app.media.tmdbv3api.tmdb import logger
from app.utils import RequestUtils
from config import Config


class MtFunc(object):
    signin_url = "%s/api/member/updateLastBrowse"
    api_key_url = "%s/api/apikey/getKeyList"
    download_url = "%s/api/torrent/genDlToken"
    torrent_detail_url = "%s/api/torrent/detail"
    _site_name = None
    _site_api_key = None
    _site_cookie = None
    _site_url = None
    _site_ua = None
    _site_proxy = None

    def __init__(self, site_info):
        self._site_ua = site_info.get("ua") or Config().get_ua()
        self._site_api_key = site_info.get("apikey")
        self._site_cookie = site_info.get("cookie")
        self._site_proxy = site_info.get("proxy") or Config().get_proxies()
        self._site_url = site_info.get('strict_url')

    def signin(self):
        res = (RequestUtils(headers=self._site_ua, authorization=self._site_cookie
                            , proxies=self._site_proxy)
               .post_res(url=self.signin_url % self._site_url))
        if res.json()["code"] == "0":
            return True
        else:
            return False

    def update_api_key(self) -> tuple[bool, str]:
        """
        获取ApiKey
        """
        try:
            res = RequestUtils(headers={
                "Content-Type": "application/json",
                "User-Agent": f"{self._site_ua}"
            }, cookies=self._site_cookie, proxies=self._site_proxy, timeout=15, authorization=self._site_cookie,
                referer=f"{self._site_url}/usercp?tab=laboratory").post_res(url=self.api_key_url % self._site_url)
            if res and res.status_code == 200:
                api_keys = res.json().get('data')
                if api_keys:
                    logger.info(f"{self._site_name} 获取ApiKey成功")
                    # 按lastModifiedDate倒序排序
                    api_keys.sort(key=lambda x: x.get('lastModifiedDate'), reverse=True)
                    self._site_api_key = api_keys[0].get('apiKey')
                else:
                    __err_msg=res.json().get('message')
                    if __err_msg:
                        logger.warn(f"{self._site_name} {__err_msg}")
                        return False, "{__err_msg}"
                    else:
                        logger.warn(f"{self._site_name} 获取ApiKey失败，请先在`控制台`->`实验室`建立存取令牌")
                        return False, "获取ApiKey失败，请先在`控制台`->`实验室`建立存取令牌"
            else:
                logger.warn(f"{self._site_name} 获取ApiKey失败，请检查Cookie是否有效")
                return False, "获取ApiKey失败，请检查Cookie是否有效"
        except Exception as e:
            logger.error(f"{self._site_name} 获取ApiKey出错：{e}")
            return False, "获取ApiKey出错"
        return True, self._site_api_key

    def get_download_url(self, torrent_id: str) -> str:
        """
        获取下载链接，返回base64编码的json字符串及URL
        """
        url = self.download_url % self._site_url
        params = {
            'method': 'post',
            'cookie': False,
            'params': {
                'id': torrent_id
            },
            'header': {
                'Content-Type': 'application/json',
                'User-Agent': f'{self._site_ua}',
                'Accept': 'application/json, text/plain, */*',
                'x-api-key': self._site_api_key
            },
            'result': 'data'
        }
        # base64编码
        base64_str = base64.b64encode(json.dumps(params).encode('utf-8')).decode('utf-8')
        return f"[{base64_str}]{url}"

    def get_torrent_detail(self, torrent_id: str) -> str:
        """
        获取下载链接，返回base64编码的json字符串及URL
        """
        url = self.torrent_detail_url % self._site_url
        param = {'id': torrent_id}
        res = RequestUtils(
            authorization=self._site_cookie,
            apikey=self._site_api_key,
            ua=self._site_ua,
            proxies=self._site_proxy
        ).post_res(url=url, data=param)
        if res and res.status_code == 200:
            res.encoding = res.apparent_encoding
            return res.text
