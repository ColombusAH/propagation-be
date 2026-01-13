using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Access_Demo
{
    public class SocketServer
    {
        private string _ip = string.Empty;
        private int _port = 0;
        private Socket _socket = null;
        private byte[] buffer = new byte[1024 * 1024 * 2];
        Form1 _owner = null;

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="ip">监听的IP</param>
        /// <param name="port">监听的端口</param>
        public SocketServer(Form1 owner, string ip, int port)
        {
            this._owner = owner;
            this._ip = ip;
            this._port = port;
        }

        public SocketServer(Form1 owner, int port)
        {
            this._owner = owner;
            this._ip = "0.0.0.0";
            this._port = port;
        }

        public void StartListen()
        {
            try
            {
                //1.0 实例化套接字(IP4寻找协议,流式协议,TCP协议)
                _socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                //2.0 创建IP对象
                IPAddress address = IPAddress.Parse(_ip);
                //3.0 创建网络端口,包括ip和端口
                IPEndPoint endPoint = new IPEndPoint(address, _port);
                //4.0 绑定套接字
                _socket.Bind(endPoint);
                //5.0 设置最大连接数
                _socket.Listen(int.MaxValue);
                _owner.txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"Successful Listen to [{_socket.LocalEndPoint.ToString()}]\r\n");
                //6.0 开始监听
                Thread thread = new Thread(ListenClientConnect);
                thread.IsBackground = true;
                thread.Start();
            }
            catch (Exception ex)
            {
                _owner.txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + ex.Message + "\r\n");
            }
        }

        /// <summary>
        /// 监听客户端连接
        /// </summary>
        private void ListenClientConnect()
        {
            try
            {
                while (true)
                {
                    //Socket创建的新连接
                    Socket clientSocket = _socket.Accept();
                    // clientSocket.Send(Encoding.UTF8.GetBytes("服务端发送消息:"));
                    Thread thread = new Thread(ReceiveMessage);
                    thread.IsBackground = true;
                    thread.Start(clientSocket);
                    _owner.txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"[{clientSocket.RemoteEndPoint}]was launched!\r\n");
                }
            }
            catch { }
        }

        /// <summary>
        /// 接收客户端消息
        /// </summary>
        /// <param name="socket">来自客户端的socket</param>
        private void ReceiveMessage(object socket)
        {
            Socket clientSocket = (Socket)socket;
            while (true)
            {
                try
                {
                    //获取从客户端发来的数据
                    int length = clientSocket.Receive(buffer);
                    AccessInfo access = Util.ByteToStructure<AccessInfo>(buffer);
                    int card_len = access.CustomerInfo[0];
                    byte[] bytes = access.CustomerInfo.Skip(1).Take(card_len).ToArray();
                    string card = bytes.HexArray2String(false);
                    string type = "";
                    switch (access.State)
                    {
                        case 0x10:
                            type = "Authorized Entry";
                            break;
                        case 0x11:
                            type = "Unauthorized Entry";
                            break;
                        case 0x20:
                            type = "Authorized Exit";
                            break;
                        case 0x21:
                            type = "Unauthorized Exit";
                            break;
                        case 0x22:
                            type = "Button Exit";
                            break;
                        default:
                            type = "Unknown Type";
                            break;
                    }
                    _owner.txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"Monitoring Data[{card}]_Type[{type}]\r\n");
                }
                catch (Exception ex)
                {
                    _owner.txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + ex.Message + "\r\n");
                    clientSocket.Shutdown(SocketShutdown.Both);
                    clientSocket.Close();
                    break;
                }
            }
        }

        public void StopListen()
        {
            try
            {
                _socket.Close();
            }
            catch (Exception ex)
            {
                _owner.txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + ex.Message + "\r\n");
            }
        }
    }
}
