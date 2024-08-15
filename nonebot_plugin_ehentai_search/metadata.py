import random
from io import BytesIO
from datetime import datetime
import time
from bs4 import BeautifulSoup

class MetaData:
    def __init__(self):
        pass

    def change_pixel(self, image, quality: int) -> bytes:
        """
        图像镜像左右翻转, 并且随机修改左上角一个像素点
        """
        image = image.convert("RGB")
        image.load()[0, 0] = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        byte_data = BytesIO()
        image.save(byte_data, format="JPEG", quality=quality)
        return byte_data.getvalue()

    def get_id_token_from_url(self, url: str) -> tuple:
        return (int(url.split("/")[4]), url.split("/")[5])

    def get_next_id(self, resp_page: BeautifulSoup) -> int:
        scripts = resp_page.find_all("script", type="text/javascript")
        for tag in scripts:
            if len(tag.contents) == 0:
                continue
            if "var nexturl" in tag.contents[0]:
                for line in tag.contents[0].split("\n"):
                    if "var nexturl" in line:
                        next_id = line.split("=")[2][:-2]
                        return int(next_id)
        return -1

    def is_gallery_entry(self, entry_tag) -> bool:
        # subtag example:
        # <tr>
        #   <td class="gl1c glcat">
        if entry_tag.name != "tr":
            return False
        if len(entry_tag.contents) == 0:
            return False
        td_tag = entry_tag.contents[0]
        if td_tag.name != "td":
            return False
        if not td_tag.has_attr("class"):
            return False
        clss = td_tag.get("class")
        if not ("gl1c" in clss and "glcat" in clss):
            return False
        return True

    def is_posted_entry(self, entry_tag) -> bool:
        if not entry_tag.has_attr("id"):
            return False
        if "posted" not in entry_tag.get("id"):
            return False
        return True

    def parse_entry(self, resp_tag) -> dict:
        # get type, located in the first div inside td
        # structure:
        # <tr> <td> <div> category
        # gl1c
        category = resp_tag.contents[0].contents[0].contents[0]
        # gl2c
        td2 = resp_tag.contents[1]
        # prioritize data-src
        img_tag = td2.find("img")
        if img_tag.has_attr("data-src"):
            thumbnail = img_tag.get("data-src")
        else:
            thumbnail = img_tag.get("src")

        timestamp_string = td2.find(self.is_posted_entry).contents[0]
        format_string = "%Y-%m-%d %H:%M"
        datetime_object = datetime.strptime(timestamp_string, format_string)
        posted = int(time.mktime(datetime_object.timetuple()))
        # gl3c
        td3 = resp_tag.contents[2]
        url = td3.find("a").get("href")
        gid, token = self.get_id_token_from_url(url)
        # name
        entry_title = td3.find("a").contents[0].contents[0]
        # tags
        tags_tag = td3.find("a").contents[1]
        tags = []
        if not len(tags_tag.find_all("div")) == 0:
            for tag_element in tags_tag.children:
                tags.append(tag_element.get("title"))
        # gl4c
        td4 = resp_tag.contents[3]
        try:
            uploader = td4.find("a").contents[0]
        except AttributeError:
            uploader = "Unknown"
        pages = td4.contents[1].contents[0].split(" ")[0]
        return {
            "gid": gid,
            "token": token,
            "title": entry_title,
            "category": category,
            "thumb": thumbnail,
            "uploader": uploader,
            "posted": posted,
            "filecount": pages,
            "tags": tags,
        }

    def get_metadata(self, resp_page: BeautifulSoup, limit_num: int):
        entries = resp_page.find_all(self.is_gallery_entry)
        count = 0
        res = []
        for entry in entries:
            if count == limit_num:
                break
            res.append(self.parse_entry(entry))
            count += 1
        return res

# 使用示例
metadata = MetaData()