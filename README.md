# content_merge

一种借助于代码托管来备份文件，同时有一定安全隐私诉求，且需要记录明文文本的变更历史，这里提供一种解决方案

## 使用方式

```bash
# 配置文件
echo > ./content_merge_conf <<EOF
zip_pwd {zip_pwd}
encrypt_key {encrypt_key}
origin ./0private_origin/
zipped ./0private_workspace/1zipped/
encrypted ./0private_completed/
decrypted ./0private_workspace/3decrypted/
restored ./0private_workspace/4restored/
EOF

uv run /path/to/script/main.py # 压缩并且解压
uv run /path/to/script/main.py -d # do_merge 压缩合并加密
uv run /path/to/script/main.py -u # un_merge 解密解压缩

```

## 实现方式

### 内容合并

1. 将特定文件夹（可以是一个 git 项目）整个打包压缩（分卷压缩以规避二进制文件的大小检测，可选使用密码）
1. 依次将压缩包加密（可选）
1. 上传加密后的文件

### 内容还原

1. 下载加密后的文件
1. 依次解密为压缩包
1. 将压缩包解压为文件夹

## 产物

总共需要或产生 5 个文件夹

- 原始内容，同时也是一个 git 项目
- 放置打包压缩后的分卷压缩包
- 压缩包加密后的内容，同时也是实际上传或下载的内容，文件内容放在另一个 git 项目中进行同步
- 放置解密后重新得到的分卷压缩包
- 解压后得到的原始内容

## 项目依赖管理

不使用 `.venv` （虽然为了开发调试还是加了），因为设想中的使用方式为任意位置执行 `uv run /path/to/script/main.py` ，脚本中根据当前路径下的配置去执行对应操作

因此优先使用 内联脚本元数据 (Inline Script Metadata) ，遵循 Python 社区的 PEP 723 标准
