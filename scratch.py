# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = ''
slack_client_id = ''
slack_client_secret = ''
slack_verification = ''
sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    # 함수를 구현해 주세요
    title = []
    artist = []
    book = []
    merge = []

    when = []
    morning_r = []
    afternoon_r = []
    morning_t = []
    today = []

    if ("음악" in text) or ("music" in text):
        merge.append("실시간 음악 차트 Top 10\n")
        url = "https://music.bugs.co.kr"
        req = urllib.request.Request(url)

        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")

        # keywords.append( "Bus 실시간 음악 차트 Top 10")
        for data in soup.find("tbody").find_all("p", class_="title"):
            if not data.get_text() in title:
                if len(title) >= 10:
                    break
                title.append(data.get_text().replace('\n', ''))
        for data in soup.find("tbody").find_all("p", class_="artist"):
            if not data.get_text() in artist:
                if len(artist) >= 10:
                    break
                artist.append(data.get_text().replace('\n', ''))

        # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
        for i in range(0, 10):
            message = str(i + 1) + '위:' + title[i] + '/' + artist[i]
            merge.append(message)

    elif ("영화" in text) or ("movie" in text):
        merge.append("CGV 예매순위\n")
        url = "http://www.cgv.co.kr/movies/?lt=1&ot=1"
        req = urllib.request.Request(url)
        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")

        # keywords.append( "Bus 실시간 음악 차트 Top 10")
        for data in soup.find("div", class_="sect-movie-chart").find_all("strong", class_="title"):
            if not data.get_text() in title:
                if len(title) >= 10:
                    break
                title.append(data.get_text().replace('\n', ''))
        for data in soup.find("div", class_="sect-movie-chart").find_all("strong", class_="percent"):
            data = data.find("span")
            if not data.get_text() in book:
                if len(book) >= 10:
                    break
                book.append(data.get_text().replace('\n', ''))

        for i in range(0, len(title)):
            message = str(i + 1) + '번째: ' + title[i] + '/ 예매율: ' + book[i]
            merge.append(message)

    elif ("날씨" in text) or ("weather" in text):
        # today = []
        # when = []
        # morning_r = []
        # afternoon_r = []
        # morning_t = []
        # afternoon_t = []

        merge.append("구미 인동 날씨\n")
        url = "https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query=%EA%B5%AC%EB%AF%B8%EB%82%A0%EC%94%A8"
        req = urllib.request.Request(url)

        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")

        if ("지금" in text) or ("now" in text):

            merge.append(" - 현재날씨 - ")
            # 0: 현재온도
            data = soup.find("div", class_="today_area _mainTabContent").find("span", class_="todaytemp")
            data = data.get_text().replace('\n', '') + '℃'
            today.append(data)
            # 1 : 온도 비교
            data = soup.find("div", class_="today_area _mainTabContent").find("p", class_="cast_txt")
            data = data.get_text().replace('\n', '')
            today.append(data)
            # 2 : 최고/최저
            data = soup.find("div", class_="today_area _mainTabContent").find("span", class_="merge")
            data = data.get_text().replace('\n', '')
            today.append(data)
            # 3 : 미세먼지
            data = soup.find("div", class_="today_area _mainTabContent").find("dl", class_="indicator").find("dd")
            data = data.get_text().replace('\n', '')
            today.append(data[-2:])

            message = "현재온도 : " + today[0] + '       |       최저\\최고 : ( ' + today[2] + ' )'
            merge.append(message)
            message = "\t\t<<< " + today[1] + " >>>"
            merge.append(message)
            message = "미세먼지 : " + today[3]
            merge.append(message)
            if "나쁨" in today[3]:
                message = "\t\t미세먼지 농도가 높습니다. 마스크 준비하세욥 > < "
            else:
                message = "\t\t화창한하고 깨끗 ! 산책하기 좋아욥 !"
            merge.append(message)


        else:
            for data in soup.find("div", class_="table_info weekly _weeklyWeather").find_all("span", class_="day_info"):
                if not data.get_text() in when:
                    if len(when) >= 10:
                        break
                    when.append(data.get_text().replace('\n', '')[0])
            for data in soup.find("div", class_="table_info weekly _weeklyWeather").find_all("span",
                                                                                             class_="point_time morning"):
                data = data.find("span", class_="rain_rate").find("span", class_="num")
                if len(morning_r) >= 10:
                    break
                morning_r.append(data.get_text().replace('\n', ''))
            for data in soup.find("div", class_="table_info weekly _weeklyWeather").find_all("span",
                                                                                             class_="point_time afternoon"):
                data = data.find("span", class_="rain_rate").find("span", class_="num")
                if len(afternoon_r) >= 10:
                    break
                afternoon_r.append(data.get_text().replace('\n', ''))
                print(afternoon_r)
            for data in soup.find("div", class_="table_info weekly _weeklyWeather").find_all("dl"):
                data = data.find("dd")
                if len(morning_t) >= 10:
                    break
                morning_t.append(data.get_text().replace('\n', ''))
            # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
            for i in range(0, len(afternoon_r)):
                message = when[i] + " || 온도 - (" + morning_t[i] + ")  | 강수확률 - (" + morning_r[i] + "% / " + afternoon_r[
                    i] + "% )"
                # message = when[i] + " | 오전 : (온도 : " + morning_t[i] + ' / 강수확률 : '+morning_r[i] + ' ) | 오후 : (온도 : ' + afternoon_t[i] + ' / 강수확률 : '+afternoon_r[i] + ' )'
                merge.append(message)
    elif ("뉴스" in text) or ("news" in text) or ("이슈" in text) or ("topic" in text):
        merge.append("오늘의 Topic\n")
        url = "https://news.naver.com/"
        req = urllib.request.Request(url)
        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")

        for data in soup.find("div", class_="main_component droppable").find_all("div", class_="newsnow_tx_inner"):
            if not data.get_text() in title:
                print(data)
                if len(title) >= 10:
                    break
                title.append(data.get_text().replace('\n', ''))
            print(title)

        for i in range(0, len(title)):
            message = str(i + 1) + '번 기사 : ' + title[i]
            merge.append(message)
    else:
        merge.append("#공유와함께하는 #카페타임\n")
        merge.append("[ 원하는 소식을 선택해 주세요 ]")
        merge.append("- 날씨 ")
        merge.append("- 영화 예매 순위 ")
        merge.append("- 실시간 음악 순위")
        merge.append("- 오늘의 뉴스")

    return u'\n'.join(merge)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)