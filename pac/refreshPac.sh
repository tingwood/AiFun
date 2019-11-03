# http proxy 	:	PROXY IP:port
# https proxy	:	HTTPS IP:port
# socks5 proxy	:	SOCKS5 IP:port
genpac --proxy="PROXY 192.168.8.101:3128" --gfwlist-proxy="PROXY 192.168.8.101:3128" -o autoproxy.pac --gfwlist-url="https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"
