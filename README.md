# NAS媒体库管理工具

## 版本声明

1）本项目基于开源维护项目[nas-tools](https://github.com/hsuyelin/nas-tools)开发，非官方项目；  
2）相关声明和说明参考原项目[nas-tools](https://github.com/hsuyelin/nas-tools)。   

---

## 注意事项

1）mt站适配情况：  

- [x] 连通性测试

- [x] 获取令牌

- [x] 自动签到

- [x] 站点数据统计

- [x] 刷流

- [x] RSS订阅、下载

- [x] 订阅搜索、下载

- [x] 站点资源列表、下载

- [x] 资源搜索、下载

- [x] 自动删种

- [x] 未读消息提醒

- [ ] 从详情页下载字幕（基本没有，所以没做）



2）使用前需手动在mt站创建ApiKey(控制台-实验室-创建令牌)。


3）由于mt的限制，如果需要全部功能则cookie和apikey都需要。如果只需要部分功能可以参考下面：  

| cookie | apikey |
| ------ | ------ |
| 站点自动签到 | 资源查询相关 |
| 未读消息提醒 | 资源下载相关 |
| 站点数据统计 | 订阅刷流相关 |

例如：

A只想使用刷流功能，就不必关心cookie是否过期，只需要保证apikey没有删除就可以。  

B只使用自动签到，就不必建立令牌，只要保证cookie没有过期就可以。


4）站点维护中的设置（重点）：

- 浏览器仿真设置为否。

- 站点地址设置到mt主域名(https://xx.x-xxxx.xx/) 。

- UA设置为常用浏览器UA，或在设置-基础设置里设置为常用浏览器UA。

- 填入全部内容后，点击更新apikey会自动获取最新的令牌，也可以自己填入，在mt更换令牌后需重新再获取一次。

- 如果是导入以前的配置，可能站点维护中看不见更新apikey的按钮，将站点地址重新输入一下就可以了。

- RSS订阅生成链接时，項目標題格式选项需勾选[大小]，否则无法使用按种子大小过滤（自动获取大小会对站点造成很多无意义访问，加重mt站点压力，自己改一下叭。）。
   
- COOKIE:请求头中Authorization的值。(在浏览器中F12->网络页抓取，字段名为[Authorization])。

5）已去除更新提示和更新系统的指令。

6）常用功能已本机测试，有bug欢迎反馈。


---

## 安装
### 1、Docker
```
docker pull demigody12138/nas-tools:latest
```

如无法连接Github，注意不要开启自动更新开关(NASTOOL_AUTO_UPDATE=false)，将NASTOOL_CN_UPDATE设置为true可使用国内源加速安装依赖。

### 2、本地运行
仅支持python3.10版本，需要预安装cython（python3 -m pip install Cython），如发现缺少依赖包需额外安装：
```
git clone -b master https://github.com/demigody12138/nas-tools --recurse-submodule 
python3 -m pip install --force-reinstall -r requirements.txt
export NASTOOL_CONFIG="/xxx/config/config.yaml"
nohup python3 run.py & 
```

### 3、可执行文件运行
下载地址：https://github.com/demigody/nas-tools/releases
仅支持python3.10版本，先从tag下载对应的可执行文件，打开终端，例如下载的是macos版本，文件名为：nastool_macos_v3.2.2：
```bash
mv nastool_macos_v3.2.2 nastools
chmod +x nastools
// macos 12以上需要去隐私-安全性，允许任意开发者
./nastools（如果需要不在终端输出执行：./nastool &> /dev/null）
```