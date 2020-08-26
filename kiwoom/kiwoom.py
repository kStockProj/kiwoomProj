from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
#QAxWidget에 있는 것들을 전부 사용하겠다.
class Kiwoom(QAxWidget) :
    def __init__(self):
        super().__init__() #QAxWidget에 있는 메소드를 사용하기 위해 초기화
        print('키움 Class 입니다')
        #eventLoop 모듈
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()
        ################

        #스크린변수모음##
        self.screen_my_info = "2000"
        self.screen_day_info = "3000"
        self.screen_calculation_stock = "4000"
        ##############

        #변수모음 ########
        self.account_num = None
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        #################

        ######종목분석용#####
        self.calcul_data = []
        ###################

        ###계좌관련변수 ####
        self.use_money = 0
        self.use_money_percent= 0.5
        ###############

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commconnect()
        self.get_account_info()
        self.detail_account_info() # 예수금 가져오기
        self.detail_account_mystock() # 계좌평가잔고내역요청 가져오기
        self.not_concluded_account() #미체결 요청
        self.calculator_fnc() #종목 분석용, 임시용

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1") # 레지스트리에 저장된 api 모듈 불러오기

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)

    def signal_login_commconnect(self):
        self.dynamicCall('CommConnect()') #다른 응용프로그램에 전송을 할 수 있게끔 하는 함수
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def login_slot(self, errCode):
        print(errors(errCode))
        self.login_event_loop.exit()

    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCLIST")
        self.account_num = account_list.split(';')[0]
        print("나의 보유 계좌번호 %s " % self.account_num) # 8142633311

    def detail_account_info(self):
        print('예수금 가져오기')
        self.dynamicCall("SetInputValue(String,String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String,String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String,String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String,String)", "조회구분", "1")
        self.dynamicCall("CommRqData(String,String,int,String)", "예수금상세현황요청","opw00001","0",self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def detail_account_mystock(self, sPrevNext="0"):
        print('계좌평가잔고내역요청')
        self.dynamicCall("SetInputValue(String,String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String,String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String,String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String,String)", "조회구분", "1")
        self.dynamicCall("CommRqData(String,String,int,String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def not_concluded_account(self, sPrevNext="0"):

        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "실시간미체결요청", "opt10075", sPrevNext,self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def trdata_slot(self, sScrNo,sRQName,sTrCode,sRecordName,sPrevNext):
        '''
        tr 요청을 받는 구역임. 슬롯
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청ID, tr코드
        :param sRecordName: 사용 안함
        :param sPrevNext: 다음 페이지가 있는지
        :return:
        '''
        if sRQName == "예수금상세현황요청" :
            deposit = self.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName, 0 ,"예수금")
            print("예수금 %s" %int(deposit))

            self.use_money = int(deposit) * self.use_money_percent
            self.use_moeny = self.use_money / 4

            ok_deposit = self.dynamicCall("GetCommData(String,String,int,String)", sTrCode, sRQName, 0, "출금가능금액")
            print(int(ok_deposit))
            self.detail_account_info_event_loop.exit()
        elif sRQName == "계좌평가잔고내역요청" :
            total_buy_money = self.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName, 0 ,"총매입금액")
            total_buy_money_result = int(total_buy_money)

            print("총매입금액 %s" %total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName, 0 ,"총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)

            print("총수익률(%%) : %s" %total_profit_loss_rate_result)


            rows = self.dynamicCall("GetRepeatCnt(QString,QString)",sTrCode,sRQName)
            cnt = 0
            print(rows)
            for i in range(rows) :
                code = self.dynamicCall("GetCommData(QString,QString,int, QString)",sTrCode,sRQName,i,"종목번호") # 출력 : A039423 // 알파벳 A는 장내주식, J는 ELW종목, Q는 ETN종목
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목명")  # 출럭 : 한국기업평가
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"보유수량")  # 보유수량 : 000000000000010
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매입가")  # 매입가 : 000000000054100
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"수익률(%)")  # 수익률 : -000000001.94
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"현재가")  # 현재가 : 000000003450
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매매가능수량")

                if code in self.account_stock_dict :
                    pass
                else :
                    self.account_stock_dict.update({code:{}})

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())

                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({'매매가능수량': possible_quantity})

                cnt += 1

                #스크롤페이징기능
                if sPrevNext == "2":
                    self.detail_account_mystock(sPrevNext="2")
                else:
                    self.detail_account_info_event_loop.exit()

            self.detail_account_info_event_loop.exit()

        elif sRQName == "실시간미체결요청":
            print('실시간미체결요청')
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문상태")  # 접수,확인,체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문구분")  # -매도, +매수, -매도정정, +매수정정
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                self.not_account_stock_dict[order_no].update({'종목코드': code})
                self.not_account_stock_dict[order_no].update({'종목명': code_nm})
                self.not_account_stock_dict[order_no].update({'주문번호': order_no})
                self.not_account_stock_dict[order_no].update({'주문상태': order_status})
                self.not_account_stock_dict[order_no].update({'주문수량': order_quantity})
                self.not_account_stock_dict[order_no].update({'주문가격': order_price})
                self.not_account_stock_dict[order_no].update({'주문구분': order_gubun})
                self.not_account_stock_dict[order_no].update({'미체결수량': not_quantity})
                self.not_account_stock_dict[order_no].update({'체결량': ok_quantity})

                self.logging.logger.debug("미체결 종목 : %s "  % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()

        elif sRQName == "주식일봉차트조회":

            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            # data = self.dynamicCall("GetCommDataEx(QString, QString)", sTrCode, sRQName)
            # [[‘’, ‘현재가’, ‘거래량’, ‘거래대금’, ‘날짜’, ‘시가’, ‘고가’, ‘저가’. ‘’], [‘’, ‘현재가’, ’거래량’, ‘거래대금’, ‘날짜’, ‘시가’, ‘고가’, ‘저가’, ‘’]. […]]
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print(cnt)
            #print('%s일봉데이터 요청' %code)

            #한번 조회하면 600일치의 일봉데이터를 볼 수 있음.
            print("데이터 일수 %s" % cnt)
            for i in range(cnt) :
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"현재가")  # 출력 : 000070
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"거래량")  # 출력 : 000070
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"거래대금")  # 출력 : 000070
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"일자")  # 출력 : 000070
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"시가")  # 출력 : 000070
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"고가")  # 출력 : 000070
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"저가")  # 출력 : 000070

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")
                #getCommDataEx를 쓰면 이 방법을 사용하지 않아도 됨.
                self.calcul_data.append(data.copy())
            #print(self.calcul_data)
            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else :
                #원하는 종목만 보고싶다.
                print(self.calcul_data)
                pass_success = False
                # 120일 이평선을 그릴만큼의 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False

                else:
                    # 120일 이평선의 최근 가격 구함
                    total_price = 0
                    for value in self.calcul_data[:120]:
                        total_price += int(value[1])
                    moving_average_price = total_price / 120

                    # 오늘자 주가가 120일 이평선에 걸쳐있는지 확인
                    bottom_stock_price = False
                    check_price = None
                    #6:고가 7:저가
                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                        print("오늘 주가 120이평선 아래에 걸쳐있는 것 확인")
                        bottom_stock_price = True
                        check_price = int(self.calcul_data[0][6]) #현재기준 '고가'가 과거기준 '저가'보다 높아야 하는 case를 찾아야함.
                                                                  #그랜빌의 매수법칙 참조할 것 .

                        # 과거 일봉 데이터를 조회하면서 120일 이평선보다 주가가 계속 밑에 존재하는지 확인
                        prev_price = None
                        if bottom_stock_price == True:

                            moving_average_price_prev = 0
                            price_top_moving = False
                            idx = 1
                            while True:

                                if len(self.calcul_data[idx:]) < 120:  # 120일치가 있는지 계속 확인
                                    print("120일치가 없음")
                                    break

                                total_price = 0
                                for value in self.calcul_data[idx:120 + idx]:
                                    total_price += int(value[1])
                                moving_average_price_prev = total_price / 120

                                if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 5:
                                    print("5일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
                                    price_top_moving = False
                                    break

                                elif int(self.calcul_data[idx][
                                             7]) > moving_average_price_prev and idx > 5:  # 120일 이평선 위에 있는 구간 존재
                                    print("120일치 이평선 위에 있는 구간 확인됨")
                                    price_top_moving = True
                                    prev_price = int(self.calcul_data[idx][7])
                                    break

                                idx += 1
                            # 해당부분 이평선이 가장 최근의 이평선 가격보다 낮은지 확인
                            if price_top_moving == True:
                                if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                    self.logging.logger.debug("포착된 이평선의 가격이 오늘자 이평선 가격보다 낮은 것 확인")
                                    self.logging.logger.debug("포착된 부분의 저가가 오늘자 주가의 고가보다 낮은지 확인")
                                    pass_success = True

                    if pass_success == True:
                        print("조건부 통과됨")

                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                        f = open("files/condition_stock.txt", "a", encoding="utf8")
                        f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                        f.close()


                    elif pass_success == False:
                        print("조건부 통과 못함")

                    self.calcul_data.clear() #리스트삭제
                    self.calculator_event_loop.exit()

                self.calculator_event_loop.exit()

    def get_code_list_by_market(self, market_code):
        '''
        종목코드 리스트 받기
        #0:장내, 10:코스닥
        :param market_code: 시장코드 입력
        :return:
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(';')[:-1]
        return code_list

    def calculator_fnc(self):
        '''
        종목 분석관련 함수 모음
        :return:
        '''

        code_list = self.get_code_list_by_market("10") #코스닥종목 가져오기
        print("코스닥 갯수 %s " % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기

            print("%s / %s :  KOSDAQ Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.day_kiwoom_db(code=code)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):

        QTest.qWait(3600)  # 3.6초마다 딜레이를 준다.

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext,self.screen_calculation_stock)  # Tr서버로 전송 -Transaction

        self.calculator_event_loop.exec_()
