using System.Runtime.InteropServices;

namespace Access_Demo
{
    /// <summary>
    /// 门通道输出参数
    /// </summary>
    [StructLayout(LayoutKind.Sequential)]
    public struct GateGPIOParam
    {
        private byte _Mode;
        private byte _GPIEn;
        private byte _GPILevel;
        private byte _GPOEn;
        private byte _GPOLevel;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 8)]
        private byte[] _PutTime;

        public byte Mode
        {
            get { return _Mode; }
            set { _Mode = value; }
        }
        public byte GPIEn
        {
            get { return _GPIEn; }
            set { _GPIEn = value; }
        }
        public byte GPILevel
        {
            get { return _GPILevel; }
            set { _GPILevel = value; }
        }
        public byte GPOEn
        {
            get { return _GPOEn; }
            set { _GPOEn = value; }
        }
        public byte GPOLevel
        {
            get { return _GPOLevel; }
            set { _GPOLevel = value; }
        }
        public byte[] PutTime
        {
            get { return _PutTime; }
            set { _PutTime = value; }
        }
    }
}
