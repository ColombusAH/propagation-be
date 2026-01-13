using System;
using System.Runtime.InteropServices;

namespace Access_Demo
{
    [StructLayout(LayoutKind.Sequential)]
    public struct WhiteListParam
    {
        private byte _STATUS;

        public byte STATUS
        {
            get { return _STATUS; }
            set { _STATUS = value; }
        }

        /// <summary>
        /// 
        /// </summary>
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 2)]
        private byte[] _FRAMENUM;

        public ushort FRAMENUM
        {
            get
            {
                long temp;
                temp = _FRAMENUM[0] << 8;
                temp += _FRAMENUM[1];
                return (ushort)temp;
            }
            set
            {
                _FRAMENUM = BitConverter.GetBytes(value);     // BitConverter 默认小端
                Array.Reverse(_FRAMENUM);                     // 切换成大端
            }
        }

        private byte _INFOCOUNT;

        public byte INFOCOUNT
        {
            get { return _INFOCOUNT; }
            set { _INFOCOUNT = value; }
        }

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 4096)]
        private byte[] _WHITELIST;

        public byte[] WHITELIST
        {
            get { return _WHITELIST; }
            set { _WHITELIST = value; }
        }
    }
}
