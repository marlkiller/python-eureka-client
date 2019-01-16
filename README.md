> 在Spring Cloud的Netfix技术框架中，有一个很重要的管家：Eureka，它作为服务注册中心，提供给各个微服务注册进去，方便整合监控各个微服务等，其以Java语言为基础，同时也有部分客户端实现了服务注册协议，也可以注册进去,详情请点这里[(https://blog.csdn.net/Keijack/article/details/82498144)](https://blog.csdn.net/Keijack/article/details/82498144 "(https://blog.csdn.net/Keijack/article/details/82498144)")


## Eureka Server

- defaultZone: http://localhost:8080/web-eureka/eureka/
- context-path: /web-eureka


## Eureka Client-Java

- spring.application.name: application-client-demo
- context-path: /web-client-demo
port: 8081

提供一个服务接口

[![](http://voidm.com/wp-content/uploads/2019/01/TIM截图20190116163631.png)](http://voidm.com/wp-content/uploads/2019/01/TIM截图20190116163631.png)

此时,注册中心 有以上一个Client节点(**不包含EurekaServer本身**)

[![](http://voidm.com/wp-content/uploads/2019/01/TIM截图20190116163557-1024x168.png)](http://voidm.com/wp-content/uploads/2019/01/TIM截图20190116163557.png)

------------

## Eureka Client-Python

依赖
pip install py-eureka-client 
[https://github.com/keijack/python-eureka-client](https://github.com/keijack/python-eureka-client "https://github.com/keijack/python-eureka-client")


```python
# 导包
import py_eureka_client.eureka_client as eureka_client
```

```python
# 服务ip 与 端口
server_host = "127.0.0.1"
server_port = 9099
```


```python
# 提供健康监测接口(health/info)
class ActuatorInfo(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        self.write("{}")


class ActuatorHealth(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        self.write(json.dumps({
            "status": "UP"
        }))
```

```python

# 提供一个Api,内部远程调用Java-Client端的接口,并响应
# do_service的参数为 application.name , Api接口地址
class IndexHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        name = [b""]
        try:
            name = self.request.arguments['name']
        except:
            print("name 为 空")

        # 远程调用微服务
        res = eureka_client.do_service("application-client-demo", "/web-client-demo?name=" + bytes.decode(name[0]),
                                       # 返回类型，默认为 `string`，可以传入 `json`，如果传入值是 `json`，那么该方法会返回一个 `dict` 对象
                                       return_type="string")
        self.write(res)
```

Main方法

```python
if __name__ == "__main__":
    # blog.csdn.net/moshowgame
    tornado.options.parse_command_line()
    # 注册eureka服务
    eureka_client.init(eureka_server="http://localhost:8080/web-eureka/eureka/",
                       app_name="application-service-demo-python",
                       # 当前组件的主机名，可选参数，如果不填写会自动计算一个，如果服务和 eureka 服务器部署在同一台机器，请必须填写，否则会计算出 127.0.0.1
                       instance_host=server_host,
                       instance_ip=server_host,
                       instance_port=server_port,
                       status_page_url="/web-service-demo-python/actuator/info",
                       # 调用其他服务时的高可用策略，可选，默认为随机
                       ha_strategy=eureka_client.HA_STRATEGY_RANDOM)
    # 提供健康检测接口
    app = tornado.web.Application(handlers=[(r"/", IndexHandler),
                                            (r"/web-service-demo-python", IndexHandler),
                                            (r"/web-service-demo-python/actuator/info", ActuatorInfo),
                                            (r"/web-service-demo-python/actuator/health", ActuatorHealth)
                                            ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(server_port)
    # 开启Web服务
    tornado.ioloop.IOLoop.instance().start()
```

python启动后,刷新Eureka注册中心

[![](http://voidm.com/wp-content/uploads/2019/01/TIM截图20190116164602-1024x181.png)](http://voidm.com/wp-content/uploads/2019/01/TIM截图20190116164602.png)

可以看到,向Eureka注册成功,
调用接口测试,发现服务远程调用也成功了

[![](http://voidm.com/wp-content/uploads/2019/01/TIM截图20190116164729.png)](http://voidm.com/wp-content/uploads/2019/01/TIM截图20190116164729.png)

**远程调用时需要注意 被调用端要配置使用IP替代实例名,并且配置可用IP(如下图),否则调用会404**

[![](http://voidm.com/wp-content/uploads/2019/01/TIM截图20190116165213.png)](http://voidm.com/wp-content/uploads/2019/01/TIM截图20190116165213.png)