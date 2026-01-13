using System.Runtime.InteropServices;

namespace Access_Demo
{
    [StructLayout(LayoutKind.Sequential)]
    public struct AccessOperateParam
    {
        private byte _LISTENABLE;
        /// <summary>
        /// 白名单使能
        /// </summary>
        public byte LISTENABLE
        {
            get { return _LISTENABLE; }
            set { _LISTENABLE = value; }
        }

        private byte _GPI1;
        /// <summary>
        /// GPI1触发操作
        /// </summary>
        public byte GPI1
        {
            get { return _GPI1; }
            set { _GPI1 = value; }
        }

        private byte _GPI2;
        /// <summary>
        /// GPI2触发操作
        /// </summary>
        public byte GPI2
        {
            get { return _GPI2; }
            set { _GPI2 = value; }
        }

        private byte _GPI3;
        /// <summary>
        /// GPI3触发操作
        /// </summary>
        public byte GPI3
        {
            get { return _GPI3; }
            set { _GPI3 = value; }
        }

        private byte _GPI4;
        /// <summary>
        /// GPI4触发操作
        /// </summary>
        public byte GPI4
        {
            get { return _GPI4; }
            set { _GPI4 = value; }
        }

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 4)]
        private byte[] _RECVGPIEXEFUNC;
        /// <summary>
        /// 保留的GPI操作
        /// </summary>
        public byte[] RECVGPIEXEFUNC
        {
            get { return _RECVGPIEXEFUNC; }
            set { _RECVGPIEXEFUNC = value; }
        }

        private byte _GPO1;
        /// <summary>
        /// GPO1执行部件参数
        /// </summary>
        public byte GPO1
        {
            get { return _GPO1; }
            set { _GPO1 = value; }
        }

        private byte _GPO2;
        /// <summary>
        /// GPO2执行部件参数
        /// </summary>
        public byte GPO2
        {
            get { return _GPO2; }
            set { _GPO2 = value; }
        }

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 6)]
        private byte[] _RECVACTIONEXEPART;
        /// <summary>
        /// 保留的GPO操作
        /// </summary>
        public byte[] RECVACTIONEXEPART
        {
            get { return _RECVACTIONEXEPART; }
            set { _RECVACTIONEXEPART = value; }
        }
    }
}
