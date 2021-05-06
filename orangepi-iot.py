from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests
from urllib import request
import ST7735
from bs4 import BeautifulSoup
from time import gmtime, strftime, localtime
from datetime import datetime, timedelta
import time
import numpy as np
import os
import _thread
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from io import BytesIO
import smbus
import time
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
weaLoop = 300
coinLoop = 180
switchScreenLoop = 15


def getLocalWea():
    bus = smbus.SMBus(1)    #0 means /dev/i2c-0, 1 means /dev/i2c-1
    bus.write_i2c_block_data(0x44, 0x2C, [0x06])    #address 0x44, offset 0x2c, data 0x06
    time.sleep(0.5)
    data = bus.read_i2c_block_data(0x44, 0x00, 6)   #read data from address 0x44, offset 0, 6 bytes
    cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
    fTemp = cTemp * 1.8 + 32
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
    #print("Relative Humidity : %.2f %%RH" %humidity)
    #print("Temperature in Celsius : %.2f C" %cTemp)
    #print("Temperature in Fahrenheit : %.2f F" %fTemp)
    return (cTemp, fTemp, humidity)

def getWea():
    global session
    url = 'http://www.weather.com.cn/weather/101110101.shtml'
    weekly_weather = session.get(url).content
    #req = request.Request(url)
    #weekly_weather = request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(weekly_weather, 'html.parser')
    seven_days = soup.find('ul', class_='t clearfix').get_text()
    seven_days = seven_days.split('\n')
    days = []
    for day in seven_days:
        if day != '':
            days.append(day)
        else:
            pass
    strAll = ''
    for i in range(2):
        #print(days[i*4])
        strAll += days[i*4] + '\n'
        #print(days[i*4+1])
        strAll += days[i*4+1] + '\n'
        #print(days[i*4+2])
        strAll += days[i*4+2] + ' '
        #print(days[i*4+3])
        strAll += days[i*4+3] + ' '
        #print('\n')
        strAll += '\n'
    #print(strAll)
    wea=strAll
    return wea

disp = ST7735.ST7735(port=1, cs=0, dc=7, backlight=None, rst=25, width=129, height=160, rotation=0, offset_left=-1, offset_top=-1, invert=False)
WIDTH = disp.width
HEIGHT = disp.height
path_to_ttf = r'/home/orangepi/Songti.ttc'
font = ImageFont.truetype(path_to_ttf, size=14)
fontCL = ImageFont.truetype(path_to_ttf, size=13)
fontE = ImageFont.truetype(path_to_ttf, size=10)
#r = requests.get('http://www.weather.com.cn/data/sk/101110101.html')
#r.encoding = 'utf-8'
#wea =  '城市:' + r.json()['weatherinfo']['city']+'\nWS:'+ r.json()['weatherinfo']['WS']+'\nWD:'+ r.json()['weatherinfo']['njd']+'\n温度:'+ r.json()['weatherinfo']['temp']

#wea=getWea()


#img = Image.new('RGB', (WIDTH, HEIGHT), (55,5,5))
#img2 = Image.open('/boot/boot.bmp')
img2 = Image.open('/home/orangepi/kqy.jpeg')
imgcoin_bk = Image.new('RGB', (WIDTH, HEIGHT), (0,0,255))
imgbk = img2.resize((WIDTH, HEIGHT))
draw = ImageDraw.Draw(imgbk)
cur = (datetime.now()+ timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
draw.text((1, 0), '启动中...\n'+cur, font=font, fill=(255, 0, 0))
disp.display(imgbk)

img = img2.resize((WIDTH, HEIGHT))
imgcoin0 = imgcoin_bk.resize((WIDTH, HEIGHT))
imgcoin1 = imgcoin_bk.resize((WIDTH, HEIGHT))
imgcoin2 = imgcoin_bk.resize((WIDTH, HEIGHT))
imgcoin3 = imgcoin_bk.resize((WIDTH, HEIGHT))
#data = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
#data[0:256, 0:256] = [255, 0, 0] # red patch in upper left
#img = Image.fromarray(data, 'RGB')

#draw = ImageDraw.Draw(img)

# Load default font.
#font = ImageFont.load_default()
#draw.text((0, 0), '西安天气\n'+(datetime.now()+ timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"), font=font, fill=(0, 0, 0))
#disp.begin()
#subprocess.run(["/etc/init.d/networking", "restart"])
print("Restarting networks...")
os.system("/etc/init.d/networking restart")
time.sleep(5)

i = 60
lastErr = 'ok'
lastOk = 'ok'
wea='获取中...'

def getCoin():
    global session
    content = session.get("https://coinmarketcap.com/").content
    soup = BeautifulSoup(content,"html.parser")
    coin_table = soup.find('table', class_='cmc-table')
    tb = coin_table.find('tbody')
    trs = tb.find_all('tr')
    ret = []
    for tr in trs[0:10]:
        #print(len(trs))
        #print(tr.get_text())
        b = []
        all_td = tr.find_all('td')

        coin_seq = all_td[1].find('p').get_text()
        b.append(coin_seq)
        coin_name = all_td[2].find('div', class_='sc-16r8icm-0').find('p').get_text()
        b.append(coin_name)
        coin_name_simp = all_td[2].find('div', class_='sc-1teo54s-2').find('p').get_text()
        b.append(coin_name_simp)
        coin_price = all_td[3].get_text()
        b.append(coin_price)
        coin_price_change_24h = all_td[4].get_text()
        b.append(coin_price_change_24h)
        coin_price_change_7d = all_td[5].get_text()
        b.append(coin_price_change_7d)
        coin_market_cap = all_td[6].get_text()
        b.append(coin_market_cap)
        coin_volume = all_td[7].get_text()
        b.append(coin_volume)
        coin_image = all_td[9].find('img').get('src')
        b.append(coin_image)
        ret.append(b)
        #print(coin_seq,coin_name,coin_name_simp,coin_price,coin_price_change_24h,coin_price_change_7d,
        #coin_market_cap,coin_volume,coin_image)
    #print(ret)
    return ret
def create_coincap():
    lastErr = 'ok'
    lastOk = 'ok'
    coin_name0 = ''
    coin_price0 = ''
    coin_change_24h0 = ''
    coin_change_7d0 = ''
    coin_img0 = ''

    coin_name1 = ''
    coin_price1 = ''
    coin_change_24h1 = ''
    coin_change_7d1 = ''
    coin_img1 = ''

    coin_name2 = ''
    coin_price2 = ''
    coin_change_24h2 = ''
    coin_change_7d2 = ''
    coin_img2 = ''
    ret = []
    global imgcoin3, imgcoin0, imgcoin1,imgcoin2, imgcoin_bk, WIDTH, HEIGHT, coinLoop,session
    while True:
        cur = (datetime.now()+ timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print("start get coin: "+cur)
        imgOcc = (WIDTH,30)
        try:
            start = datetime.now()
            ret=getCoin()
            coin_name0 = ret[0][2]
            coin_price0 = ret[0][3]
            coin_change_24h0 = ret[0][4]
            coin_change_7d0 = ret[0][5]
            coin_img0 = ret[0][-1]

            coin_name1 = ret[1][2]
            coin_price1 = ret[1][3]
            coin_change_24h1 = ret[1][4]
            coin_change_7d1 = ret[1][5]
            coin_img1 = ret[1][-1]

            coin_name2 = ret[2][2]
            coin_price2 = ret[2][3]
            coin_change_24h2 = ret[2][4]
            coin_change_7d2 = ret[2][5]
            coin_img2 = ret[2][-1]
            imgcoin0 = imgcoin_bk.resize((WIDTH, HEIGHT))
            imgResp = session.get(coin_img0)
            imgRemote = Image.open(BytesIO(imgResp.content))
            imgRemote = imgRemote.resize(imgOcc)
            imgRemoteNew = Image.new("RGB", imgRemote.size, (255, 255, 255))
            imgRemoteNew.paste(imgRemote, mask=imgRemote.split()[3]) # 3 is the alpha channel
            #imgRemote = imgRemote.convert(imgcoin0.mode)
            imgcoin0.paste(imgRemoteNew, (0, 115, 0+imgOcc[0], 115+imgOcc[1]))
            imgcoin1 = imgcoin_bk.resize((WIDTH, HEIGHT))
            imgResp = session.get(coin_img1)
            imgRemote = Image.open(BytesIO(imgResp.content))
            imgRemote = imgRemote.resize(imgOcc)
            imgRemoteNew = Image.new("RGB", imgRemote.size, (255, 255, 255))
            imgRemoteNew.paste(imgRemote, mask=imgRemote.split()[3]) # 3 is the alpha channel
            #imgRemote = imgRemote.convert(imgcoin0.mode)
            imgcoin1.paste(imgRemoteNew, (0, 115, 0+imgOcc[0], 115+imgOcc[1]))
            imgcoin2 = imgcoin_bk.resize((WIDTH, HEIGHT))
            imgResp = session.get(coin_img2)
            imgRemote = Image.open(BytesIO(imgResp.content))
            imgRemote = imgRemote.resize(imgOcc)
            imgRemoteNew = Image.new("RGB", imgRemote.size, (255, 255, 255))
            imgRemoteNew.paste(imgRemote, mask=imgRemote.split()[3]) # 3 is the alpha channel
            #imgRemote = imgRemote.convert(imgcoin0.mode)
            imgcoin2.paste(imgRemoteNew, (0, 115, 0+imgOcc[0], 115+imgOcc[1]))
            imgcoin3 = imgcoin_bk.resize((WIDTH, HEIGHT))
            end = datetime.now()
            lastOk = "coin ok:"+cur
            elapsed = end - start
            print("coin elapsed:",elapsed)
        except Exception as e:
            lastErr="coin err:"+cur
            #print(lastErr)
            print(e)

        draw = ImageDraw.Draw(imgcoin0)
        col = (255,255,255)
        draw.text((1, 0), 'Crypto currency 1:\n'+cur, font=font, fill=col)
        draw.text((1, 35), "Name:"+coin_name0, font=font, fill=col)
        draw.text((1, 55), "Price:"+coin_price0, font=font, fill=col)
        draw.text((1, 75), "Change(24h):"+coin_change_24h0, font=font, fill=col)
        draw.text((1, 95), "Change(7d):"+coin_change_7d0, font=font, fill=col)
        #draw.text((1, 105), "img:"+coin_img0, font=font, fill=col)
        draw.text((1, 145), lastOk, font=fontE, fill=(255, 255, 255))

        draw = ImageDraw.Draw(imgcoin1)
        draw.text((1, 0), 'Crypto currency 2:\n'+cur, font=font, fill=col)
        draw.text((1, 35), "Name:"+coin_name1, font=font, fill=col)
        draw.text((1, 55), "Price:"+coin_price1, font=font, fill=col)
        draw.text((1, 75), "Change(24h):"+coin_change_24h1, font=font, fill=col)
        draw.text((1, 95), "Change(7d):"+coin_change_7d1, font=font, fill=col)
        #draw.text((1, 105), "img:"+coin_img1, font=font, fill=col)
        draw.text((1, 145), lastOk, font=fontE, fill=(255, 255, 255))

        draw = ImageDraw.Draw(imgcoin2)
        draw.text((1, 0), 'Crypto currency 3:\n'+cur, font=font, fill=col)
        draw.text((1, 35), "Name:"+coin_name2, font=font, fill=col)
        draw.text((1, 55), "Price:"+coin_price2, font=font, fill=col)
        draw.text((1, 75), "Change(24h):"+coin_change_24h2, font=font, fill=col)
        draw.text((1, 95), "Change(7d):"+coin_change_7d2, font=font, fill=col)
        #draw.text((1, 105), "img:"+coin_img2, font=font, fill=col)
        draw.text((1, 145), lastOk, font=fontE, fill=(255, 255, 255))


        draw = ImageDraw.Draw(imgcoin3)
        if len(ret) >= 10:
            for i in range(0,10):
                draw.text((1, i*14), ret[i][2]+": "+ret[i][4]+', '+ret[i][3], font=fontCL, fill=col)
        draw.text((1, 145), lastOk, font=fontE, fill=(255, 255, 255))
        time.sleep(coinLoop)
def create_weather():
    lastErr = 'ok'
    lastOk = 'ok'
    localC = '5.0'
    localH = '25%'
    global img, img2, WIDTH, HEIGHT, weaLoop,wea
    while True:
        cur = (datetime.now()+ timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print("start get wea: "+cur)
        try:
            start = datetime.now()
            wea=getWea()
            localSensor = getLocalWea()
            localC = "%.1f" %localSensor[0]
            localH = "%.1f" %localSensor[2]
            end = datetime.now()
            elapsed = end - start
            print("wea elapsed:",elapsed)
            lastOk = "wea ok:"+cur
        except:
            lastErr="wea error:"+cur
            print(lastErr)
        img = img2.resize((WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        col = (255,255,0)
        draw.text((1, 0), '西安天气:\n'+'实时:'+localC+'C, '+localH+'%RH', font=font, fill=col)
        draw.text((1, 35), wea, font=font, fill=col)
        draw.text((1, 145), lastOk, font=fontE, fill=(0, 0, 255))
        time.sleep(weaLoop)

_thread.start_new_thread(create_weather,())
_thread.start_new_thread(create_coincap,())

screenIndex = 0
while True:
    cur = (datetime.now()+ timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    print("main: "+cur+" ", i)
    if i%switchScreenLoop == 0:
        print("Switching: ", screenIndex)
        if screenIndex == 0:
            disp.display(img)
        elif screenIndex == 1:
            disp.display(imgcoin0)
        elif screenIndex == 2:
            disp.display(imgcoin1)
        elif screenIndex == 3:
            disp.display(imgcoin2)
        elif screenIndex == 4:
            disp.display(imgcoin3)
        else:
            screenIndex = 0
            disp.display(img)
        screenIndex = screenIndex + 1
        i = 0
    i = i + 1
    time.sleep(1)