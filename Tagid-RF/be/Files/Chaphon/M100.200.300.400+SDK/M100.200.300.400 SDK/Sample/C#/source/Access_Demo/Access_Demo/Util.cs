using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

namespace Access_Demo
{
    public static class Util
    {
        /// <summary>
        /// 
        /// </summary>
        /// <param name="s1"></param>
        /// <param name="s2"></param>
        /// <returns>小于0--往前移 等于0--不变 大于0--后移</returns>
        public static int StringComparison(string s1, string s2)
        {
            if (s1.Length < s2.Length) return -1;
            return s1.CompareTo(s2);
        }

        /// <summary>
        /// 转换为String 如果转换失败 则返回默认值
        /// </summary>
        /// <param name="thisValue"></param>
        /// <param name="errorValue">默认值</param>
        /// <returns></returns>
        public static string Obj2String(this object value, string errorValue = "")
        {
            if (value != null) return value.ToString().Trim();
            return errorValue;
        }

        /// <summary>
        /// 是否为空
        /// </summary>
        /// <param name="ch"></param>
        /// <returns></returns>
        public static bool IsSpec(char ch)
        {
            return ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n';
        }

        /// <summary>
        /// 是否为十六进制
        /// </summary>
        /// <param name="ch"></param>
        /// <returns></returns>
        public static bool IsHex(char ch)
        {
            return ch >= '0' && ch <= '9' || ch >= 'A' && ch <= 'F' || ch >= 'a' && ch <= 'f';
        }

        /// <summary>
        /// 将Char转换为Hex
        /// </summary>
        /// <param name="ch"></param>
        /// <returns></returns>
        private static byte Char2Hex(char ch)
        {
            byte btHex = 0;
            if (ch >= '0' && ch <= '9')
            {
                btHex = (byte)(ch - '0');
            }
            else if (ch >= 'A' && ch <= 'Z')
            {
                btHex = (byte)(ch - 'A' + 10);
            }
            else if (ch >= 'a' && ch <= 'z')
            {
                btHex = (byte)(ch - 'a' + 10);
            }
            return btHex;
        }

        public static readonly byte[] EmptyArray = new byte[0];
        /// <summary>
        /// 将String类型转换为16进制的数组
        /// </summary>
        /// <param name="value"></param>
        /// <returns></returns>
        public static byte[] String2HexArray(this string value)
        {
            if (string.IsNullOrEmpty(value))
                return EmptyArray;

            List<byte> lstHex = new List<byte>(1024);
            String2HexArray(value, lstHex);
            return lstHex.ToArray();
        }

        private static void String2HexArray(string value, List<byte> lstHex)
        {
            // 当前状态
            // ，0 表示当前字节还没数据，等待接收第一个4位数据
            // ，1 表示已经接收第一个4位数据，等待接收第二个4位数据
            int iState = 0;
            byte btCur = 0, btTmp = 0;
            foreach (char ch in value)
            {
                switch (iState)
                {
                    case 0:
                        if (IsSpec(ch))
                        {
                            continue;
                        }
                        if (!IsHex(ch))
                        {
                            throw new FormatException("错误的十六进制字符串'" + value + "'");
                        }
                        btCur = Char2Hex(ch);
                        iState = 1;
                        break;
                    case 1:
                        if (IsSpec(ch))
                        {
                            lstHex.Add(btCur);
                            iState = 0;
                            continue;
                        }
                        if (!IsHex(ch))
                        {
                            throw new FormatException("错误的十六进制字符串'" + value + "'");
                        }
                        btTmp = Char2Hex(ch);
                        btCur = (byte)((btCur << 4) + btTmp);
                        lstHex.Add(btCur);
                        iState = 0;
                        break;
                    default:
                        throw new FormatException("错误的十六进制字符串'" + value + "'");
                }
            }
            if (iState == 1)
            {
                lstHex.Add(btCur);
            }
        }

        /// <summary>
        /// 将十六进制数组转换为String类型
        /// </summary>
        /// <param name="arrData"></param>
        /// <param name="isSpace">是否用空格隔开</param>
        /// <returns></returns>
        public static string HexArray2String(this byte[] arrData, bool isSpace = true)
        {
            return HexArray2String(arrData, 0, arrData.Length, isSpace);
        }

        private static string HexArray2String(byte[] arrData, int index, int len, bool isSpace = true)
        {
            if (len == 0)
                return string.Empty;
            if (len == 1)
                return arrData[0].ToString("X2");
            StringBuilder sb = new StringBuilder(len * 3);
            if (arrData.Length > 0)
            {
                len = index + len - 1;
                for (int i = index; i < len; ++i)
                {
                    sb.Append(arrData[i].ToString("X2"));
                    if (isSpace) sb.Append(' ');
                }
                sb.Append(arrData[len].ToString("X2"));
            }
            return sb.Obj2String();
        }

        private static byte _fillChar = 0;
        public static byte[] FillZero(this byte[] data, int len)
        {
            byte[] result = new byte[len];
            for (int i = 0; i < len - 2; i++)
                result[i] = ((i < data.Length) ? data[i] : _fillChar);

            return result;
        }

        /// <summary>  
        /// 由byte数组转换为结构体  
        /// </summary>  
        public static T ByteToStructure<T>(this byte[] dataBuffer)
        {
            object structure = null;
            int size = Marshal.SizeOf(typeof(T));
            IntPtr allocIntPtr = Marshal.AllocHGlobal(size);
            try
            {
                Marshal.Copy(dataBuffer, 0, allocIntPtr, size);
                structure = Marshal.PtrToStructure(allocIntPtr, typeof(T));
            }
            finally
            {
                Marshal.FreeHGlobal(allocIntPtr);
            }
            return (T)structure;
        }
    }
}
