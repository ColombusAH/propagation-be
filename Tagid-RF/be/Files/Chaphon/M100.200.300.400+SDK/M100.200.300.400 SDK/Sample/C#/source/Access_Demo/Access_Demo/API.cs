using System;
using System.Runtime.InteropServices;

namespace Access_Demo
{
    public unsafe class API
    {
        [DllImport("UHFPrimeReader.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
        public static extern int OpenNetConnection(out IntPtr handler, string ip, ushort port, uint timeoutMs);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int CloseDevice(IntPtr hComm);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int GetDevicePara(IntPtr hComm, out DeviceParam devInfo);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int SetDevicePara(IntPtr hComm, DeviceParam devInfo);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int GetGPIOWorkParam(IntPtr handler, out GateGPIOParam gpioInfo);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int SetGPIOWorkParam(IntPtr handler, GateGPIOParam gpioInfo);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int GetAccessOperateParam(IntPtr handler, out AccessOperateParam aParam);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int SetAccessOperateParam(IntPtr handler, AccessOperateParam aParam);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int BeginWhiteList(IntPtr handler, byte option, ushort customerCount);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int GetWhiteList(IntPtr handler, out WhiteListParam whiteList, ushort timeout);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int SetWhiteList(IntPtr handler, ushort length, [In] byte[] pParam);
        [DllImport("UHFPrimeReader.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int EndWhiteList(IntPtr handler, ref ushort customerCount);
    }
}
