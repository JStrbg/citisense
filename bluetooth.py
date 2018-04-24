# - automate the agent for running on a headless Pi - to answer pair and connection requests without a blocking query

import dbus
import dbus.service
import dbus.mainloop.glib
import bluezutils

BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/test/agent"

bus = None
device_obj = None
dev_path = None

def set_trusted(path):
    props = dbus.Interface(bus.get_object("org.bluez", path),
                    "org.freedesktop.DBus.Properties")
    props.Set("org.bluez.Device1", "Trusted", True)

def dev_connect(path):
    dev = dbus.Interface(bus.get_object("org.bluez", path),
                            "org.bluez.Device1")
    dev.Connect()

class Rejected(dbus.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
    exit_on_release = True

    def set_exit_on_release(self, exit_on_release):
        self.exit_on_release = exit_on_release

    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="", out_signature="")
    def Release(self):
        printlog("Release")
        if self.exit_on_release:
            mainloop.quit()

    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        printlog("AuthorizeService (%s, %s)" % (device, uuid))
        authorize = "yes" #ask("Authorize connection (yes/no): ")
        if (authorize == "yes"):
            return
        raise Rejected("Connection rejected by user")

    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        printlog("RequestPinCode (%s)" % (device))
        set_trusted(device)
        return "0000" #ask("Enter PIN Code: ")

    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        printlog("RequestPasskey (%s)" % (device))
        set_trusted(device)
        passkey = "0000" #ask("Enter passkey: ")
        return dbus.UInt32(passkey)

    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        printlog("DisplayPasskey (%s, %06u entered %u)" %
                        (device, passkey, entered))

    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        printlog("DisplayPinCode (%s, %s)" % (device, pincode))

    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        printlog("RequestConfirmation (%s, %06d)" % (device, passkey))
        confirm = "yes" #ask("Confirm passkey (yes/no): ")
        if (confirm == "yes"):
            set_trusted(device)
            return
        raise Rejected("Passkey doesn't match")

    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        printlog("RequestAuthorization (%s)" % (device))
        auth = "yes" #ask("Authorize? (yes/no): ")
        if (auth == "yes"):
            return
        raise Rejected("Pairing rejected")

    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="", out_signature="")
    def Cancel(self):
        printlog("Cancel")
