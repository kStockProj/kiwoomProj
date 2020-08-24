from kiwoom.kiwoom import *
from PyQt5.QtWidgets import *
import sys
class UI_class() :
    def __init__(self):
        print('UI_class 입니다')
        #Application을 실행시키기 위한 함수.
        #argv = ['파이썬파일경로','추가할옵션1','추가할옵션2'] 즉 프로그로밍 하는 파이썬경로가 담겨있음.
        self.app = QApplication(sys.argv)
        self.kiwoon = Kiwoom()

        self.app.exec_() #프로그램을 종료시키지 않기 위한 함수