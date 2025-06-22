import logging
import os
import shutil


LOG = logging.getLogger()


def init_logging():
    logging.basicConfig(
        format="%(asctime)s [%(name)s::%(levelname)s] %(message)s",
        level=logging.INFO,
    )


class Config:
    defaule_encrypt_key = b"0Ooq0QoCDoO0Oo0q"

    def __init__(self) -> None:
        self.zip_pwd = ""
        self.encrypt_key = self.defaule_encrypt_key
        self.origin = ""
        self.zipped = ""
        self.encrypted = ""
        self.decrypted = ""
        self.restored = ""

    def set_attr(self, key: str, value: str) -> None:
        if key == "encrypt_key":
            self.encrypt_key = value.encode("utf-8")
            return
        if key in self.__dict__:
            setattr(self, key, value)


def load_config() -> Config:
    config = Config()
    with open("./content_merge_conf", "r", encoding="utf-8") as f:
        for line in f.readlines():
            [key, value] = line.split()
            config.set_attr(key, value)
    return config


def init_workspace(source_folder, target_folder):
    """
    检查 source 文件夹
    重置 target 文件夹
    """

    folder_path = source_folder
    LOG.info("check folder: %s", folder_path)

    if not os.path.exists(folder_path):
        raise Exception(f"{folder_path} not exists")
    if not os.path.isdir(folder_path):
        raise Exception(f"{folder_path} not folder")

    folder_path = target_folder
    LOG.info("ensure folder: %s", folder_path)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

        if not os.path.exists(folder_path):
            raise Exception(f"{folder_path} makedirs failed")
        return

    if not os.path.isdir(folder_path):
        raise Exception(f"{folder_path} not folder")
    
    if not os.listdir(folder_path):
        return

    LOG.info("empty the folder: %s", folder_path)
    shutil.rmtree(folder_path)
    os.makedirs(folder_path)

    if not os.path.exists(folder_path):
        raise Exception(f"{folder_path} makedirs failed")
    if os.listdir(folder_path):
        raise Exception(f"{folder_path} not empty")
