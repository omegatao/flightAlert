import json
import requests
import time
import math


def pushMessage(message, token):
    sendUrl = f'http://sc.ftqq.com/{token}.send?text={message}'
    requests.get(sendUrl)


if __name__ == "__main__":
    # first import the json config file
    with open("config.json") as f:
        config = json.load(f)
    # assemble the request url
    baseUrl = "https://flights.ctrip.com/itinerary/api/12808/lowestPrice?"
    url = f'https://flights.ctrip.com/itinerary/api/12808/lowestPrice?flightWay={config["flightWay"]}&dcity={config["placeFrom"]}&acity={config["placeTo"]}&direct=true&army=false'

    # get the price periodicly and alert through wechat
    targetPrice = 0
    while True:
        r = requests.get(url)
        if r.status_code != 200 or r.json()["status"] == 2:
            print("无法获取机票信息,等待30s后重新尝试获取")
            for i in range(30):
                print(".", end="")
                time.sleep(1)
            print("\n等待完毕，尝试重新获取机票信息")
            continue
        else:
            result = r.json()["data"]["oneWayPrice"][0]
            if not config["dateToGo"] in result:
                print("未能找到指定日期机票价格，请检查日期是否过长或者是过期日期")
                exit()
            else:
                currentPrice = result[config["dateToGo"]]
                if targetPrice == 0:
                    print(f'当前票价:{currentPrice}，第一次获取票价请检查微信推送')
                    pushMessage(
                        f'第一次推送，当前价格{currentPrice}-当前时间:{time.strftime("%H-%m-%S",time.localtime())}', config["ftqq_SCKEY"])
                    targetPrice = currentPrice
                else:
                    if abs(currentPrice - targetPrice) >= config["priceStep"]:
                        pushMessage(
                            f'价格变化超过设定值，当前价格{currentPrice},变化:{currentPrice-targetPrice},当前时间:{time.strftime("%H:%m:%S",time.localtime())}', config["ftqq_SCKEY"])
                        targetPrice = currentPrice
        print(f'当前轮次查询完毕，等待{config["sleepTime"]}s后继续查询价格')
        time.sleep(config["sleepTime"])
