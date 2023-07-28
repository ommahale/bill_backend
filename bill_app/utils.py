from http.client import RemoteDisconnected
from bs4 import BeautifulSoup
import requests
import dotenv
import os
from random import randint
from requests.exceptions import ConnectTimeout

class MahadiscomApi:
    
    user_agent = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    
    def __init__(self,targetUrl,username,password,max_retrys) -> None:
        self.targetUrl = targetUrl
        self.username = username
        self.password = password
        self.max_retrys = max_retrys
        self.try_count=0
        self.cookie=None
        self.html_text=None
        self.bill_html=None
        self.bills=[]

        # ======================= PROXY API CALL =======================
        #Need to improve this

        # self.proxy_arr=requests.get('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc',headers=self.user_agent).json()['data']
        # index=randint(0,500)
        # self.proxy=self.proxy_arr[index]['protocols'][0]+'://'+self.proxy_arr[index]['ip']+':'+self.proxy_arr[index]['port']
        # print(self.proxy)

    # def getNewProxy(self):
    #     index=randint(0,500)
    #     self.proxy=self.proxy_arr[index]['protocols'][0]+'://'+self.proxy_arr[index]['ip']+':'+self.proxy_arr[index]['port']

    def executeGet(self):
        try:
            response = requests.get(self.targetUrl,headers=self.user_agent)
            cookie = response.headers['Set-Cookie']
            self.cookie = cookie
            print(cookie)
            return cookie
        except(RemoteDisconnected):
            print("Proxy Error")
            self.executeGet()
    
    def executePost(self):
        payload = {'loginId':self.username,'password':self.password,'uiActionName':'postCustAccountLogin'}
        params = {'Set-Cookie':self.cookie}
        try:
            response = requests.post(self.targetUrl,data=payload,headers=params)
            self.html_text = response.text
        except:
            self.executePost()

    def executePostBills(self,bu,bm,csn):
        payload= {'loginId':self.username,'password':self.password,'uiActionName':'getLTEnergyBillPage','hdnBillMonth': bm,'isViaForm': 'Y',
               'isLT':'Y','hdnBu':bu,'hdnConsumerNumber':csn}
        params = {'Set-Cookie':self.cookie}
        response = requests.post(self.targetUrl,data=payload,headers=params)
        self.bill_html = response.text
        soup_bill = BeautifulSoup(self.bill_html,'html.parser')
        info={}
        billDate = soup_bill.find('label',{'id':'billDate'}).text
        amount = soup_bill.find('label',{'id':'roundBill1'}).text.replace(',','')
        last_date = soup_bill.find('label',{'id':'billDueDate1'}).text
        penalty_amount = soup_bill.find('label',{'id':'netBillDPC1'}).text.replace(',','')
        current_reading = soup_bill.find('label',{'id':'currentReading1M'}).text.lstrip()
        incentive_date = soup_bill.find('label',{'id':'promptPaymentDate5'}).text
        incentive_amount = soup_bill.find('label',{'id':'netBillPPD3'}).text.replace(',','')
        connection_category= soup_bill.find('label',{'id':'category'}).text
        bill_description = soup_bill.find('label',{'id':'consumerAddress'}).text
        consumer_name = soup_bill.find('label',{'id':'consumerName'}).text
        electrical_duty = soup_bill.find('label',{'id':"electricityDuty"}).text
        info['billDate']=billDate
        info['amount']=float(amount)
        info['last_date']=last_date
        info['penalty_amount']=float(penalty_amount)
        info['current_reading']=current_reading
        info['incentive_date']=incentive_date
        info['incentive_amount']=float(incentive_amount)
        info['connection_category']=connection_category
        info['bill_description']=bill_description
        info['consumer_name']=consumer_name
        info['electrical_duty']=float(electrical_duty)
        return info



    def consumer_parser(self):
        soup = BeautifulSoup(self.html_text,'html.parser')
        table = soup.find('table',{"id": "grdCustList"})
        # find all the rows in table excluding the headers
        rows = table.find_all('tr')
        data = []
        # all data is stored here
        try_bills=[]
        for r in rows:
            # find table columns
            table_data = r.find_all('td')
            data.append([ i.text for i in table_data ])
        try:    
            for d in data:
                if len(d)==15:
                    bill=self.executePostBills(csn=d[1],bu=d[2],bm=d[5])
                    # print(d[6].strip())
                    bill['units_consumed']=d[6].strip()
                    bill['bill_month']=d[5]
                    bill['consumer_number']=d[1]
                    bill['bill_unit']=int(d[2])
                    print(bill)
                    try_bills.append(bill)
                    if len(try_bills)>len(self.bills):
                        self.bills=try_bills
                        print('Bills Updated____________________')
                        print(self.bills)
        except:
            if self.try_count<self.max_retrys:
                self.try_count+=1
                print('Retrying')
                self.consumer_parser()
            else:
                print('Max Retrys Exceeded')
                print(self.bills)
                return self.bills

        return self.bills

    def getData(self):
        self.executeGet()
        self.executePost()
        self.consumer_parser()
        


dotenv.load_dotenv()
targetUrl='https://wss.mahadiscom.in/wss/wss?uiActionName=getCustAccountLogin'
apiKalwa=MahadiscomApi(targetUrl=targetUrl,username=os.getenv('KALWA_USERNAME'),password=os.getenv('KALWA_PASSWORD'),max_retrys=10)
# apiKalwa.getData()
# print(apiKalwa.bills)

def getData():
    data=requests.get('http://127.0.0.1:5500/bill_app/railway_response.json')
    return data.json()