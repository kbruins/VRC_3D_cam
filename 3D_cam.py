import asyncio
import struct
from pythonosc import udp_client, osc_server, dispatcher


MESSAGE_ADDRESS = "/avatar/parameters/"

# movement multipliers. increasing the number will increase sensitivity for that tracking axis. - will invert the axis.
X_MULTIPLIER = 1.0  # side to side
Y_MULTIPLIER = 1.0  # up and down
Z_MULTIPLIER = 1.0  # depth


class OSCHandler:
    """basic class for handling osc connections"""
    def __init__(self, default_handler, ip="127.0.0.1", server_port=9001, client_port=9000):
        self.ip = ip
        self.server_port = server_port
        self.client_port = client_port
        self.mapper = dispatcher.Dispatcher()
        self.mapper.set_default_handler(default_handler)
        self.client = udp_client.SimpleUDPClient(address=self.ip, port=self.client_port)
        self.server: osc_server.AsyncIOOSCUDPServer | None = None
        self.transport: asyncio.Transport | None = None
        self.data_send = False
        self.synced_params = {}

    def start_server(self, loop: asyncio.AbstractEventLoop):
        """creates a asyncIO server"""
        # noinspection PyTypeChecker
        self.server = osc_server.AsyncIOOSCUDPServer((self.ip, self.server_port), self.mapper, loop)
        return self.server

    def stop(self):
        """closes asyncIO"""
        if self.transport is not None:
            self.transport.close()

    def send_param(self, location: str, value):
        """send a value to a avatar parameter"""
        self.client.send_message(MESSAGE_ADDRESS + location, value)

    def send_synced(self, location: str, value):
        """same as send param but only 5 times per second for synced params"""
        self.synced_params[location] = value

    def send_update(self):
        """called 5 times per second to send any synced parameters"""
        self.data_send = not self.data_send
        for key, value in self.synced_params.items():
            self.send_param(key, value)
        self.send_param("data_receive", self.data_send)
        self.synced_params.clear()


class HeadTracker:
    """class for head tracker/3D cam"""
    def __init__(self, osc: OSCHandler):
        self.osc = osc
        # if you want to use head tracking data you can use read from this dictionary.
        self.transform = {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0, "pitch": 0.0, "roll": 0.0}
        self.active = False

    def on_udp(self, udp_message):
        """ran whenever a udp message has been received about head tracking data"""
        # decode UDP message
        for i, label in enumerate(["x", "y", "z", "yaw", "pitch", "roll"]):
            self.transform[label] = struct.unpack('d', udp_message[i*8:(i+1)*8])[0]

        # send osc parameters if 3D cam is active
        if self.active:
            x = (self.transform["x"]/300)*X_MULTIPLIER
            y = (self.transform["y"]/300)*Y_MULTIPLIER
            z = (self.transform["z"]/150)*Z_MULTIPLIER
            self.osc.send_param("cam_x", min(max(x+0.5, 0.0), 1.0))
            self.osc.send_param("cam_y", min(max(y+0.5, 0.0), 1.0))
            self.osc.send_param("cam_z", min(max(z, 0.0), 1.0))


class SyslogProtocol(asyncio.DatagramProtocol):
    """class for receiving udp messages from opentrack"""
    message_dest: None | HeadTracker = None

    def __init__(self):
        super().__init__()
        self.transport: None | asyncio.BaseTransport = None

    def connection_made(self, transport: asyncio.BaseTransport):
        self.transport = transport

    @classmethod
    def datagram_received(cls, data, addr):
        # Here is where you would push message to whatever methods/classes you want.
        # print(f"Received Syslog message: {data}")
        cls.message_dest.on_udp(data)


def main():
    print("VRC 3D cam starting up...")

    def on_3d_cam(arg):
        tracker.active = arg[0] == 1.0

    def on_recv(address: str, *args: any) -> None:
        """put in your code you want to run when osc data is received"""
        if not address.startswith(MESSAGE_ADDRESS):
            if address == "/avatar/change":
                # avatar was changed. ignore event
                return
            print(f"unknown path! path: {address}, arguments: {args}. other programs might be sending on this port.")
            return
        parameter = address[19:]  # remove header (/avatar/change) from the string to get the parameter

        try:
            osc_functions[parameter](args)  # try executing the function defined for this address
        except KeyError:
            pass

    async def start_osc():
        print("opening OSC...")
        loop = asyncio.get_event_loop()
        server = osc.start_server(loop)
        osc.transport, protocol = await server.create_serve_endpoint()
        print("OSC ready, starting UDP...")
        # receiver for opentrack data. default: ip=127.0.0.1 port=8000
        transport, _ = await loop.create_datagram_endpoint(SyslogProtocol, local_addr=('127.0.0.1', 8000))
        print("UDP open, startup complete. activate the 3D cam toggle in expression menu to activate 3D cam")

        await main_loop()

        osc.stop()
        transport.close()

    async def main_loop():
        nonlocal run
        try:
            while run:
                # put in code that you want to run on a timely basis
                await asyncio.sleep(loop_time)
        except KeyboardInterrupt:
            run = False
            print("closing")

    # setup variables
    loop_time = 0.2  # main loop runs at 5 times per second
    osc = OSCHandler(on_recv)
    tracker = HeadTracker(osc)
    SyslogProtocol.message_dest = tracker

    osc_functions = {"3D_cam": on_3d_cam}

    run = True

    # start connections and begin loop
    asyncio.run(start_osc())


if __name__ == "__main__":
    main()
