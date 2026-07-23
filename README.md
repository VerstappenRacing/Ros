# Ros
로보티즈 로봇팔


---

#20260720
wsl 설치 (Ubuntu 24.04)
github아이디 만들고 repository 생성
git clone 을 해서 wsl에 복사
VSC 설치 후 remote wsl로 접속
github 계정연동
ros2 설치 - Jazzy

ros multyprocess 정보를 주고받음
IPC

#20260721
ROS2 common pakages-RCL
DDS: OMG에서 표준화한 실시간 발간자-구독자 방식 통신 미들웨어
Node:최소 단위의 실행 가능한 프로세스.

#20260723
*DDS설정 wsl ----> mirror-net 방화벽
*interface[type] ---> message(topic, service, action)
    ros2 기본제공. user.interface [idl] service [request
                                                response]
    idl은 cpp기반. cmake 패키지 필요.
*topic (UserInt). service (AddAndOdd) server 동기 <-------> client 비동기 (특정상황에서 반복)
    service는 주기적인 센서 확인. 반복적으로 확인.
    thread_server 순차적

parameter 변수. process 여러개 운동
    환경변수 .yaml
    내부변수. 파라미터 변수 (독립적으로) DDS -->외부노드, CLI로 변경 가능.

launch
    노드 여러개
    파라미터 로드(파라미터, 파일 붙여넣기 .yaml)