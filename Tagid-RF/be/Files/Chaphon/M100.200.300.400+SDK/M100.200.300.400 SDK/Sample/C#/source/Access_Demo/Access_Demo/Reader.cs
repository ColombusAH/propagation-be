using System;
using System.IO;
using System.Threading;

namespace Access_Demo
{
    public unsafe partial class Reader
    {
        IntPtr m_handler = IntPtr.Zero;
        volatile int m_iState = 0;

        public void Open(string ip, ushort port, uint timeoutMs, bool throwExcpOnTimeout)
        {
            if (ip == null)
                throw new ArgumentNullException("ip(ipaddr)");
            ip = ip.Trim();
            if (ip.Length == 0)
                throw new ArgumentException("IPaddr is null", "ip(ipaddr)");
            if (port == 0)
                throw new ArgumentException("port is null", "port(port)");
            if (m_iState != 0)
                throw new InvalidOperationException("Reader is already open");

            if (m_handler != IntPtr.Zero)
            {
                try { API.CloseDevice(m_handler); }
                catch { }
                m_handler = IntPtr.Zero;
            }

            int state = API.OpenNetConnection(out m_handler, ip, port, timeoutMs);
            if (state != ReaderException.ERROR_SUCCESS)
            {
                m_handler = IntPtr.Zero;
                if (state == ReaderException.ERROR_CMD_COMM_TIMEOUT && !throwExcpOnTimeout)
                    return;
                throw new IOException("IP  '" + ip + "' Port " + port + " Connet Fail");
            }
            m_iState = 2;
        }

        public void Close()
        {
            if (m_handler != IntPtr.Zero)
            {
                try { API.CloseDevice(m_handler); }
                catch { }
                m_handler = IntPtr.Zero;
            }
            m_iState = 0;
        }

        /// <summary>
        /// 
        /// </summary>
        /// <returns></returns>
        /// <exception cref="InvalidOperationException"></exception>
        /// <exception cref="ReaderException"></exception>
        public DeviceParam GetDevicePara()
        {
            Thread.Sleep(50);
            if (m_iState == 0)
                throw new InvalidOperationException("Reader is not open");
            DeviceParam info;
            int state = API.GetDevicePara(m_handler, out info);
            if (state == ReaderException.ERROR_SUCCESS)
                return info;
            throw new ReaderException(state);
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="info"></param>
        /// <exception cref="InvalidOperationException"></exception>
        /// <exception cref="ReaderException"></exception>
        public void SetDevicePara(DeviceParam info)
        {
            Thread.Sleep(50);
            if (m_iState == 0)
                throw new InvalidOperationException("Reader is not open");
            int state = API.SetDevicePara(m_handler, info);
            if (state == ReaderException.ERROR_SUCCESS)
                return;
            throw new ReaderException(state);
        }

        public GateGPIOParam GetGPIOWorkParam()
        {
            Thread.Sleep(50);
            if (m_iState == 0)
                throw new InvalidOperationException("Reader is not open");
            GateGPIOParam gpio;
            int state = API.GetGPIOWorkParam(m_handler, out gpio);
            if (state == ReaderException.ERROR_SUCCESS)
                return gpio;
            throw new ReaderException(state);
        }

        public void SetGPIOWorkParam(GateGPIOParam gpio)
        {
            Thread.Sleep(50);
            if (m_iState == 0)
                throw new InvalidOperationException("Reader is not open");
            int state = API.SetGPIOWorkParam(m_handler, gpio);
            if (state == ReaderException.ERROR_SUCCESS)
                return;
            throw new ReaderException(state);
        }

        /// <summary>
        /// 
        /// </summary>
        /// <returns></returns>
        /// <exception cref="InvalidOperationException"></exception>
        /// <exception cref="ReaderException"></exception>
        public AccessOperateParam GetAccessOperateParam()
        {
            Thread.Sleep(50);
            if (m_iState == 0)
                throw new InvalidOperationException("Reader is not open");
            AccessOperateParam info;
            int state = API.GetAccessOperateParam(m_handler, out info);
            if (state == ReaderException.ERROR_SUCCESS)
                return info;
            throw new ReaderException(state);
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="info"></param>
        /// <exception cref="InvalidOperationException"></exception>
        /// <exception cref="ReaderException"></exception>
        public void SetAccessOperateParam(AccessOperateParam info)
        {
            Thread.Sleep(50);
            if (m_iState == 0)
                throw new InvalidOperationException("Reader is not open");
            int state = API.SetAccessOperateParam(m_handler, info);
            if (state == ReaderException.ERROR_SUCCESS)
                return;
            throw new ReaderException(state);
        }

        /// <summary>
        /// 开始更新白名单
        /// </summary>
        /// <param name="infoCount">更新的白名单数量</param>
        /// <exception cref="InvalidOperationException"></exception>
        /// <exception cref="ReaderException"></exception>
        public void BeginWhiteList(byte option, ushort infoCount)
        {
            Thread.Sleep(50);
            if (m_iState == 0)
                throw new InvalidOperationException("Reader is not open");
            int state = API.BeginWhiteList(m_handler, option, infoCount);
            if (state == ReaderException.ERROR_SUCCESS)
                return;
            throw new ReaderException(state);
        }

        public WhiteListParam GetWhiteList(ushort timeout)
        {
            Thread.Sleep(50);
            if (m_iState == 0)
                throw new InvalidOperationException("Reader is not open");
            WhiteListParam whiteList;
            int state = API.GetWhiteList(m_handler, out whiteList, timeout);
            if (state == ReaderException.ERROR_SUCCESS)
                return whiteList;
            throw new ReaderException(state);
        }

        public void SetWhiteList(int length, byte[] pParam)
        {
            Thread.Sleep(5);
            if (m_iState == 0)
                throw new InvalidOperationException("Reader is not open");
            int state = API.SetWhiteList(m_handler, (ushort)length, pParam);
            if (state == ReaderException.ERROR_SUCCESS)
                return;
            throw new ReaderException(state);
        }

        /// <summary>
        /// 结束更新白名单
        /// </summary>
        /// <param name="infoCount">更新的白名单数量</param>
        /// <exception cref="InvalidOperationException"></exception>
        /// <exception cref="ReaderException"></exception>
        public void EndWhiteList(ref ushort infoCount)
        {
            Thread.Sleep(50);
            if (m_iState == 0)
                throw new InvalidOperationException("Reader is not open");
            int state = API.EndWhiteList(m_handler, ref infoCount);
            if (state == ReaderException.ERROR_SUCCESS)
                return;
            throw new ReaderException(state);
        }

        static readonly ushort PRESET_VALUE = 0xFFFF;
        static readonly ushort POLYNOMIAL = 0x8408;

        public unsafe ushort Crc16Cal(byte[] pucY, ushort ucX, ushort CrcValue)
        {
            ushort ucI, ucJ;
            ushort uiCrcValue;
            if (CrcValue == 0xFFFF)    // first value
            {
                uiCrcValue = PRESET_VALUE;
            }
            else
            {
                uiCrcValue = CrcValue;
            }
            for (ucI = 1; ucI < ucX; ucI++)
            {
                uiCrcValue = (ushort)(uiCrcValue ^ pucY[ucI]);
                for (ucJ = 0; ucJ < 8; ucJ++)
                {
                    if ((uiCrcValue & 0x0001) != 0)
                    {
                        uiCrcValue = (ushort)((uiCrcValue >> 1) ^ POLYNOMIAL);
                    }
                    else
                    {
                        uiCrcValue = (ushort)(uiCrcValue >> 1);
                    }
                }
            }
            return uiCrcValue;
        }
    }
}
