using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using Timer = System.Windows.Forms.Timer;

namespace Access_Demo
{
    public partial class Form1 : Form
    {
        SocketServer _server = null;
        Reader _reader = null;
        List<string> _lstCard = new List<string>();
        int _workmode;

        public Form1()
        {
            InitializeComponent();

            Control.CheckForIllegalCrossThreadCalls = false;//取消线程间的安全检查
        }

        private void btn_Listen_Click(object sender, EventArgs e)
        {
            if (btn_Listen.Text == "STOP")
            {
                try
                {
                    if (_server != null)
                        _server.StopListen();
                    btn_Listen.Text = "LISTEN";
                    _server = null;
                    lbl_Message.Text = "";
                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + "Stop Successful!\r\n");
                }
                catch (Exception ex)
                {
                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + ex.Message + "\r\n");
                }
            }
            else
            {
                try
                {
                    if (string.IsNullOrEmpty(txt_listenPort.Text))
                    {
                        txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + "Please enter listening port!\r\n");
                        return;
                    }
                    int port = Convert.ToInt32(txt_listenPort.Text);
                    _server = new SocketServer(this, port);
                    _server.StartListen();
                    btn_Listen.Text = "STOP";
                    lbl_Message.Text = "If you cannot listen to data, please ensure the Communication Interface is [RJ45]";
                }
                catch (Exception ex)
                {
                    _server = null;
                    lbl_Message.Text = "";
                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + ex.Message + "\r\n");
                }
            }
        }

        private void btn_Open_Click(object sender, EventArgs e)
        {
            if (btn_Open.Text == "CLOSE")
            {
                try
                {
                    if (_reader != null)
                        _reader.Close();
                    btn_Get.Enabled = btn_Set.Enabled = btn_SynchronizeWhitelist.Enabled = false;
                    btn_Open.Text = "Open";
                    _reader = null;
                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + "Close Successful!\r\n");
                }
                catch (Exception ex)
                {
                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + ex.Message + "\r\n");
                }
            }
            else
            {
                try
                {
                    if (string.IsNullOrEmpty(txt_IP.Text))
                    {
                        txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + "Please enter ip!\r\n");
                        return;
                    }
                    if (string.IsNullOrEmpty(txt_Port.Text))
                    {
                        txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + "Please enter port!\r\n");
                        return;
                    }
                    _reader = new Reader();
                    _reader.Open(txt_IP.Text, (ushort)Convert.ToInt32(txt_Port.Text), 300, true);
                    InitParam();

                    btn_Get.Enabled = btn_Set.Enabled = btn_SynchronizeWhitelist.Enabled = true;
                    btn_Open.Text = "CLOSE";
                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : Open Successful.\r\n");
                }
                catch (Exception ex)
                {
                    _reader = null;
                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + ex.Message + "\r\n");
                }
            }
        }

        DeviceParam _device;
        GateGPIOParam _gpio;
        AccessOperateParam _access;
        private void InitParam()
        {
            try
            {
                Thread.Sleep(50);
                _device = _reader.GetDevicePara();
                if (_device.port == 0x20) cmb_CommunicationInterface.SelectedIndex = 0;
                else cmb_CommunicationInterface.SelectedIndex = 1;
                _workmode = _device.Workmode;

                _gpio = _reader.GetGPIOWorkParam();
                if ((_gpio.GPILevel & 0x01) == 0x01) cmb_GPI1ActiveLevel.SelectedIndex = 0;
                else cmb_GPI1ActiveLevel.SelectedIndex = 1;
                if ((_gpio.GPILevel & 0x02) == 0x02) cmb_GPI2ActiveLevel.SelectedIndex = 0;
                else cmb_GPI2ActiveLevel.SelectedIndex = 1;
                if ((_gpio.GPOLevel & 0x01) == 0x01) cmb_GPO1ActiveLevel.SelectedIndex = 0;
                else cmb_GPO1ActiveLevel.SelectedIndex = 1;
                txt_GPO1PutTime.Text = _gpio.PutTime[0].ToString();

                _access = _reader.GetAccessOperateParam();
                switch (_access.GPO1)
                {
                    case 0x00:
                        cmb_AuthorizationExecution.SelectedIndex = 0;
                        break;
                    case 0x01:
                        cmb_AuthorizationExecution.SelectedIndex = 1;
                        break;
                    case 0x80:
                        cmb_AuthorizationExecution.SelectedIndex = 2;
                        break;
                    case 0x81:
                        cmb_AuthorizationExecution.SelectedIndex = 3;
                        break;
                }
                switch (_access.GPO2)
                {
                    case 0x00:
                        cmb_UnauthorizationExecution.SelectedIndex = 0;
                        break;
                    case 0x01:
                        cmb_UnauthorizationExecution.SelectedIndex = 1;
                        break;
                    case 0x80:
                        cmb_UnauthorizationExecution.SelectedIndex = 2;
                        break;
                    case 0x81:
                        cmb_UnauthorizationExecution.SelectedIndex = 3;
                        break;
                }
                if (_access.GPI1 >> 4 == 1) cmb_GPI1TriggerOperat.SelectedIndex = 4;
                else cmb_GPI1TriggerOperat.SelectedIndex = _access.GPI1 & 0x0F;
                if (_access.GPI2 >> 4 == 1) cmb_GPI2TriggerOperat.SelectedIndex = 4;
                else cmb_GPI2TriggerOperat.SelectedIndex = _access.GPI2 & 0x0F;
            }
            catch (Exception ex)
            {
                txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + ex.Message + "\r\n");
            }
        }

        private void btn_Get_Click(object sender, EventArgs e)
        {
            if (_reader != null) InitParam();
            txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"Getting Successful!\r\n");
        }

        private void btn_Set_Click(object sender, EventArgs e)
        {
            try
            {
                Thread.Sleep(50);
                if (cmb_CommunicationInterface.SelectedIndex == 0) _device.port = 0x20;
                else _device.port = 0x80;
                _reader.SetDevicePara(_device);

                if (cmb_GPI1ActiveLevel.SelectedIndex == 0) _gpio.GPILevel |= 0x01;
                else _gpio.GPILevel &= 0xFE;
                if (cmb_GPI2ActiveLevel.SelectedIndex == 0) _gpio.GPILevel |= 0x02;
                else _gpio.GPILevel &= 0xFD;
                if (cmb_GPO1ActiveLevel.SelectedIndex == 0) _gpio.GPOLevel |= 0x01;
                else _gpio.GPOLevel &= 0xFE;
                _gpio.PutTime[0] = (byte)Convert.ToInt32(txt_GPO1PutTime.Text);
                _reader.SetGPIOWorkParam(_gpio);

                _access.LISTENABLE = 0x01;
                if (cmb_GPI1TriggerOperat.SelectedIndex == 4) _access.GPI1 = 0x01 << 4;
                else _access.GPI1 = (byte)cmb_GPI1TriggerOperat.SelectedIndex;
                if (cmb_GPI2TriggerOperat.SelectedIndex == 4) _access.GPI2 = 0x01 << 4;
                else _access.GPI2 = (byte)cmb_GPI2TriggerOperat.SelectedIndex;
                switch (cmb_AuthorizationExecution.SelectedIndex)
                {
                    case 0:
                        _access.GPO1 = 0x00;
                        break;
                    case 1:
                        _access.GPO1 = 0x01;
                        break;
                    case 2:
                        _access.GPO1 = 0x80;
                        break;
                    case 3:
                        _access.GPO1 = 0x81;
                        break;
                }
                switch (cmb_UnauthorizationExecution.SelectedIndex)
                {
                    case 0:
                        _access.GPO2 = 0x00;
                        break;
                    case 1:
                        _access.GPO2 = 0x01;
                        break;
                    case 2:
                        _access.GPO2 = 0x80;
                        break;
                    case 3:
                        _access.GPO2 = 0x81;
                        break;
                }
                _reader.SetAccessOperateParam(_access);

                txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"Setting Successful!\r\n");
            }
            catch (Exception ex)
            {
                txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + ex.Message + "\r\n");
            }
        }

        private void btn_CleanCard_Click(object sender, EventArgs e)
        {
            _lstCard.Clear();
            txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"Clean Successful!\r\n");
        }

        private void btn_CleanLog_Click(object sender, EventArgs e)
        {
            txt_Log.Text = string.Empty;
        }

        private void btn_AddCard_Click(object sender, EventArgs e)
        {
            if (!_lstCard.Contains(txt_RealCard.Text))
            {
                _lstCard.Add(txt_RealCard.Text);
                txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"Add Successful!\r\n");
            }
        }

        private void btn_Generate_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(txt_VirtualCard.Text))
            {
                txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + "Please enter virtual card Number!\r\n");
                return;
            }
            int num = Convert.ToInt32(txt_VirtualCard.Text);
            for (int i = 0; i < num; i++)
            {
                _lstCard.Add(RandomChars.NumChar(24, RandomChars.UppLowType.upper));
            }
            txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"Generate Successful!\r\n");
        }

        private void txt_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!((e.KeyChar >= 48 && e.KeyChar <= 57) || e.KeyChar == 8)) e.Handled = true;
        }

        int _second = 0;
        private void btn_SynchronizeWhitelist_Click(object sender, EventArgs e)
        {
            _second = 0;
            Timer timer = new Timer();
            timer.Interval = 1000;
            timer.Tick += Timer_Tick;
            timer.Start();
            Task.Run(() =>
            {
                try
                {
                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"Begin Package Whitelist!\r\n");
                    List<string> whiteList = new List<string>();
                    List<string> newWhiteList = new List<string>();
                    _lstCard.ForEach(c => whiteList.Add(c.String2HexArray().Length.ToString("x2") + c));
                    whiteList.Sort(Util.StringComparison);

                    // 单次发包最多64条
                    int sumCount = whiteList.Count;
                    int count = sumCount / 64;
                    int remainder = sumCount % 64;
                    if (remainder != 0) count++;
                    for (int i = 1; i <= count; i++)
                    {
                        StringBuilder sb = new StringBuilder();
                        sb.Append(i.ToString("x4"));
                        if (i == count)
                        {
                            sb.Append(remainder.ToString("x2"));
                            for (int j = 0; j < remainder; j++)
                            {
                                sb.Append(whiteList[(i - 1) * 64 + j].String2HexArray().FillZero(32).HexArray2String(false));
                            }
                        }
                        else
                        {
                            sb.Append("40"); // 64
                            for (int j = 0; j < 64; j++)
                            {
                                sb.Append(whiteList[(i - 1) * 64 + j].String2HexArray().FillZero(32).HexArray2String(false));
                            }
                        }
                        newWhiteList.Add(sb.ToString());
                    }
                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"Begin Synchronize!\r\n");

                    // 同步前先将工作模式改为应答
                    _device.Workmode = 0;
                    _reader.SetDevicePara(_device);

                    _reader.BeginWhiteList(1, (ushort)count);
                    foreach (string s in newWhiteList)
                    {
                        byte[] bytes = s.String2HexArray();
                        _reader.SetWhiteList(bytes.Length, bytes);
                    }
                    ushort SynchronizationCount = 0;
                    _reader.EndWhiteList(ref SynchronizationCount);

                    _device.Workmode = (byte)_workmode;
                    _reader.SetDevicePara(_device);

                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + $"Synchronize Successful!\r\n");
                }
                catch (Exception ex)
                {

                    ushort SynchronizationCount = 0;
                    _reader.EndWhiteList(ref SynchronizationCount);

                    _device.Workmode = 1;
                    _reader.SetDevicePara(_device);

                    txt_Log.AppendText(DateTime.Now.ToString("yyyy-MM-dd HH:mm:dd") + " : " + ex.Message + "\r\n");
                }
                finally
                {
                    _second = 0;
                    timer.Stop();
                }
            });

        }

        private void Timer_Tick(object sender, EventArgs e)
        {
            txt_Log.AppendText($"Please Wait...({_second})\r\n");
            _second++;
        }
    }
}
