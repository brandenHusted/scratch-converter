import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
import os
from time import time


class File:
    def __init__(self, content=None):
        self.content = content

    def save(self, path):
        if not self.content:
            return False
        with open(path, "wb") as f:
            f.write(self.content)
        return True


class ScratchDownloader:
    def __init__(
        self,
        download_directory: str,
        show_browser: bool = False
    ) -> None:
        cur_path = os.path.abspath(__file__)
        cur_dir = os.path.dirname(cur_path)
        self.chrome_driver_path = os.path.join(cur_dir, "public/chromedriver")
        self.show_browser = show_browser
        self.download_directory = download_directory
        self.link = ""
        self.fn = ""

    def download(self, link: str) -> bool:
        self.fn = str(time())
        self.link = link

        if not self.__check_url():
            print("Invalid link")
            return False
        driver = self.__init_webdriver()

        status = self.__download(driver)

        driver.quit()
        self.link = ""
        return status

    def get_sb3(self, link: str) -> File:
        if not self.download(link):
            return File()
        path = os.listdir(f"{self.download_directory}/{self.fn}")[0]
        path = os.path.join(f"{self.download_directory}/{self.fn}", path)
        with open(path, "rb") as f:
            sb3 = f.read()

        os.remove(path)
        os.rmdir(f"{self.download_directory}/{self.fn}")

        return File(sb3)

    def __download(self, driver: Chrome) -> bool:
        try:
            driver.get(self.link)

            fileBtn = driver.find_element(
                By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[1]/div[3]')
            fileBtn.click()

            saveBtn = driver.find_element(
                By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[1]/div[3]/div/ul/li[3]')
            saveBtn.click()

            return self.__download_status()
        except Exception as e:
            """
            TODO: might sending a warning email here
            """
            print(e.args)
            return False

    def __check_url(self):
        """
        a valid url should be something like this

        https://scratch.mit.edu/projects/848079571/editor/
        """
        self.link = self.link.strip()
        if not self.link.endswith("/"):
            self.link += "/"
        if not self.link.endswith("editor/"):
            self.link += "editor/"
        pattern = r"https://scratch.mit.edu/projects/\d+/editor/"
        match = re.match(pattern, self.link)
        return match is not None

    def __download_status(self) -> bool:
        """
        if download cost more than 5secs, means failure
        """
        s = time()
        while (time() - s) < 5:
            try:
                if len(os.listdir(f"{self.download_directory}/{self.fn}")) != 0:
                    return True
            except:
                ...
        return False

    def __init_webdriver(self) -> Chrome:
        chrome_options = webdriver.ChromeOptions()
        if not self.show_browser:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": f"{self.download_directory}/{self.fn}"
        })

        service = Service(self.chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)

        return driver


if __name__ == "__main__":
    sd = ScratchDownloader("/tmp/scratch")
    content = sd.get_sb3("https://scratch.mit.edu/projects/847425365/")
    content.save("a.sb3")
