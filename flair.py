import logging
import time
from http.client import HTTPConnection
from threading import Thread

from app import run_app
import webview

logger = logging.getLogger(__name__)

error = False
status = False


def get_user_agent(window):
    result = window.evaluate_js(r"""
        // Return user agent
        'User agent:\n' + navigator.userAgent;
        """)
    print(result)


def is_server_running(url, port, max_wait):
    global error
    global status
    time.sleep(0.4)
    start = time.time()
    while True:
        try:
            end = time.time()
            if end - start > max_wait:
                return False
            time.sleep(0.1)
            connection = HTTPConnection(url, port)
            request, response = connection.request("GET", "/"), connection.getresponse()
            if response is not None:
                status = response.status
                return True
        except Exception as e:
            error = e
            logger.exception("Server not yet running")


def main():
    url, port, max_wait = '127.0.0.1', 43968, 15  # 15 seconds
    link = "http://" + url + ":" + str(port)
    # Starting Server
    server_thread = Thread(target=run_app, args=(url, port))
    server_thread.daemon = True
    server_thread.start()
    # Waiting for server to load content
    if is_server_running(url, port, max_wait):
        logger.debug("Server started")
        # webbrowser.open(link, new=2)
        # while server_thread.is_alive():
        #     time.sleep(0.1)
        window = webview.create_window("Flair App", link, min_size=(640, 480))
        webview.start(get_user_agent, window)
    else:
        logger.debug("Server failed to start with a max wait time of " + str(max_wait))
        if status is not False:
            logger.debug("Status was " + str(status))
        if error is not False:
            logger.debug("Exception was " + str(error))
    logger.debug("Server has exited")


if __name__ == '__main__':
    main()