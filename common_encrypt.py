import os
import logging
import common_base

from Crypto.Cipher import AES


LOG = logging.getLogger()


def encrypt(ss: bytes, key: bytes):
    # 防止最后一位恰好为0 手动加上1
    ln = AES.block_size - (len(ss) + 1) % AES.block_size
    ss = ss + b"\1" + ln * b"\0"  # 补全长度 16 的倍数

    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(ss)


def decrypt(bb: bytes, key: bytes):
    cipher = AES.new(key, AES.MODE_ECB)
    msg = cipher.decrypt(bb)

    return msg.rstrip(b"\0")[:-1]


class ContentEncrypter(object):
    """
    内容加解密工具
    """

    @classmethod
    def from_conf(cls, encrypt: bool, conf: common_base.Config):
        ce = ContentEncrypter(encrypt)
        if encrypt:
            ce.source_folder = conf.zipped
            ce.target_folder = conf.encrypted
        else:
            ce.source_folder = conf.encrypted
            ce.target_folder = conf.decrypted

        ce.set_encrypt_key(conf.encrypt_key)
        return ce

    def __init__(self, encrypt: bool, **kwargs) -> None:
        self.encrypt = encrypt
        self.source_folder = kwargs.get(
            "source_folder", "./test_workspace/source_folder/"
        )
        self.target_folder = kwargs.get(
            "target_folder", "./test_workspace/target_folder/"
        )
        self.encrypt_key = common_base.Config.defaule_encrypt_key

    def set_encrypt_key(self, encrypt_key: bytes):
        """
        加载密钥
        """
        if len(encrypt_key) != 16:
            raise Exception("len of encrypt_key must be 16")

        self.encrypt_key = encrypt_key

    def init_workspace(self):
        """
        检查 source 文件夹
        重置 target 文件夹
        """
        common_base.init_workspace(self.source_folder, self.target_folder)

    def source_files_loop(self):
        """
        获取 source 目录下的所有文件 不支持子文件夹内的文件

        Returns:
            Generator for (file_name, source_path, target_path)
        """
        for file in os.listdir(self.source_folder):
            if os.path.isfile(os.path.join(self.source_folder, file)):
                yield (
                    file,  # file name
                    os.path.join(self.source_folder, file),  # source path
                    os.path.join(self.target_folder, file),  # target path
                )
            else:
                LOG.warning("the source is not file: %s", file)
                continue

    def do_action_once(self, source: str, target: str):
        """
        进行加解密动作生成 target 文件
        """
        LOG.info(">>>>>>>>> %s", source)
        try:
            with open(source, "rb") as sf, open(target, "wb") as tf:
                if self.encrypt:
                    bts = encrypt(sf.read(), self.encrypt_key)
                else:
                    bts = decrypt(sf.read(), self.encrypt_key)
                tf.write(bts)
        except Exception as e:
            LOG.exception("action exception: %s", e)
        LOG.info("<<<<<<<<< %s", target)

    def do_action_loop(self):
        """
        对所有 source 中的文件做加解密动作
        """
        self.init_workspace()
        for file_info in self.source_files_loop():
            self.do_action_once(file_info[1], file_info[2])


def test_main():
    common_base.init_logging()

    config = common_base.load_config()

    ce = ContentEncrypter.from_conf(True, config)
    ce.source_folder = config.origin  # hook
    ce.do_action_loop()
    LOG.info("encrypted")

    ce = ContentEncrypter.from_conf(False, config)
    ce.do_action_loop()
    LOG.info("decrypted")


def test():
    msg = "1234500000"
    if msg[-5:] == 5 * "0":
        print("yes", msg[:-5])
    else:
        print("no!!!")

    if msg[-0:] == 0 * "0":
        print("yes")
    else:
        print("no!!!", msg[-0:])


if __name__ == "__main__":
    # test()

    test_main()
