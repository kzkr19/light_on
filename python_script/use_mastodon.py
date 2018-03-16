from mastodon import Mastodon
from getpass import getpass
import os.path
import sys
import time

CLIENT_ID = './appconfig.secret'
DOMAIN = 'https://mstdn.jp'
ACCESS_TOKEN = './access_token.secret'
SINCE_ID_LOG = "./since_id.txt"


def create_app():
    """
    新しくアプリケーションを作成し，client idを発行する
    """
    
    print("input your new application name:")
    client_name = input()
    
    Mastodon.create_app(
        client_name,
        api_base_url = DOMAIN,
        to_file = CLIENT_ID
    )

def login():
    mastodon = Mastodon(
        client_id = CLIENT_ID,
        api_base_url = DOMAIN
    )
    
    print("input mail address and password")
    print("Email: ",end="")
    mail = input()
    pw   = getpass()
    
    try:
        mastodon.log_in(
            mail,
            pw,
            to_file = ACCESS_TOKEN
        )
    except:
        print("Error: Input correct mail address or password.")
        sys.exit(0)

def get_mastodon_instance():
    # client_id未発行の場合は作成する
    if not os.path.isfile(CLIENT_ID):
        create_app()

    # アクセストークン未取得の場合はログインする
    if not os.path.isfile(ACCESS_TOKEN):
        login()
    
    # インスタンスを作成
    mastodon = Mastodon(
        client_id = CLIENT_ID,
        access_token = ACCESS_TOKEN,
        api_base_url = DOMAIN
    )
    
    return mastodon

def read_since_id():
    ret = None
    if os.path.isfile( SINCE_ID_LOG):
        try:
            with open(SINCE_ID_LOG,"r") as f:
                ret = int(f.readline())
        except:
            ret = None
    
    return ret

def write_since_id(id):
    try:
        with open(SINCE_ID_LOG,"w") as f:
            f.write(str(id))
            f.write("\n")
    except:
        pass

def get_my_id(mastodon):
    ret = mastodon.status_post(
        u'Executed application at ' + time.ctime(),
        visibility='unlisted')
    return ret["account"]["id"]
