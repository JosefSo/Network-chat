from unittest import TestCase
import time
import Client


class TestClient(TestCase):

    """
    check messages, in order to check properly first run the server and then the test
    if it doesn't work reboot the server
    """
    def test_message_out(self):
        #open 3 clients
        a = Client.Client("dan")
        self.assertEqual((a.sock.recv(1024).decode('utf-8')), 'message from Server: dan joined\n') #dan joined..
        b = Client.Client('segev')
        self.assertEqual((b.sock.recv(1024).decode('utf-8')), 'message from Server: segev joined\n') #segev joined...
        c = Client.Client('boaz')
        self.assertEqual((c.sock.recv(1024).decode('utf-8')), 'message from Server: boaz joined\n')# boaz joined..
        time.sleep(0.2)
        self.assertEqual((a.sock.recv(1024).decode('utf-8')), 'message from Server: segev joined\nmessage from Server: boaz joined\n')#segev boaz joined

        time.sleep(0.2)
        a.message_out('/pm segev hi segev') #check pm dan to segev
        a.message_out('/pm boaz hi boaz') #check pm dan to boaz

        time.sleep(0.2)
        self.assertEqual((b.sock.recv(1024).decode('utf-8')),'message from Server: boaz joined\nprivate message from dan :  hi segev') #segev get pm
        time.sleep(0.2)
        self.assertEqual((c.sock.recv(1024).decode('utf-8')), 'private message from dan :  hi boaz') #boaz get pm without segev's
        time.sleep(0.2)
        a.message_out('hi all')
        time.sleep(0.2)
        self.assertEqual((b.sock.recv(1024).decode('utf-8')), 'message from dan: hi all')
        self.assertEqual((c.sock.recv(1024).decode('utf-8')), 'message from dan: hi all')

        #recieve all the names of logged in users
        d = Client.Client('cooper')
        d.message_out('/users')
        time.sleep(0.2)

        self.assertEqual((d.sock.recv(1024).decode('utf-8')), 'message from Server: cooper joined\nOnline users: dan ,segev ,boaz \n')
        time.sleep(0.2)


        #test files list
        d.message_out('/files')
        self.assertEqual((d.sock.recv(1024).decode('utf-8')), 'File list:\n')
        time.sleep(0.2)

        d.message_out('/download catE.jpg')
        time.sleep(0.1)

        time.sleep(0.1)

        d.message_out('/download 100inNetworking.png')
        time.sleep(1)

        #disconnect
        a.message_out('/quit')
        b.message_out('/quit')
        c.message_out('/quit')
        d.message_out('/quit')


    def test_disconnect(self):
        self.fail()


