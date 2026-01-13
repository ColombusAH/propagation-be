using System.Runtime.InteropServices;

namespace Access_Demo
{
    /// <summary>
    /// 设备参数
    /// </summary>
    [StructLayout(LayoutKind.Sequential)]
    public struct DeviceParam
    {
        private byte DEVICEARRD;
        private byte RFIDPRO;
        private byte WORKMODE;
        private byte INTERFACE;
        private byte BAUDRATE;
        private byte WGSET;
        private byte ANT;
        private byte REGION;
        private ushort STRATFREI;
        private ushort STRATFRED;
        private ushort STEPFRE;
        private byte CN;
        private byte RFIDPOWER;
        private byte INVENTORYAREA;
        private byte QVALUE;
        private byte SESSION;
        private byte ACSADDR;
        private byte ACSDATALEN;
        private byte FILTERTIME;
        private byte TRIGGLETIME;
        private byte BUZZERTIME;
        private byte INTERNELTIME;

        /// <summary>
        /// 设备地址（HEX）
        /// </summary>
        public byte Addr
        {
            get { return DEVICEARRD; }
            set { DEVICEARRD = value; }
        }

        /// <summary>
        /// 0
        /// </summary>
        public byte Protocol
        {
            get { return RFIDPRO; }
            set { RFIDPRO = value; }
        }

        /// <summary>
        /// 波特率
        /// </summary>
        public byte Baud
        {
            get { return BAUDRATE; }
            set { BAUDRATE = value; }
        }

        /// <summary>
        /// 工作模式 0：应答模式 1：自动模式 2：触发模式
        /// </summary>
        public byte Workmode
        {
            get { return WORKMODE; }
            set { WORKMODE = value; }
        }

        /// <summary>
        /// 通讯接口
        /// RS232       0x80
        /// RS485       0x40
        /// RJ45        0x20
        /// Wieggand    (wieggand >> 7) == 1
        /// WiFi        0x10
        /// USB         0x01
        /// KeyBoard    0x02
        /// CDC_COM     0x04
        /// </summary>
        public byte port
        {
            get { return INTERFACE; }
            set { INTERFACE = value; }
        }

        /// <summary>
        /// 韦根输出
        /// WG26
        /// WG34        (wieggand & 0x40) != 0
        /// </summary>
        public byte wieggand
        {
            get { return WGSET; }
            set { WGSET = value; }
        }

        /// <summary>
        /// 天线
        /// & 0x01 == 0x01      天线1
        /// & 0x02 == 0x02      天线2
        /// & 0x04 == 0x04      天线3
        /// & 0x08 == 0x08      天线4
        /// & 0x10 == 0x10      天线5
        /// & 0x20 == 0x20      天线6
        /// & 0x40 == 0x40      天线7
        /// & 0x80 == 0x80      天线8
        /// </summary>
        public byte Ant
        {
            get { return ANT; }
            set { ANT = value; }
        }

        /// <summary>
        /// 工作频段
        /// </summary>
        public byte Region
        {
            get { return REGION; }
            set { REGION = value; }
        }

        /// <summary>
        /// IF(Region==0)
        ///     结束频率 - 开始频率 / 500
        /// ELSE
        ///     结束频率 - 开始频率 + 1
        /// END
        /// </summary>
        public byte Channel
        {
            get { return CN; }
            set { CN = value; }
        }

        /// <summary>
        /// 输出功率
        /// </summary>
        public byte Power
        {
            get { return RFIDPOWER; }
            set { RFIDPOWER = value; }
        }

        /// <summary>
        /// 询查区域（号码）：
        /// Reserve
        /// EPC
        /// TID
        /// User
        /// EPC+TID
        /// EPC+User
        /// EPC+TID+User
        /// </summary>
        public byte Area
        {
            get { return INVENTORYAREA; }
            set { INVENTORYAREA = value; }
        }

        /// <summary>
        /// Q值 
        /// 0 -- 15
        /// </summary>
        public byte Q
        {
            get { return QVALUE; }
            set { QVALUE = value; }
        }

        /// <summary>
        /// Session
        /// S1 -- S3
        /// </summary>
        public byte Session
        {
            get { return SESSION; }
            set { SESSION = value; }
        }

        /// <summary>
        /// 起始地址（Byte）
        /// </summary>
        public byte Startaddr
        {
            get { return ACSADDR; }
            set { ACSADDR = value; }
        }

        /// <summary>
        /// 字节长度（Byte）
        /// </summary>
        public byte DataLen
        {
            get { return ACSDATALEN; }
            set { ACSDATALEN = value; }
        }

        /// <summary>
        /// 过滤时间(s)
        /// </summary>
        public byte Filtertime
        {
            get { return FILTERTIME; }
            set { FILTERTIME = value; }
        }

        /// <summary>
        /// 触发时间(s)
        /// </summary>
        public byte Triggletime
        {
            get { return TRIGGLETIME; }
            set { TRIGGLETIME = value; }
        }

        /// <summary>
        /// 蜂鸣器使能
        /// </summary>
        public byte Buzzertime
        {
            get { return BUZZERTIME; }
            set { BUZZERTIME = value; }
        }

        /// <summary>
        /// 询查间隔时间(s)
        /// </summary>
        public byte IntenelTime
        {
            get { return INTERNELTIME; }
            set { INTERNELTIME = value; }
        }

        /// <summary>
        /// StartFreq
        /// </summary>
        public ushort StartFreq
        {
            get
            {
                return (ushort)(STRATFREI >> 8 | STRATFREI << 8);
            }
            set
            {
                STRATFREI = (ushort)(value >> 8 | value << 8);          //大小端转换
            }
        }

        /// <summary>
        /// StartFreqde
        /// </summary>
        public ushort StartFreqde
        {
            get { return (ushort)(STRATFRED >> 8 | STRATFRED << 8); }
            set
            {
                STRATFRED = (ushort)(value >> 8 | value << 8);          //大小端转换
            }
        }

        /// <summary>
        /// Stepfreq
        /// </summary>
        public ushort Stepfreq
        {
            get { return (ushort)(STEPFRE >> 8 | STEPFRE << 8); }
            set
            {
                STEPFRE = (ushort)(value >> 8 | value << 8);          //大小端转换 
            }
        }
    };
}
