# 集成360加固和Walle多渠道打包
解决360加固导致的渠道信息丢失的问题，同时快速打多渠道包

### 用法：

- App添加Walle的依赖`compile 'com.meituan.android.walle:library:1.1.6'`
- 在config360.py里面添加自己的360账号信息
- 在sign.json文件里面添加签名信息和buildToolVersion信息
- 各种渠道的定义是在`channel`这个文件中，请根据项目情况修改
- 运行命令`python path_of_jiagu_walle.py path_of_apk you_key_name` ,这里的可以*key_name*需要配置在`sign.json`文件里面
### channel

`channel`文件是存储渠道信息的文件，格式如下：

```
360cn #360
baidu # 百度
wandoujia # 豌豆荚
yingyongbao # 应用宝
xiaomi # 小米
meizu # 魅族
vivo # vivo
oppo # oppo
huawei # 华为
samsung # 三星
chuizi # 锤子
```

### sign.json

sign.json存放的是签名信息，字段设计参考

```json
{
    "myKeyName": {
        "keyStore": "C:\\Users\\Desktop\\out\\xx.jks",
        "alias": "xxxxx",
        "keyPassword": "xxxxx",
        "aliasPassword": "xxx",
        "buildToolVersion": "27.0.0"
    }
}
```

### 兼容腾讯应用宝市场

由于腾讯的应用宝市场需要使用自己的乐加固进行加固，导致之前进行的美团渠道信息丢失，所以需要进行单独的处理。打开乐加固的软件，可以看到，它本身是支持多渠道打包的。我们可以在`Android Name`一栏写上app定义好的渠道key例如“CHANNEL”,然后`配置参数`随便写上啥，只要你自己知道这个表示的是应用宝市场就行。

![](https://file.2fun.xyz/LEJIAGU20190111112231.png)

然后在app的`AndroidManifest.xml`里面添加应用宝的渠道设置信息：

```xml
<!--应用宝渠道信息-->
<meta-data
    android:name="CHANNEL"
    android:value="lingsir" />
```

### 获取渠道信息

```java
/**
     * 获取app渠道（设备来源）
     *
     * @return
     */
    public String getAppSource(Context ctx) {
        String defChannel = "def";
        if (ctx == null) {
            return defChannel;
        }
        
        String channel = "";

        //从manifest获取,如果manifest设置了值，说明是使用的应用宝多渠道打包，walle不可用
        channel = getMetaData(ctx, "CHANNEL");
        if (!TextUtils.isEmpty(channel) && !channel.equals("lingsir")) {
            return channel;
        }

        //walle从apk包中获取
        channel = WalleChannelReader.getChannel(ctx, defChannel);
        return channel;
    }

    /**
     * 获取Manifest 里面的meta-data
     *
     * @param context
     * @param key
     * @return
     */
    public static String getMetaData(Context context, String key) {
        ApplicationInfo ai = null;
        try {
            ai = context.getPackageManager().getApplicationInfo(context.getPackageName(),
                    PackageManager.GET_META_DATA);
        } catch (PackageManager.NameNotFoundException e) {
            e.printStackTrace();
            return "";
        }
        Bundle bundle = ai.metaData;
        return bundle.getString(key);
    }
```

Walle渠道信息读取类

```java

public final class WalleChannelReader {
    private WalleChannelReader() {
        super();
    }

    /**
     * get channel
     *
     * @param context context
     * @return channel, null if not fount
     */
    @Nullable
    public static String getChannel(@NonNull final Context context) {
        return getChannel(context, null);
    }

    /**
     * get channel or default
     *
     * @param context context
     * @param defaultChannel default channel
     * @return channel, default if not fount
     */
    @Nullable
    public static String getChannel(@NonNull final Context context, @NonNull final String defaultChannel) {
        final ChannelInfo channelInfo = getChannelInfo(context);
        if (channelInfo == null) {
            return defaultChannel;
        }
        return channelInfo.getChannel();
    }

    /**
     * get channel info (include channle & extraInfo)
     *
     * @param context context
     * @return channel info
     */
    @Nullable
    public static ChannelInfo getChannelInfo(@NonNull final Context context) {
        final String apkPath = getApkPath(context);
        if (TextUtils.isEmpty(apkPath)) {
            return null;
        }
        return ChannelReader.get(new File(apkPath));
    }

    /**
     * get value by key
     *
     * @param context context
     * @param key     the key you store
     * @return value
     */
    @Nullable
    public static String get(@NonNull final Context context, @NonNull final String key) {
        final Map<String, String> channelMap = getChannelInfoMap(context);
        if (channelMap == null) {
            return null;
        }
        return channelMap.get(key);
    }

    /**
     * get all channl info with map
     *
     * @param context context
     * @return map
     */
    @Nullable
    public static Map<String, String> getChannelInfoMap(@NonNull final Context context) {
        final String apkPath = getApkPath(context);
        if (TextUtils.isEmpty(apkPath)) {
            return null;
        }
        return ChannelReader.getMap(new File(apkPath));
    }

    @Nullable
    private static String getApkPath(@NonNull final Context context) {
        String apkPath = null;
        try {
            final ApplicationInfo applicationInfo = context.getApplicationInfo();
            if (applicationInfo == null) {
                return null;
            }
            apkPath = applicationInfo.sourceDir;
        } catch (Throwable e) {
        }
        return apkPath;
    }
}
```

### 为什么不使用乐加固进行多渠道打包?

乐加固的多渠道打包时间和美团的walle差别不大，但是乐加固没有提供jar包进行操作，导致无法实现自动化操作，所以我选择了walle。

### 运行注意事项：

1. 保证你Android程序的compileSdKVersion 和 buildToosVersion 版本相同
2. 建议将jdk升级到1.8
3. 保证自己本地打包签名可以正常运行
4. 保证配置的相关路径正确，编码格式为UTF-8，不要带异常字符。
5. Android SDK buidtools请使用25.0+版本，越新越好。

----------
### 参考

[**ProtectedApkResignerForWalle**](https://github.com/Jay-Goo/ProtectedApkResignerForWalle)