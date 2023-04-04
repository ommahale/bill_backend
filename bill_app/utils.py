from bs4 import BeautifulSoup
import requests
import dotenv
import os


class MahadiscomApi:
    
    user_agent = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    
    def __init__(self,targetUrl,username,password) -> None:
        self.targetUrl = targetUrl
        self.username = username
        self.password = password
        self.cookie=None
        self.html_text=None
        self.bill_html=None
        self.bills=[]

    def executeGet(self):
        response = requests.get(self.targetUrl,headers=self.user_agent)
        cookie = response.headers['Set-Cookie']
        self.cookie = cookie
        return cookie
    
    def executePost(self):
        payload = {'loginId':self.username,'password':self.password,'uiActionName':'postCustAccountLogin'}
        params = {'Set-Cookie':self.cookie}
        response = requests.post(self.targetUrl,data=payload,headers=params)
        self.html_text = response.text

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
        bills=[]
        for r in rows:
            # find table columns
            table_data = r.find_all('td')
            data.append([ i.text for i in table_data ])
        for d in data:
            if len(d)==15:
                bill=self.executePostBills(csn=d[1],bu=d[2],bm=d[5])
                # print(d[6].strip())
                bill['units_consumed']=d[6].strip()
                bill['bill_month']=d[5]
                bill['consumer_number']=d[1]
                bill['bill_unit']=d[2]
                print(bill)
                bills.append(bill)
        return bills

    def getData(self):
        self.executeGet()
        self.executePost()
        self.bills= self.consumer_parser()


dotenv.load_dotenv()
targetUrl='https://wss.mahadiscom.in/wss/wss?uiActionName=getCustAccountLogin'
apiKalwa=MahadiscomApi(targetUrl=targetUrl,username=os.environ.get('KALWA_USERNAME'),password=os.environ.get('KALWA_PASSWORD'))
# apiKalwa.getData()