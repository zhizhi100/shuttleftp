# -*- coding: utf-8 -*-
'''
Created on 2016年5月4日

@author: ZhongPing
'''
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.authorizers import AuthenticationFailed
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.filesystems import FilesystemError
from pyftpdlib.log import logger
import filemd5

def _strerror(err):
    if isinstance(err, EnvironmentError):
        try:
            return os.strerror(err.errno)
        except AttributeError:
            # not available on PythonCE
            if not hasattr(os, 'strerror'):
                return err.strerror
            raise
    else:
        return str(err)

class MyHandler(FTPHandler):
    
    def ftp_DELE(self, path):
        """Delete the specified file.
        On success return the file path, else None.
        """
        try:
            print 'try to delete file:'+path
            self.run_as_current_user(self.fs.remove, path)
        except (OSError, FilesystemError) as err:
            why = _strerror(err)
            self.respond('550 %s.' % why)
        else:
            self.respond("250 File removed.")
            return path    
    
    def readfile(self,file):
        file_object = open(file)
        try:
            all_the_text = file_object.read( )
        finally:
            file_object.close( )
        return all_the_text

    def on_connect(self):
        #print "%s:%s connected" % (self.remote_ip, self.remote_port)
        pass

    def on_disconnect(self):
        # do something when client disconnects
        pass

    def on_login(self, username):
        # do something when user login
        pass

    def on_logout(self, username):
        # do something when user logs out
        pass

    def on_file_sent(self, file):
        # do something when a file has been sent
        print 'on sent'
        print self.readfile(file)

    def on_file_received(self, file):
        # do something when a file has been received
        print 'on receive'
        print file
        print self.readfile(file)

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        pass

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        #import os
        #os.remove(file)
        pass

class MyAuthorizer(DummyAuthorizer):
    
    def validate_authentication(self,username, password, handler):
        msg = "Authentication failed."
        if not password == '123456':
            if username == 'anonymous':
                msg = "Anonymous access not allowed."
            raise AuthenticationFailed(msg)
        #if username != 'anonymous':
        #   if self.user_table[username]['pwd'] != password:
        #        raise AuthenticationFailed(msg)
        if not self.has_user(username):
            self.add_user(username, password, "e://test2/", perm="elradfmw")
            
class MyFTPServer(FTPServer):
    
    def serve_forever(self, timeout=None, blocking=True, handle_exit=True):
        if handle_exit:
            log = handle_exit and blocking
            if log:
                self._log_start()
            try:
                self.ioloop.loop(timeout, blocking)
            except (KeyboardInterrupt, SystemExit):
                logger.info("received interrupt signal")
            if blocking:
                if log:
                    logger.info(
                        ">>> shutting down FTP server (%s active socket "
                        "fds) <<<",
                        self._map_len())
                self.close_all()
        else:
            self.ioloop.loop(timeout, blocking)

def main():
        
    authorizer = MyAuthorizer()
    authorizer.add_user("user", "12345", "e://test2/", perm="elradfmw")
    
    handler = MyHandler
    handler.authorizer = authorizer
    
    server = FTPServer(("127.0.0.1", 21), handler)
    server.serve_forever()


if __name__ == '__main__':
    main()