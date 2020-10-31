# CSU-COVID19-SIGN

![Windows](https://img.shields.io/badge/Web-Vue-green.svg)

![Windows](https://img.shields.io/badge/Server-Python-green.svg)

![License](https://img.shields.io/badge/License-MPL_2.0-orange.svg)

> 人不能，至少不应该，把注意力消耗在重复性的工作上

本项目旨在提供一项自动打卡服务

使用该服务可减少使用者接入自动打卡的门槛，使更多人接触并使用自动打卡脚本

在线服务地址：https://covid19.csu-edu.cn

离线打卡项目：https://github.com/wolfbolin/Tools-for-CSU/tree/master/src/nCOV-sign-in



## 工作逻辑

### 登录逻辑

用户在首页填写信息门户的账号密码后，由服务器代为执行登录操作

在服务器执行登录操作后，服务器将保存登录产生的Cookie信息，并在每次连接时更新

该Cookie仅拥有访问打卡页面的权限，不涉及账户下其他数字资产的访问权限，并且在登录后释放密码

### 打卡逻辑

服务器在用户设定的时间节点，由外部时钟驱动触发打卡记录检查工作。

服务端将按照一定顺序，使用先前存储的Cookies，逐个检查用户的打卡状态。

对于没有打卡的用户，将获取用户前一日打卡的信息，并使用该信息进行打卡。

若需要修改打卡记录中的信息，仅需要在服务自动打卡前，自行在平台打卡即可。

### 存在的问题

Cookies的有效性无法有效保证，但是为了不存储密码采用该折中方案。

用户打卡结果无法实时或异步进行推送，使用平台发短信有点贵，仅VIP用户可收短信。



