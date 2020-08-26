1. 커뮤니티 툴
트렐로 사용

2.개념
- 쓰레드
- PyQt5(GUI용으로 사용했었음)
>1000여개의 기능이 있음.  ex) QEventLoop() 이벤트루프 가능.
                                       단점 : Block기능이 있음.

3. 가상화에 대해?
- 가상환경으로 32비트와 64비트를 나눠서 써야함
(32비트 환경에서만 돌리면 tensorflow가 제대로 동작할 수 없음)
http://stackoverflow.com/questions/33709391/using-multiple-python-engines-32bit-64bit- and-2-7-3-5
>
32비트 가상환경

1)  set CONDA_FORCE_32BIT = 1
2) conda create -n py37_32 python3.7 anaconda
3) activate py37_32

- 64비트 가상환경 
: conda create -n py37_64 python3.7 anaconda

4. git  연동방법
https://blog.naver.com/norankoj/221286289683

*참고
<주식삽질기>
https://www.slideshare.net/cybrshin/ss-77492097
<유튜브>
#프로그램동산 채널

