import time
from serial.android import get_android_context
from com.hoho.android.usbserial.driver import UsbSerialProber, UsbSerialPort
from java.lang import UnsupportedOperationException
from com.lemote.sunlighten import USBHelper
from java.io import IOException
from serial.serialutil import SerialBase, SerialException, PortNotOpenError


class Serial(SerialBase):

    def open(self):
        if self._port is None:
            raise SerialException("Port must be configured before it can be used.")
        if self.is_open:
            raise SerialException("Port is already open.")
        context = get_android_context()
 
        # usb_manager = context.getSystemService(context.USB_SERVICE)
        # available_drivers = UsbSerialProber.getDefaultProber().findAllDrivers(usb_manager)
        # if not available_drivers:
        #     raise SerialException("No USB serial device found.")
        # print("available_drivers:" + str(available_drivers))
        # self.driver = available_drivers.get(0)
        # connection = usb_manager.openDevice(self.driver.getDevice())
        # if connection is None:
        #     raise SerialException("Could not open connection to device.")
        # self.fd = connection.getFileDescriptor()
        # print("fd:" + str(self.fd))
        # self.mik3yPort = self.driver.getPorts().get(0)
        
        # print("mik3yPort:started")
        # self.mik3yPort.open(connection)

        self._reconfigure_port()
        self.is_open = True

    def _reconfigure_port(self):

        # Map bytesize to UsbSerialPort constants
        if self._bytesize == 5:
            dataBits = UsbSerialPort.DATABITS_5
        elif self._bytesize == 6:
            dataBits = UsbSerialPort.DATABITS_6
        elif self._bytesize == 7:
            dataBits = UsbSerialPort.DATABITS_7
        elif self._bytesize == 8:
            dataBits = UsbSerialPort.DATABITS_8
        else:
            raise ValueError("unsupported bytesize: %r" % self._bytesize)

        # Map stopbits to UsbSerialPort constants
        if self._stopbits == 1:
            stopBits = UsbSerialPort.STOPBITS_1
        elif self._stopbits == 1.5:
            stopBits = UsbSerialPort.STOPBITS_1_5
        elif self._stopbits == 2:
            stopBits = UsbSerialPort.STOPBITS_2
        else:
            raise ValueError("unsupported number of stopbits: %r" % self._stopbits)

        # Map parity to UsbSerialPort constants
        if self._parity == 'N':
            parity = UsbSerialPort.PARITY_NONE
        elif self._parity == 'E':
            parity = UsbSerialPort.PARITY_EVEN
        elif self._parity == 'O':
            parity = UsbSerialPort.PARITY_ODD
        elif self._parity == 'M':
            parity = UsbSerialPort.PARITY_MARK
        elif self._parity == 'S':
            parity = UsbSerialPort.PARITY_SPACE
        else:
            raise ValueError("unsupported parity type: %r" % self._parity)

        # Set the parameters on the port
        # print("setParametersPy " + str(self._baudrate) + " " + str(dataBits) + " " + str(stopBits) + " " + str(parity))
        USBHelper.setParametersPy(self._baudrate, dataBits, stopBits, parity)
        USBHelper.setDTRPy(True)
        USBHelper.setRTSPy(True)
        

    def _update_rts_state(self):
        USBHelper.setRTSPy(bool(self._rts_state))

    def _update_dtr_state(self):
        USBHelper.setDTRPy(bool(self._dtr_state))

    def close(self):
        if self.is_open:
            # USBHelper.closePort()
            self.is_open = False

    def read(self, size=16 * 1024):
        if size == -1:
            size = 16 * 1024
        data = bytearray(size)
        timeout2 = self._timeout if self._timeout is not None else 0
        # print("read timeout:" + str(self._timeout))
        # print("read timeout2:" + str(timeout2))
        if timeout2 != 0:
            if timeout2 > 3:
                time.sleep(timeout2)
            else:
                time.sleep(0.5)
            
        collected_bytes = bytes(USBHelper.getCollectedBytesForPython())
        # print("collected_bytes:" + str(len(collected_bytes)))
        # print(f"collected_bytes: hex={collected_bytes.hex()}, str={collected_bytes.decode('utf-8', errors='replace')}")
        return collected_bytes
        # try:
        #     num_bytes_read = self.mik3yPort.read(data, timeout)
        #     received_data = data[:num_bytes_read]
        #     print(f"num_bytes_read: hex={received_data.hex()}, str={received_data.decode('utf-8', errors='replace')}")
        #     return bytes(data[:num_bytes_read])
        # except IOException as e:
        #     print(f"Error reading data: {e}")
        #     return None

    def write(self, data):
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError('expected bytes or bytearray, got %s' % type(data))
        USBHelper.writeBytesPy(data)
        return len(data)

    def reset_input_buffer(self):
       return
        # print("reset_input_buffer")

    def reset_output_buffer(self):
        return
        # print("reset_output_buffer")
        # if not self.mik3yPort:
        #     raise SerialException("Port not open")
        # try:
        #     self.mik3yPort.purgeHwBuffers(False, True)
        # except UnsupportedOperationException:
        #     print("Warning: Purging output buffer is not supported on this device.")

    def send_break(self, duration=0.25):
        USBHelper.setBreakPy(True)
        time.sleep(duration)
        USBHelper.setBreakPy(False)

    def fileno(self):
        """\
        For easier use of the serial port instance with select.
        WARNING: this function is not portable to different platforms!
        """
        FD=USBHelper.getFdPy()
        return FD

    @property
    def in_waiting(self):
        return -1

    @property
    def cts(self):
        return USBHelper.getCtsPy()

    @property
    def dsr(self):
        return USBHelper.getDsrPy()

    @property
    def ri(self):
        return USBHelper.getRiPy()

    @property
    def cd(self):
        return USBHelper.getCdPy()
