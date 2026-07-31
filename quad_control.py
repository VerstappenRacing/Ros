import sys, select, termios, tty, subprocess, time

msg = """
========================================
   🚁 진짜 쿼드콥터 모터 직접 조종기
========================================
   [E] : 4개 모터 회전수 상승 (출력 업 -> 상승)
   [Q] : 4개 모터 회전수 하강 (출력 다운 -> 하강)
   [SPACE] : 모터 정지 (출력 0)

   CTRL-C : 종료
========================================
"""

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
    key = rlist[0].read(1) if rlist else ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def send_motor_speed(rpm):
    cmd = f'gz topic -t "/quadcopter/command/motor_speed" -m gz.msgs.Actuators -p "velocity: [{rpm}, {rpm}, {rpm}, {rpm}]"'
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    settings = termios.tcgetattr(sys.stdin)
    print(msg)
    
    rpm = 0.0
    
    try:
        while True:
            key = get_key(settings)
            
            if key == 'e':
                rpm += 20.0
            elif key == 'q':
                rpm = max(0.0, rpm - 20.0)
            elif key == ' ':
                rpm = 0.0
            elif key == '\x03':
                break
                
            send_motor_speed(rpm)
            if key != '':
                print(f"\r[모터 RPM 출력]: {rpm:.1f} rad/s    ", end="")
            time.sleep(0.02)
            
    except Exception as e:
        print(e)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

if __name__ == '__main__':
    main()
