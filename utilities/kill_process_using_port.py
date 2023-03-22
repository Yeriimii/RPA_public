import subprocess
import re

def kill_process_using_port(port):
    try:
        output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True, text=True)
        pid = re.search(r'\s+([0-9]+)$', output.strip()).group(1)
        if pid:
            subprocess.call(f'taskkill /F /PID {pid}', shell=True)
    except subprocess.CalledProcessError:
        print(f'No process found using port {port}')

if __name__ == '__main__':
    kill_process_using_port(9222)
