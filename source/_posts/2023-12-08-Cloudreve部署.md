---
title: Cloudreve部署
slug: Cloudreve部署
permalink: 2023/12/08/Cloudreve部署/
date: 2023-12-08 23:18:00
---
# Cloudreve部署
​	Linux专业课 期末大作业

​	Cloudreve是一个由Go语言开发的网盘系统，可以快速部署在服务器上，支持不同的云存储平台。本次作业我们小组将基于Centos7使用Cloudreve搭建一个以ECS云盘为存储平台的小团体的网盘系统。

## 1.1 环境准备
​	需要准备的内容有：

- Go语言开发环境

- 安装Node.js

- 安装Yarn

- 安装git

​	Cloudreve程序中内置了一个Web服务器，构建完毕运行之后会在5212端口创建一个服务，所以我们不需要额外安装Apache或者Nginx

### 安装Go语言开发环境
1.在Go官网下载Linux开发工具包

```shell
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
```

![image-20231208165511910](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208165511910-1702048792490-20.png)

2.解压安装包

```shell
sudo tar -C /usr/local -xzf go1.16.7.linux-amd64.tar.gz
```

3.设置环境变量

编辑文件`/etc/profile`

```shell
vim /etc/profile
```

在其底部添加

```shell
export PATH=$PATH:/usr/local/go/bin
```

![image-20231208165958797](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208165958797-1702048792490-21.png)

4.查看go版本

```shell
go version
```

![image-20231208170852664](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208170852664-1702048792490-22.png)

确保已经正确安装go环境。

### 安装Node.js
​	Node.js是JavaScript的一个免费开源跨平台的一个运行环境，因为Cloudreve需要Node.js的支持，所以我们需要在centos7中安装Node.js。

1.在官网找到软件包

​	![image-20231208172633648](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208172633648.png)

使用wget下载

```shell
wget https://nodejs.org/download/release/latest-v16.x/node-v16.20.2-linux-x64.tar.gz
```

2.解压软件包

```shell
tar -xvf node-v16.20.2-linux-x64.tar.gz
```

![image-20231208172754511](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208172754511-1702048792490-23.png)

3.移动目录

```shell
mv node-v16.20.2-linux-x64/ /usr/local/
```

4.配置环境变量&刷新

```shell
vi /etc/profile
```

```shell
export NODEJS=/usr/local/node-v16.20.2-linux-x64
export PATH=$PATH:$NODEJS/bin
```

![image-20231208173053180](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208173053180.png)

安装成功

![image-20231208173233575](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208173233575.png)

### 安装Yarn
1.添加Yarn仓库

```shell
curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | sudo tee /etc/yum.repos.d/yarn.repo
```

![image-20231208173432216](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208173432216.png)

2.安装Yarn

```shell
yum install -y yarn
```

![image-20231208173516937](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208173516937.png)

3.安装完成检查版本

```shell
yarn --version
```

![image-20231208173541256](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208173541256-1702048792490-24.png)

### 安装git工具

```shell
yum install -y git
```

## 1.2 开始构建

### 克隆代码

```shell
git clone --recurse-submodules https://github.com/cloudreve/Cloudreve.git
```

![image-20231208173818483](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208173818483.png)

```shell
# 签出要编译的版本
git checkout 3.x.x
```

### 构建静态资源

```shell
# 进入前端子模块
cd assets
# 安装依赖
yarn install
# 开始构建
yarn run build
# 构建完成后删除映射文件
cd build
find . -name "*.map" -type f -delete
# 返回项目主目录打包静态资源
cd ../../
zip -r - assets/build >assets.zip
```

![image-20231208180753853](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208180753853.png)

![image-20231208180733294](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208180733294.png)

### 编译项目
获得当前版本号

```shell
export COMMIT_SHA=$(git rev-parse --short HEAD)
export VERSION=$(git describe --tags)
```

开始编译

```shell
go build -a -o cloudreve -ldflags " -X 'github.com/cloudreve/Cloudreve/v3/pkg/conf.BackendVersion=$VERSION' -X 'github.com/cloudreve/Cloudreve/v3/pkg/conf.LastCommit=$COMMIT_SHA'
```

首次编译时，Go 会下载相关依赖库![image-20231208181120297](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208181120297.png)

编译完成之后，在项目根目录生成最终的可执行文件`cloudreve`

## 1.3 启动 Cloudreve

```shell
# 赋予执行权限
chmod +x ./cloudreve

# 启动 Cloudreve
./cloudreve
```

​	Cloudreve 默认会监听`5212`端口。在浏览器中访问`http://服务器IP:5212`进入 Cloudreve。

![image-20231208225643025](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208225643025-1702048792490-25.png)

## 1.4 完成
​	访问IP:5212端口，保存初次启动Cloudreve的默认密码登录web端后台

![image-20231208225711848](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208225711848.png)

![image-20231208225802195](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208225802195.png)

​	设置存储空间和用户组![image-20231208225806921](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208225806921.png)

![image-20231208225835962](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208225835962.png)

​	Cloudreve作为一个云盘系统，可以选择本机存储，从机存储，七牛云，或者阿里云OSS对象存储等多种存储方式

![image-20231208230226316](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208230226316-1702048792490-26.png)

​	并且还拥有创建分享链接的功能

![image-20231208230630730](/2023/12/08/Cloudreve%E9%83%A8%E7%BD%B2/image-20231208230630730-1702048792490-27.png)

                
              
            
            
---

            
              
  
  

              
  

  
    
      Cloudreve部署
      http://example.com/2023/12/08/Cloudreve部署/
    
    
      
        
          作者
          To1y5
        
      
      
        
          发布于
          2023年12月8日
        
      
      
      
        
          许可协议
          
            
              
              
                [
                  
                    
                  
                ](https://creativecommons.org/licenses/by/4.0/)
              
            
          
        
      
    
    
  

              
                
                  
                    
                    
                      [
                        
                        速成蓝桥省一
                        上一篇
                      ](/2023/12/14/%E9%80%9F%E6%88%90%E8%93%9D%E6%A1%A5%E7%9C%81%E4%B8%80/)
