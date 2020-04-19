# http proxy 	:	PROXY IP:port
# https proxy	:	HTTPS IP:port
# socks5 proxy	:	SOCKS5 IP:port
GFW_URL=https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt
HOST="192.168.8.101"
HTTP_PROXY="PROXY $HOST:3128"
SOCKS_PROXY="SOCKS5 $HOST:1080"
echo $HTTP_PROXY
echo $SOCKS_PROXY
genpac --proxy="$HTTP_PROXY" --gfwlist-proxy="$HTTP_PROXY"   -o ./static/proxy.pac --gfwlist-url="$GFW_URL"
genpac --proxy="$SOCKS_PROXY" --gfwlist-proxy="$SOCKS_PROXY" -o ./static/socks.pac --gfwlist-url="$GFW_URL"
