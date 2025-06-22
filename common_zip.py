import os
import logging
import subprocess

import common_base

LOG = logging.getLogger()


def zip(source_folder: str, target_folder: str, archive_name: str, pwd=""):
    """
    将 source_folder 下所有文件进行分卷打包压缩（不包括文件夹） 分卷压缩文件放置到 target_folder
    """

    source_path = os.path.abspath(os.path.join(source_folder, "*"))
    target_path = os.path.abspath(os.path.join(target_folder, archive_name))

    LOG.info(
        "zip >>>>>>>>>>>>>>>>>>>>>>>>>>> start from %s to %s",
        source_path,
        target_path,
    )

    # 分卷大小 35M 一般超过 50 MiB 时会警告 超过 100 MiB 时会阻止 必须使用 Git LFS 来管理
    # powershell> 7z a -v35m .\0_1_zipped\archive_volumes.zip .\0_0_origin\*
    # output: .\0_1_zipped\archive_volumes.zip.001
    cmd = [
        "7z",
        "a",
        "-v35m",
        target_path,
        source_path,
    ]
    if pwd:
        cmd.append(f"-p{pwd}")
    subprocess.run(
        cmd,
        check=True,
    )

    LOG.info("zip <<<<<<<<<<<<<<<<<<<<<<<<<<< finish")


def unzip(source_folder: str, target_folder: str, archive_name: str, pwd=""):
    """
    将 source_folder 下的分卷压缩文件解压到 target_folder
    """

    source_path = os.path.abspath(os.path.join(source_folder, archive_name))
    target_path = os.path.abspath(target_folder)

    LOG.info(
        "unzip >>>>>>>>>>>>>>>>>>>>>>>>>>> start from %s to %s",
        source_path,
        target_path,
    )

    # -ao{a|s|t|u} : set Overwrite mode
    #     a (A)lways 直接覆盖现有文件
    #     s (S)kip all 跳过所有重复文件
    #     u A(u)to rename all 自动重命名新文件
    #     t 自动重命名旧文件
    # powershell> 7z x .\0_1_zipped\archive_volumes.zip.001 -aoa -o".\0_4_restored\"
    cmd = [
        "7z",
        "x",
        source_path,
        "-aoa",  # 若重复则强制覆盖解压后的文件
        f"-o{target_path}",
    ]
    if pwd:
        cmd.append(f"-p{pwd}")
    subprocess.run(
        cmd,
        check=True,
    )

    LOG.info("unzip <<<<<<<<<<<<<<<<<<<<<<<<<<< finish")


class ContentZipper(object):
    """
    内容打包压缩工具
    """

    default_archive_filename = "archive_volumes.zip"
    default_archive_filename_unzip = default_archive_filename + ".001"

    @classmethod
    def from_conf(cls, zip: bool, conf: common_base.Config):
        cz = ContentZipper(zip)
        if zip:
            cz.source_folder = conf.origin
            cz.target_folder = conf.zipped
        else:
            cz.source_folder = conf.decrypted
            cz.target_folder = conf.restored

        cz.zip_pwd = conf.zip_pwd
        return cz

    def __init__(self, zip: bool, **kwargs) -> None:
        self.zip_pwd = ""
        self.zip = zip
        self.source_folder = kwargs.get(
            "source_folder", "./test_workspace/source_folder/"
        )
        self.target_folder = kwargs.get(
            "target_folder", "./test_workspace/target_folder/"
        )
        self.archive_filename = self.default_archive_filename
        self.archive_filename_unzip = self.default_archive_filename_unzip

    def init_workspace(self):
        """
        检查 source 文件夹
        重置 target 文件夹
        """
        common_base.init_workspace(self.source_folder, self.target_folder)

    def do_action(self):
        self.init_workspace()
        if self.zip:
            zip(
                self.source_folder,
                self.target_folder,
                self.archive_filename,
                pwd=self.zip_pwd,
            )
        else:
            unzip(
                self.source_folder,
                self.target_folder,
                self.archive_filename_unzip,
                pwd=self.zip_pwd,
            )


def test_main():
    common_base.init_logging()

    # 重复执行会报错 因为已存在压缩包
    # zip(
    #     os.path.abspath("./test_workspace/0_0_origin"),
    #     os.path.abspath("./test_workspace/0_1_zipped"),
    #     "archive_volumes.zip",
    # )

    # unzip(
    #     os.path.abspath("./test_workspace/0_1_zipped"),
    #     os.path.abspath("./test_workspace/0_4_restored"),
    #     "archive_volumes.zip.001",
    # )

    config = common_base.load_config()

    czip = ContentZipper.from_conf(True, config)
    czip.do_action()

    cunzip = ContentZipper.from_conf(False, config)
    cunzip.source_folder = czip.target_folder  # hook
    cunzip.do_action()


if __name__ == "__main__":
    test_main()
