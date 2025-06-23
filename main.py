import logging
import argparse
import common_base, common_encrypt, common_zip


LOG = logging.getLogger()


def do_action(do_merge: bool):
    conf = common_base.load_config()
    util_zip = common_zip.ContentZipper.from_conf(do_merge, conf)
    util_encrypter = common_encrypt.ContentEncrypter.from_conf(do_merge, conf)

    if do_merge:
        util_zip.do_action()
        util_encrypter.do_action_loop()
    else:
        util_encrypter.do_action_loop()
        util_zip.do_action()


def do_action_without_encrypt(do_merge: bool):
    conf = common_base.load_config()
    util_zip = common_zip.ContentZipper.from_conf(do_merge, conf)

    if do_merge:
        util_zip.target_folder = conf.encrypted
        util_zip.do_action()
    else:
        util_zip.source_folder = conf.encrypted
        util_zip.do_action()


def main():
    common_base.init_logging()

    # parse the args
    parser = argparse.ArgumentParser(
        description="do_merge or un_merge action, will do both actions if has no action given."
    )
    parser.add_argument(
        "-d",
        action="store_true",  # 默认 false
        help="merge everything",
    )
    parser.add_argument(
        "-u",
        action="store_true",  # 默认 false
        help="unmerge all",
    )

    args = parser.parse_args()
    do_merge = args.d
    un_merge = args.u

    if not do_merge and not un_merge:
        LOG.info("will do do_merge and do un_merge both, if you want to do one of them, use args '-d' or '-u'")
        do_action(True)
        do_action(False)
    else:
        if do_merge:
            do_action(True)
        if un_merge:
            do_action(False)

    # do_action_without_encrypt(True)
    # do_action_without_encrypt(False)


if __name__ == "__main__":
    main()
