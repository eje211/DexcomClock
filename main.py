# This is a sample Python script.
from typing import Optional, Awaitable, List
import asyncio
from datetime import datetime
from datetime import timedelta

from tornado.web import RequestHandler, Application, StaticFileHandler
from tornado.httpclient import HTTPRequest, HTTPClient
from sanction import _default_parser as parser


CONFIG = {
    'CLIENT_ID': 'PiKbg9eAY7KKBx8fI0BKxi6GcLKoTWEV',
    'CLIENT_SECRET': 'yex6ajKYRekqVFoq',
    'REDIRECT': 'http://0.tcp.ngrok.io:18517/redirect'
}

PRODUCTION_SERVER = "api.dexcom.com"
DEV_SERVER = "sandbox-api.dexcom.com"
CURRENT_SERVER = DEV_SERVER

http_client = HTTPClient()


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
        params = [
            ['startDate', (datetime.now() - timedelta(minutes=10)).isoformat()],
            ['endDate', datetime.now().isoformat()]
        ]
        params = ['='.join(p) for p in params]
        params = '&'.join(params)
        params = '?' + params
        URI = f"https://{CURRENT_SERVER}//v2/users/self/egvs{params}"
        print(URI)
        request = HTTPRequest(URI,
                    headers={'authorization': f'Bearer: {WebApp.oauthClient.access_token}'})
        response = http_client.fetch(request)
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
