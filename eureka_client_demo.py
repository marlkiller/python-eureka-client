# coding:utf-8
import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import py_eureka_client.eureka_client as eureka_client

# 服务ip 与 端口
server_host = "127.0.0.1"
server_port = 9099


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
        self.write("Python Response : " + res)


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
