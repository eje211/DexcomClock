# This is a sample Python script.
from typing import Optional, Awaitable
import asyncio
from datetime import datetime, timedelta
from configparser import ConfigParser
from urllib.parse import urlencode

from tornado.web import RequestHandler, Application, StaticFileHandler
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.ioloop import  IOLoop
from sanction import _default_parser as parser

PRODUCTION_SERVER = "api.dexcom.com"
DEV_SERVER = "sandbox-api.dexcom.com"
CURRENT_SERVER = DEV_SERVER

credentials = ConfigParser()

CONFIG = {
    'CLIENT_ID': credentials['OAuth']['CLIENT_ID'],
    'CLIENT_SECRET': credentials['OAuth']['CLIENT_SECRET'],
    'REDIRECT': 'http://4.tcp.ngrok.io:14519/redirect',
    'GLUCOSE_CHECK': f'https://{CURRENT_SERVER}/v2/users/self/egvs'
}


http_client = AsyncHTTPClient()


class Redirect(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):

        try:
            code = self.request.arguments['code'][0].decode('utf8')
            self.set_header('content-type', "application/x-www-form-urlencoded")
            self.set_header('cache-control', "no-cache")
            WebApp.oauthClient.request_token(
                code=code, redirect_uri=CONFIG['REDIRECT'], grant_type='authorization_code',
                parser=parser)
            self.redirect('/updateglucose')
        except KeyError:
            pass

    def get_token(self, token):
        pass


class StartOAuth(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):
        self.redirect(WebApp.oauthClient.auth_uri(
            scope="offline_access", response_type="code", redirect_uri=CONFIG['REDIRECT']))


class Connect(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):
        print(WebApp.oauthClient.access_token)
        print(WebApp.oauthClient.token_expires)


class UpdateGlucose(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):
        query = {
            'startDate': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'endDate': datetime.now().isoformat(),
        }
        URI = f"{CONFIG['GLUCOSE_CHECK']}?{urlencode(query)}"
        print(URI)
        IOLoop.current().add_callback(self.get_glucose, URI)

    async def get_glucose(self, URI):
        print(f'Token: {WebApp.oauthClient.access_token}')
        request = HTTPRequest(URI,
                    headers={'authorization': f'Bearer: {WebApp.oauthClient.access_token}'})
        response = await http_client.fetch(request)
        self.write(response.body)

class WebApp:
    from sanction import Client

    application: Optional[Application] = None
    oauthClient = Client(token_endpoint=f"https://{CURRENT_SERVER}/v2/oauth2/token",
                    resource_endpoint=f"https://{CURRENT_SERVER}/v2/oauth2/login",
                    client_id=CONFIG["CLIENT_ID"],
                    client_secret=CONFIG["CLIENT_SECRET"],
                    auth_endpoint=f"https://{CURRENT_SERVER}/v2/oauth2/login")

    @classmethod
    async def start(cls):
        from os import getcwd

        cls.application = Application([
            ('/redirect', Redirect),
            ('/connect', Connect),
            ('/startoauth', StartOAuth),
            ('/updateglucose', UpdateGlucose),
            (r'/static/(.*)', StaticFileHandler, {'path': getcwd() + '/static'})
        ])
        cls.application.listen(8888)
        await asyncio.Event().wait()

    def __new__(cls):
        asyncio.run(cls.start())


if __name__ == '__main__':
    WebApp()
