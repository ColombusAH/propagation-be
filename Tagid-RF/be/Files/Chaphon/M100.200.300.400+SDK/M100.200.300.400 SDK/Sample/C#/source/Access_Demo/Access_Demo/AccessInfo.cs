using System.Runtime.InteropServices;

namespace Access_Demo
{
    [StructLayout(LayoutKind.Sequential)]
    public struct AccessInfo
    {
        private byte _head;
        public byte Head
        {
            get { return _head; }
            set { _head = value; }
        }

        private byte _addr;

        public byte Addr
        {
            get { return _addr; }
            set { _addr = value; }
        }

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 2)]
        private byte[] _cmd;

        public byte[] Cmd
        {
            get { return _cmd; }
            set { _cmd = value; }
        }

        private byte _len;

        public byte Len
        {
            get { return _len; }
            set { _len = value; }
        }

        private byte _status;

        public byte Status
        {
            get { return _status; }
            set { _status = value; }
        }

        private byte _state;

        public byte State
        {
            get { return _state; }
            set { _state = value; }
        }

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 32)]
        private byte[] _customerInfo;

        public byte[] CustomerInfo
        {
            get { return _customerInfo; }
            set { _customerInfo = value; }
        }

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 2)]
        private byte[] _check;

        public byte[] Check
        {
            get { return _check; }
            set { _check = value; }
        }

    }
}
