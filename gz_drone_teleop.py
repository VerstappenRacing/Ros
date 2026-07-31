import sys, select, termios, tty
import subprocess
import time

msg = """
========================================
    🚀 드론 전용 WASDQE 컨트롤러
========================================
   [E] : 상승 (Up)      | [Q] : 하강 (Down)
   [W] : 전진 (Forward) | [S] : 후진 (Back)
   [A] : 좌로 이동      | [D] : 우로 이동
   [J] : 좌회전         | [L] : 우회전
   [SPACE] : 제자리 정지

   CTRL-C : 종료
========================================
"""

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
    key = rlist[0].read(1) if rlist else ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def send_cmd(x, y, z, yaw):
    # Enable 신호와 cmd_vel을 Gazebo로 직접 전송
    cmd_enable = 'gz topic -t "/drone/enable" -m gz.msgs.Boolean -p "data: true"'
    cmd_vel = f'gz topic -t "/drone/cmd_vel" -m gz.msgs.Twist -p "linear: {{x: {x}, y: {y}, z: {z}}}, angular: {{z: {yaw}}}"'
    subprocess.Popen(cmd_enable, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(cmd_vel, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    settings = termios.tcgetattr(sys.stdin)
    print(msg)
    
    speed = 3.0 # 이동 속도
    
    try:
        while True:
            key = get_key(settings)
            x, y, z, yaw = 0.0, 0.0, 0.0, 0.0
            
            if key == 'w': x = speed
            elif key == 's': x = -speed
            elif key == 'a': y = speed
            elif key == 'd': y = -speed
            elif key == 'e': z = speed
            elif key == 'q': z = -speed
            elif key == 'j': yaw = 1.0
            elif key == 'l': yaw = -1.0
            elif key == ' ': x, y, z, yaw = 0.0, 0.0, 0.0, 0.0
            elif key == '\x03': break
            
            if key != '':
                send_cmd(x, y, z, yaw)
                print(f"\r[조작 중] 입력키: {key.upper()} | Z축속도: {z} | X축속도: {x}   ", end="")
            time.sleep(0.02)
            
    except Exception as e:
        print(e)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

if __name__ == '__main__':
    main()
