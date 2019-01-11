#!/usr/bin/python
# -*-coding:utf-8-*-
import config360
import os
import sys
import json
import platform
import shutil

##########################################################
# 整个流程分为3步：1获取基本配置信息 2使用360加固apk 3使用walle打多渠道包
# 其中第一步需要 两个输入参数，在调用py文件的时候需要传入
# 第一个参数是 APK文件地址 例如 d:/lingsir.apk
# 第二个参数是apk的签名配置信息在sign.json中的命名 例如 lingsir
##########################################################


##########################################################
# 第一步 从输入和json文件读取基本信息
##########################################################

# 判断当前系统
def isWindows():
    sysstr = platform.system()
    if("Windows" in sysstr):
        return 1
    else:
        return 0


# 兼容不同系统的路径分隔符
def getBackslash():
    if(isWindows() == 1):
        return "\\"
    else:
        return "/"


# 获取脚本文件的当前路径
def curFileDir():
    # 获取脚本路径
    path = sys.path[0]
    # 判断为脚本文件还是py2exe编译后的文件，
    # 如果是脚本文件，则返回的是脚本的目录，
    # 如果是编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


# 第一个输入的参数作为需要加固的apk的地址
JIAGU_APK_PATH = sys.argv[1]

# 第二个输入的参数作为需要加固的apk的签名名字，从sign.json文件获取 ，例如 lingsir
signName = sys.argv[2]

# 输出文件的路径为输入文件同目录
JIAGU_APK_PARENT_PATH = os.path.dirname(JIAGU_APK_PATH)
# 当前脚本文件所在目录
SCRIPT_PARENT_PATH = curFileDir()

# 从json里面获取获取签名key的信息
signJson = open(SCRIPT_PARENT_PATH+getBackslash()+"sign.json", "r")
signDict = json.load(signJson)
signJson.close()
# 签名jks的位置
KEY_STORE_PATH = signDict[signName]["keyStore"]
# 签名的alias
KEY_ALIAS = signDict[signName]["alias"]
# 签名的密码
KEY_PASSWORD = signDict[signName]["keyPassword"]
# 别名的密码
KEY_ALIAS_PASSWORD = signDict[signName]["aliasPassword"]
# buildToolVersion
BUILD_TOOL_PATH = os.environ["ANDROID_HOME"] + \
    getBackslash() + "build-tools"+getBackslash() + \
    signDict[signName]["buildToolVersion"]


#######################################################
# 第二步 360加固，需要使用360加固然后才可以打多渠道包
#######################################################


# 360加固jar的位置
# JIAGU360_HOME = os.environ["JIAGU360_HOME"]
JIAGU360_HOME = ""
if isWindows():
    JIAGU360_HOME = SCRIPT_PARENT_PATH+getBackslash()+"lib"+getBackslash() + \
        "jiaguWindows"+getBackslash()
else:
    JIAGU360_HOME = SCRIPT_PARENT_PATH+getBackslash()+"lib"+getBackslash() + \
        "jiaguLinux"+getBackslash()

# 360加固的账号
JIAGU_USERNAME = config360.USERNAME
# 360加固的账号密码
JIAGU_PASSWORD = config360.USERPASEEWORD

# 登录360账号
loginCommd = "java -jar "+JIAGU360_HOME + \
    "jiagu.jar -login "+JIAGU_USERNAME+" "+JIAGU_PASSWORD
os.system(loginCommd)

# 配置签名信息
signCommd = "java -jar "+JIAGU360_HOME+"jiagu.jar -importsign " + \
    KEY_STORE_PATH+" "+KEY_PASSWORD+" "+KEY_ALIAS+" "+KEY_ALIAS_PASSWORD
os.system(signCommd)

# 加固选项
configCommd = "java -jar "+JIAGU360_HOME+"jiagu.jar -config -update -x86"
os.system(configCommd)


# 加固
jiaguCommd = "java -jar "+JIAGU360_HOME + \
    "\jiagu.jar -jiagu "+JIAGU_APK_PATH+" "+JIAGU_APK_PARENT_PATH
os.system(jiaguCommd)

print("******↓↓↓↓↓↓↓↓↓360加固完成，输出路径在下面的地址↓↓↓↓↓↓↓↓↓******\n")
print(JIAGU_APK_PARENT_PATH+"\n")
print("******↑↑↑↑↑↑↑↑↑360加固完成，输出路径在上面的地址↑↑↑↑↑↑↑↑↑******\n")


####################################################################
# 第三步 将加固之后的apk进行多渠道打包
####################################################################


# 清空临时资源
def cleanTempResource():
    try:
        os.remove(zipalignedApkPath)
        os.remove(signedApkPath)
        pass
    except Exception:
        pass

# 清空渠道信息


def cleanChannelsFiles():
    try:
        os.makedirs(channelsOutputFilePath)
        pass
    except Exception:
        pass

# 创建Channels输出文件夹


def createChannelsDir():
    try:
        os.makedirs(channelsOutputFilePath)
        pass
    except Exception:
        pass


# config
checkAndroidV2SignaturePath = SCRIPT_PARENT_PATH + getBackslash() + \
    "lib"+getBackslash() + "CheckAndroidV2Signature.jar"
walleChannelWritterPath = SCRIPT_PARENT_PATH + getBackslash() + \
    "lib"+getBackslash() + "walle-cli-all.jar"
channelsOutputFilePath = JIAGU_APK_PARENT_PATH + getBackslash() + "channels"
channelFilePath = SCRIPT_PARENT_PATH + getBackslash() + "channel"

# 获取加固好了的apk的文件地址


def getJiaguApkName():
    filelist = os.listdir(JIAGU_APK_PARENT_PATH)
    for filename in filelist:
        if filename[-10:] == "_jiagu.apk":
            return filename
    return ""


# 如果加固好的apk文件不存在，就中断流程
if getJiaguApkName() == "":
    sys.exit(0)
protectedSourceApkPath = JIAGU_APK_PARENT_PATH+getBackslash()+getJiaguApkName()
print(protectedSourceApkPath)

zipalignedApkPath = protectedSourceApkPath[0: -4] + "_aligned.apk"
signedApkPath = zipalignedApkPath[0: -4] + "_signed.apk"

# 创建Channels输出文件夹
createChannelsDir()

# 清空Channels输出文件夹
cleanChannelsFiles()


# 对齐
zipalignShell = BUILD_TOOL_PATH+getBackslash() + "zipalign -v 4 " + \
    protectedSourceApkPath + " " + zipalignedApkPath
os.system(zipalignShell)

# 签名
signShell = BUILD_TOOL_PATH + getBackslash() + "apksigner sign --ks " + KEY_STORE_PATH +\
    " --ks-key-alias " + KEY_ALIAS + " --ks-pass pass:" + KEY_PASSWORD + \
    " --key-pass pass:" + KEY_ALIAS_PASSWORD + " --out " + \
    signedApkPath + " " + zipalignedApkPath
os.system(signShell)
print(signShell)

# 检查V2签名是否正确
checkV2Shell = "java -jar " + checkAndroidV2SignaturePath + " " + signedApkPath
os.system(checkV2Shell)

# 写入渠道,配置信息在channel文件
writeChannelShell = "java -jar " + walleChannelWritterPath + " batch -f " + \
    channelFilePath + " " + signedApkPath + " " + channelsOutputFilePath

os.system(writeChannelShell)

cleanTempResource()

print("\n**** =============================TASK FINISHED=================================== ****\n")
print("\n↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓   Please check channels in the path   ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\n")
print("\n"+channelsOutputFilePath+"\n")
print("\n**** =============================TASK FINISHED=================================== ****\n")
