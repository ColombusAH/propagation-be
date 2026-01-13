namespace Access_Demo
{
    partial class Form1
    {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            this.panel1 = new System.Windows.Forms.Panel();
            this.btn_Listen = new System.Windows.Forms.Button();
            this.txt_listenPort = new System.Windows.Forms.TextBox();
            this.label17 = new System.Windows.Forms.Label();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.txt_IP = new System.Windows.Forms.TextBox();
            this.label15 = new System.Windows.Forms.Label();
            this.btn_Open = new System.Windows.Forms.Button();
            this.txt_Port = new System.Windows.Forms.TextBox();
            this.label13 = new System.Windows.Forms.Label();
            this.cmb_CommunicationInterface = new System.Windows.Forms.ComboBox();
            this.btn_Set = new System.Windows.Forms.Button();
            this.btn_Get = new System.Windows.Forms.Button();
            this.label12 = new System.Windows.Forms.Label();
            this.txt_GPO1PutTime = new System.Windows.Forms.TextBox();
            this.cmb_GPO1ActiveLevel = new System.Windows.Forms.ComboBox();
            this.label11 = new System.Windows.Forms.Label();
            this.cmb_GPI2TriggerOperat = new System.Windows.Forms.ComboBox();
            this.cmb_GPI2ActiveLevel = new System.Windows.Forms.ComboBox();
            this.label6 = new System.Windows.Forms.Label();
            this.label7 = new System.Windows.Forms.Label();
            this.cmb_GPI1TriggerOperat = new System.Windows.Forms.ComboBox();
            this.cmb_GPI1ActiveLevel = new System.Windows.Forms.ComboBox();
            this.cmb_UnauthorizationExecution = new System.Windows.Forms.ComboBox();
            this.cmb_AuthorizationExecution = new System.Windows.Forms.ComboBox();
            this.label5 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.label9 = new System.Windows.Forms.Label();
            this.label8 = new System.Windows.Forms.Label();
            this.label10 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label14 = new System.Windows.Forms.Label();
            this.label16 = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.txt_VirtualCard = new System.Windows.Forms.TextBox();
            this.btn_Generate = new System.Windows.Forms.Button();
            this.btn_AddCard = new System.Windows.Forms.Button();
            this.txt_RealCard = new System.Windows.Forms.TextBox();
            this.label18 = new System.Windows.Forms.Label();
            this.label19 = new System.Windows.Forms.Label();
            this.txt_Log = new System.Windows.Forms.TextBox();
            this.groupBox3 = new System.Windows.Forms.GroupBox();
            this.btn_SynchronizeWhitelist = new System.Windows.Forms.Button();
            this.btn_CleanCard = new System.Windows.Forms.Button();
            this.btn_CleanLog = new System.Windows.Forms.Button();
            this.lbl_Message = new System.Windows.Forms.Label();
            this.panel1.SuspendLayout();
            this.groupBox1.SuspendLayout();
            this.groupBox2.SuspendLayout();
            this.groupBox3.SuspendLayout();
            this.SuspendLayout();
            // 
            // panel1
            // 
            this.panel1.Controls.Add(this.btn_Listen);
            this.panel1.Controls.Add(this.txt_listenPort);
            this.panel1.Controls.Add(this.label17);
            this.panel1.Controls.Add(this.groupBox1);
            this.panel1.Dock = System.Windows.Forms.DockStyle.Left;
            this.panel1.Location = new System.Drawing.Point(0, 0);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(200, 420);
            this.panel1.TabIndex = 0;
            // 
            // btn_Listen
            // 
            this.btn_Listen.Location = new System.Drawing.Point(113, 9);
            this.btn_Listen.Name = "btn_Listen";
            this.btn_Listen.Size = new System.Drawing.Size(78, 23);
            this.btn_Listen.TabIndex = 33;
            this.btn_Listen.Text = "LISTEN";
            this.btn_Listen.UseVisualStyleBackColor = true;
            this.btn_Listen.Click += new System.EventHandler(this.btn_Listen_Click);
            // 
            // txt_listenPort
            // 
            this.txt_listenPort.Location = new System.Drawing.Point(53, 11);
            this.txt_listenPort.Name = "txt_listenPort";
            this.txt_listenPort.Size = new System.Drawing.Size(54, 21);
            this.txt_listenPort.TabIndex = 32;
            this.txt_listenPort.Text = "7788";
            this.txt_listenPort.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.txt_KeyPress);
            // 
            // label17
            // 
            this.label17.AutoSize = true;
            this.label17.Location = new System.Drawing.Point(12, 16);
            this.label17.Name = "label17";
            this.label17.Size = new System.Drawing.Size(35, 12);
            this.label17.TabIndex = 31;
            this.label17.Text = "Port:";
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.txt_IP);
            this.groupBox1.Controls.Add(this.label15);
            this.groupBox1.Controls.Add(this.btn_Open);
            this.groupBox1.Controls.Add(this.txt_Port);
            this.groupBox1.Controls.Add(this.label13);
            this.groupBox1.Controls.Add(this.cmb_CommunicationInterface);
            this.groupBox1.Controls.Add(this.btn_Set);
            this.groupBox1.Controls.Add(this.btn_Get);
            this.groupBox1.Controls.Add(this.label12);
            this.groupBox1.Controls.Add(this.txt_GPO1PutTime);
            this.groupBox1.Controls.Add(this.cmb_GPO1ActiveLevel);
            this.groupBox1.Controls.Add(this.label11);
            this.groupBox1.Controls.Add(this.cmb_GPI2TriggerOperat);
            this.groupBox1.Controls.Add(this.cmb_GPI2ActiveLevel);
            this.groupBox1.Controls.Add(this.label6);
            this.groupBox1.Controls.Add(this.label7);
            this.groupBox1.Controls.Add(this.cmb_GPI1TriggerOperat);
            this.groupBox1.Controls.Add(this.cmb_GPI1ActiveLevel);
            this.groupBox1.Controls.Add(this.cmb_UnauthorizationExecution);
            this.groupBox1.Controls.Add(this.cmb_AuthorizationExecution);
            this.groupBox1.Controls.Add(this.label5);
            this.groupBox1.Controls.Add(this.label4);
            this.groupBox1.Controls.Add(this.label3);
            this.groupBox1.Controls.Add(this.label9);
            this.groupBox1.Controls.Add(this.label8);
            this.groupBox1.Controls.Add(this.label10);
            this.groupBox1.Controls.Add(this.label2);
            this.groupBox1.Controls.Add(this.label14);
            this.groupBox1.Controls.Add(this.label16);
            this.groupBox1.Controls.Add(this.label1);
            this.groupBox1.Location = new System.Drawing.Point(3, 32);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(194, 385);
            this.groupBox1.TabIndex = 3;
            this.groupBox1.TabStop = false;
            // 
            // txt_IP
            // 
            this.txt_IP.Location = new System.Drawing.Point(40, 11);
            this.txt_IP.Name = "txt_IP";
            this.txt_IP.Size = new System.Drawing.Size(148, 21);
            this.txt_IP.TabIndex = 33;
            this.txt_IP.Text = "192.168.1.216";
            // 
            // label15
            // 
            this.label15.AutoSize = true;
            this.label15.Location = new System.Drawing.Point(11, 14);
            this.label15.Name = "label15";
            this.label15.Size = new System.Drawing.Size(23, 12);
            this.label15.TabIndex = 31;
            this.label15.Text = "IP:";
            // 
            // btn_Open
            // 
            this.btn_Open.Location = new System.Drawing.Point(138, 35);
            this.btn_Open.Name = "btn_Open";
            this.btn_Open.Size = new System.Drawing.Size(50, 23);
            this.btn_Open.TabIndex = 30;
            this.btn_Open.Text = "OPEN";
            this.btn_Open.UseVisualStyleBackColor = true;
            this.btn_Open.Click += new System.EventHandler(this.btn_Open_Click);
            // 
            // txt_Port
            // 
            this.txt_Port.Location = new System.Drawing.Point(40, 36);
            this.txt_Port.Name = "txt_Port";
            this.txt_Port.Size = new System.Drawing.Size(92, 21);
            this.txt_Port.TabIndex = 29;
            this.txt_Port.Text = "2022";
            this.txt_Port.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.txt_KeyPress);
            // 
            // label13
            // 
            this.label13.AutoSize = true;
            this.label13.Location = new System.Drawing.Point(9, 65);
            this.label13.Name = "label13";
            this.label13.Size = new System.Drawing.Size(143, 12);
            this.label13.TabIndex = 26;
            this.label13.Text = "Communication Interface";
            // 
            // cmb_CommunicationInterface
            // 
            this.cmb_CommunicationInterface.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmb_CommunicationInterface.FormattingEnabled = true;
            this.cmb_CommunicationInterface.Items.AddRange(new object[] {
            "RJ45",
            "RS232"});
            this.cmb_CommunicationInterface.Location = new System.Drawing.Point(9, 82);
            this.cmb_CommunicationInterface.Name = "cmb_CommunicationInterface";
            this.cmb_CommunicationInterface.Size = new System.Drawing.Size(174, 20);
            this.cmb_CommunicationInterface.TabIndex = 25;
            // 
            // btn_Set
            // 
            this.btn_Set.Enabled = false;
            this.btn_Set.Location = new System.Drawing.Point(86, 357);
            this.btn_Set.Name = "btn_Set";
            this.btn_Set.Size = new System.Drawing.Size(102, 23);
            this.btn_Set.TabIndex = 24;
            this.btn_Set.Text = "SET";
            this.btn_Set.UseVisualStyleBackColor = true;
            this.btn_Set.Click += new System.EventHandler(this.btn_Set_Click);
            // 
            // btn_Get
            // 
            this.btn_Get.Enabled = false;
            this.btn_Get.Location = new System.Drawing.Point(4, 357);
            this.btn_Get.Name = "btn_Get";
            this.btn_Get.Size = new System.Drawing.Size(82, 23);
            this.btn_Get.TabIndex = 23;
            this.btn_Get.Text = "GET";
            this.btn_Get.UseVisualStyleBackColor = true;
            this.btn_Get.Click += new System.EventHandler(this.btn_Get_Click);
            // 
            // label12
            // 
            this.label12.AutoSize = true;
            this.label12.Location = new System.Drawing.Point(9, 333);
            this.label12.Name = "label12";
            this.label12.Size = new System.Drawing.Size(71, 12);
            this.label12.TabIndex = 22;
            this.label12.Text = "Put Time(s)";
            // 
            // txt_GPO1PutTime
            // 
            this.txt_GPO1PutTime.Location = new System.Drawing.Point(86, 330);
            this.txt_GPO1PutTime.Name = "txt_GPO1PutTime";
            this.txt_GPO1PutTime.Size = new System.Drawing.Size(102, 21);
            this.txt_GPO1PutTime.TabIndex = 21;
            this.txt_GPO1PutTime.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.txt_KeyPress);
            // 
            // cmb_GPO1ActiveLevel
            // 
            this.cmb_GPO1ActiveLevel.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmb_GPO1ActiveLevel.FormattingEnabled = true;
            this.cmb_GPO1ActiveLevel.Items.AddRange(new object[] {
            "High",
            "Low"});
            this.cmb_GPO1ActiveLevel.Location = new System.Drawing.Point(118, 304);
            this.cmb_GPO1ActiveLevel.Name = "cmb_GPO1ActiveLevel";
            this.cmb_GPO1ActiveLevel.Size = new System.Drawing.Size(70, 20);
            this.cmb_GPO1ActiveLevel.TabIndex = 20;
            // 
            // label11
            // 
            this.label11.AutoSize = true;
            this.label11.Location = new System.Drawing.Point(9, 307);
            this.label11.Name = "label11";
            this.label11.Size = new System.Drawing.Size(113, 12);
            this.label11.TabIndex = 19;
            this.label11.Text = "GPO1 Active Level:";
            // 
            // cmb_GPI2TriggerOperat
            // 
            this.cmb_GPI2TriggerOperat.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmb_GPI2TriggerOperat.FormattingEnabled = true;
            this.cmb_GPI2TriggerOperat.Items.AddRange(new object[] {
            "None",
            "Reading",
            "Relay Open",
            "Relay Close",
            "GPO1"});
            this.cmb_GPI2TriggerOperat.Location = new System.Drawing.Point(100, 276);
            this.cmb_GPI2TriggerOperat.Name = "cmb_GPI2TriggerOperat";
            this.cmb_GPI2TriggerOperat.Size = new System.Drawing.Size(88, 20);
            this.cmb_GPI2TriggerOperat.TabIndex = 14;
            // 
            // cmb_GPI2ActiveLevel
            // 
            this.cmb_GPI2ActiveLevel.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmb_GPI2ActiveLevel.FormattingEnabled = true;
            this.cmb_GPI2ActiveLevel.Items.AddRange(new object[] {
            "High",
            "Low"});
            this.cmb_GPI2ActiveLevel.Location = new System.Drawing.Point(118, 246);
            this.cmb_GPI2ActiveLevel.Name = "cmb_GPI2ActiveLevel";
            this.cmb_GPI2ActiveLevel.Size = new System.Drawing.Size(70, 20);
            this.cmb_GPI2ActiveLevel.TabIndex = 13;
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(9, 249);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(113, 12);
            this.label6.TabIndex = 12;
            this.label6.Text = "GPI2 Active Level:";
            // 
            // label7
            // 
            this.label7.AutoSize = true;
            this.label7.Location = new System.Drawing.Point(9, 279);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(95, 12);
            this.label7.TabIndex = 11;
            this.label7.Text = "Trigger Operat:";
            // 
            // cmb_GPI1TriggerOperat
            // 
            this.cmb_GPI1TriggerOperat.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmb_GPI1TriggerOperat.FormattingEnabled = true;
            this.cmb_GPI1TriggerOperat.Items.AddRange(new object[] {
            "None",
            "Reading",
            "Relay Open",
            "Relay Close",
            "GPO1"});
            this.cmb_GPI1TriggerOperat.Location = new System.Drawing.Point(100, 217);
            this.cmb_GPI1TriggerOperat.Name = "cmb_GPI1TriggerOperat";
            this.cmb_GPI1TriggerOperat.Size = new System.Drawing.Size(88, 20);
            this.cmb_GPI1TriggerOperat.TabIndex = 10;
            // 
            // cmb_GPI1ActiveLevel
            // 
            this.cmb_GPI1ActiveLevel.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmb_GPI1ActiveLevel.FormattingEnabled = true;
            this.cmb_GPI1ActiveLevel.Items.AddRange(new object[] {
            "High",
            "Low"});
            this.cmb_GPI1ActiveLevel.Location = new System.Drawing.Point(118, 187);
            this.cmb_GPI1ActiveLevel.Name = "cmb_GPI1ActiveLevel";
            this.cmb_GPI1ActiveLevel.Size = new System.Drawing.Size(70, 20);
            this.cmb_GPI1ActiveLevel.TabIndex = 9;
            // 
            // cmb_UnauthorizationExecution
            // 
            this.cmb_UnauthorizationExecution.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmb_UnauthorizationExecution.FormattingEnabled = true;
            this.cmb_UnauthorizationExecution.Items.AddRange(new object[] {
            "None",
            "GPO1",
            "Relay",
            "GPO1+Relay"});
            this.cmb_UnauthorizationExecution.Location = new System.Drawing.Point(9, 161);
            this.cmb_UnauthorizationExecution.Name = "cmb_UnauthorizationExecution";
            this.cmb_UnauthorizationExecution.Size = new System.Drawing.Size(179, 20);
            this.cmb_UnauthorizationExecution.TabIndex = 8;
            // 
            // cmb_AuthorizationExecution
            // 
            this.cmb_AuthorizationExecution.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmb_AuthorizationExecution.FormattingEnabled = true;
            this.cmb_AuthorizationExecution.Items.AddRange(new object[] {
            "None",
            "GPO1",
            "Relay",
            "GPO1+Relay"});
            this.cmb_AuthorizationExecution.Location = new System.Drawing.Point(9, 123);
            this.cmb_AuthorizationExecution.Name = "cmb_AuthorizationExecution";
            this.cmb_AuthorizationExecution.Size = new System.Drawing.Size(179, 20);
            this.cmb_AuthorizationExecution.TabIndex = 7;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(9, 190);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(113, 12);
            this.label5.TabIndex = 3;
            this.label5.Text = "GPI1 Active Level:";
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(9, 146);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(161, 12);
            this.label4.TabIndex = 2;
            this.label4.Text = "Unauthorization Execution:";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(9, 220);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(95, 12);
            this.label3.TabIndex = 2;
            this.label3.Text = "Trigger Operat:";
            // 
            // label9
            // 
            this.label9.AutoSize = true;
            this.label9.ForeColor = System.Drawing.SystemColors.ControlLight;
            this.label9.Location = new System.Drawing.Point(4, 179);
            this.label9.Name = "label9";
            this.label9.Size = new System.Drawing.Size(185, 12);
            this.label9.TabIndex = 16;
            this.label9.Text = "------------------------------";
            // 
            // label8
            // 
            this.label8.AutoSize = true;
            this.label8.ForeColor = System.Drawing.SystemColors.ControlLight;
            this.label8.Location = new System.Drawing.Point(6, 236);
            this.label8.Name = "label8";
            this.label8.Size = new System.Drawing.Size(185, 12);
            this.label8.TabIndex = 17;
            this.label8.Text = "------------------------------";
            // 
            // label10
            // 
            this.label10.AutoSize = true;
            this.label10.ForeColor = System.Drawing.SystemColors.ControlLight;
            this.label10.Location = new System.Drawing.Point(4, 295);
            this.label10.Name = "label10";
            this.label10.Size = new System.Drawing.Size(185, 12);
            this.label10.TabIndex = 18;
            this.label10.Text = "------------------------------";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(9, 108);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(149, 12);
            this.label2.TabIndex = 1;
            this.label2.Text = "Authorization Execution:";
            // 
            // label14
            // 
            this.label14.AutoSize = true;
            this.label14.ForeColor = System.Drawing.SystemColors.ControlLight;
            this.label14.Location = new System.Drawing.Point(4, 100);
            this.label14.Name = "label14";
            this.label14.Size = new System.Drawing.Size(185, 12);
            this.label14.TabIndex = 27;
            this.label14.Text = "------------------------------";
            // 
            // label16
            // 
            this.label16.AutoSize = true;
            this.label16.ForeColor = System.Drawing.SystemColors.ControlLight;
            this.label16.Location = new System.Drawing.Point(3, 57);
            this.label16.Name = "label16";
            this.label16.Size = new System.Drawing.Size(185, 12);
            this.label16.TabIndex = 32;
            this.label16.Text = "------------------------------";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(7, 41);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(35, 12);
            this.label1.TabIndex = 28;
            this.label1.Text = "Port:";
            // 
            // groupBox2
            // 
            this.groupBox2.Controls.Add(this.txt_VirtualCard);
            this.groupBox2.Controls.Add(this.btn_Generate);
            this.groupBox2.Controls.Add(this.btn_AddCard);
            this.groupBox2.Controls.Add(this.txt_RealCard);
            this.groupBox2.Controls.Add(this.label18);
            this.groupBox2.Controls.Add(this.label19);
            this.groupBox2.Dock = System.Windows.Forms.DockStyle.Top;
            this.groupBox2.Location = new System.Drawing.Point(200, 0);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(600, 40);
            this.groupBox2.TabIndex = 4;
            this.groupBox2.TabStop = false;
            // 
            // txt_VirtualCard
            // 
            this.txt_VirtualCard.Location = new System.Drawing.Point(455, 12);
            this.txt_VirtualCard.Name = "txt_VirtualCard";
            this.txt_VirtualCard.Size = new System.Drawing.Size(74, 21);
            this.txt_VirtualCard.TabIndex = 6;
            this.txt_VirtualCard.Text = "10000";
            this.txt_VirtualCard.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.txt_KeyPress);
            // 
            // btn_Generate
            // 
            this.btn_Generate.Location = new System.Drawing.Point(530, 12);
            this.btn_Generate.Name = "btn_Generate";
            this.btn_Generate.Size = new System.Drawing.Size(64, 23);
            this.btn_Generate.TabIndex = 2;
            this.btn_Generate.Text = "Generate";
            this.btn_Generate.UseVisualStyleBackColor = true;
            this.btn_Generate.Click += new System.EventHandler(this.btn_Generate_Click);
            // 
            // btn_AddCard
            // 
            this.btn_AddCard.Location = new System.Drawing.Point(248, 12);
            this.btn_AddCard.Name = "btn_AddCard";
            this.btn_AddCard.Size = new System.Drawing.Size(31, 23);
            this.btn_AddCard.TabIndex = 1;
            this.btn_AddCard.Text = "Add";
            this.btn_AddCard.UseVisualStyleBackColor = true;
            this.btn_AddCard.Click += new System.EventHandler(this.btn_AddCard_Click);
            // 
            // txt_RealCard
            // 
            this.txt_RealCard.Location = new System.Drawing.Point(67, 13);
            this.txt_RealCard.Name = "txt_RealCard";
            this.txt_RealCard.Size = new System.Drawing.Size(177, 21);
            this.txt_RealCard.TabIndex = 0;
            // 
            // label18
            // 
            this.label18.AutoSize = true;
            this.label18.Location = new System.Drawing.Point(6, 17);
            this.label18.Name = "label18";
            this.label18.Size = new System.Drawing.Size(65, 12);
            this.label18.TabIndex = 4;
            this.label18.Text = "Real Card:";
            // 
            // label19
            // 
            this.label19.AutoSize = true;
            this.label19.Location = new System.Drawing.Point(280, 17);
            this.label19.Name = "label19";
            this.label19.Size = new System.Drawing.Size(179, 12);
            this.label19.TabIndex = 5;
            this.label19.Text = "Generate Virtual Cards (pcs):";
            // 
            // txt_Log
            // 
            this.txt_Log.BackColor = System.Drawing.SystemColors.Window;
            this.txt_Log.Dock = System.Windows.Forms.DockStyle.Fill;
            this.txt_Log.Location = new System.Drawing.Point(200, 40);
            this.txt_Log.Multiline = true;
            this.txt_Log.Name = "txt_Log";
            this.txt_Log.ReadOnly = true;
            this.txt_Log.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txt_Log.Size = new System.Drawing.Size(600, 340);
            this.txt_Log.TabIndex = 1;
            // 
            // groupBox3
            // 
            this.groupBox3.Controls.Add(this.btn_SynchronizeWhitelist);
            this.groupBox3.Controls.Add(this.btn_CleanCard);
            this.groupBox3.Controls.Add(this.btn_CleanLog);
            this.groupBox3.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.groupBox3.Location = new System.Drawing.Point(200, 380);
            this.groupBox3.Name = "groupBox3";
            this.groupBox3.Size = new System.Drawing.Size(600, 40);
            this.groupBox3.TabIndex = 7;
            this.groupBox3.TabStop = false;
            // 
            // btn_SynchronizeWhitelist
            // 
            this.btn_SynchronizeWhitelist.Enabled = false;
            this.btn_SynchronizeWhitelist.ForeColor = System.Drawing.Color.Black;
            this.btn_SynchronizeWhitelist.Location = new System.Drawing.Point(6, 12);
            this.btn_SynchronizeWhitelist.Name = "btn_SynchronizeWhitelist";
            this.btn_SynchronizeWhitelist.Size = new System.Drawing.Size(182, 23);
            this.btn_SynchronizeWhitelist.TabIndex = 9;
            this.btn_SynchronizeWhitelist.Text = "Synchronize Whitelist";
            this.btn_SynchronizeWhitelist.UseVisualStyleBackColor = true;
            this.btn_SynchronizeWhitelist.Click += new System.EventHandler(this.btn_SynchronizeWhitelist_Click);
            // 
            // btn_CleanCard
            // 
            this.btn_CleanCard.ForeColor = System.Drawing.Color.Red;
            this.btn_CleanCard.Location = new System.Drawing.Point(442, 12);
            this.btn_CleanCard.Name = "btn_CleanCard";
            this.btn_CleanCard.Size = new System.Drawing.Size(75, 23);
            this.btn_CleanCard.TabIndex = 8;
            this.btn_CleanCard.Text = "Clean Card";
            this.btn_CleanCard.UseVisualStyleBackColor = true;
            this.btn_CleanCard.Click += new System.EventHandler(this.btn_CleanCard_Click);
            // 
            // btn_CleanLog
            // 
            this.btn_CleanLog.ForeColor = System.Drawing.Color.Red;
            this.btn_CleanLog.Location = new System.Drawing.Point(518, 12);
            this.btn_CleanLog.Name = "btn_CleanLog";
            this.btn_CleanLog.Size = new System.Drawing.Size(75, 23);
            this.btn_CleanLog.TabIndex = 7;
            this.btn_CleanLog.Text = "Clean Log";
            this.btn_CleanLog.UseVisualStyleBackColor = true;
            this.btn_CleanLog.Click += new System.EventHandler(this.btn_CleanLog_Click);
            // 
            // lbl_Message
            // 
            this.lbl_Message.AutoSize = true;
            this.lbl_Message.ForeColor = System.Drawing.Color.Red;
            this.lbl_Message.Location = new System.Drawing.Point(206, 362);
            this.lbl_Message.Name = "lbl_Message";
            this.lbl_Message.Size = new System.Drawing.Size(0, 12);
            this.lbl_Message.TabIndex = 8;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(800, 420);
            this.Controls.Add(this.lbl_Message);
            this.Controls.Add(this.txt_Log);
            this.Controls.Add(this.groupBox3);
            this.Controls.Add(this.groupBox2);
            this.Controls.Add(this.panel1);
            this.MaximizeBox = false;
            this.MaximumSize = new System.Drawing.Size(816, 459);
            this.MinimizeBox = false;
            this.MinimumSize = new System.Drawing.Size(816, 459);
            this.Name = "Form1";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Access Reader Demo";
            this.panel1.ResumeLayout(false);
            this.panel1.PerformLayout();
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
            this.groupBox3.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.Button btn_Set;
        private System.Windows.Forms.Button btn_Get;
        private System.Windows.Forms.Label label12;
        private System.Windows.Forms.TextBox txt_GPO1PutTime;
        private System.Windows.Forms.ComboBox cmb_GPO1ActiveLevel;
        private System.Windows.Forms.Label label11;
        private System.Windows.Forms.ComboBox cmb_GPI2TriggerOperat;
        private System.Windows.Forms.ComboBox cmb_GPI2ActiveLevel;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.ComboBox cmb_GPI1TriggerOperat;
        private System.Windows.Forms.ComboBox cmb_GPI1ActiveLevel;
        private System.Windows.Forms.ComboBox cmb_UnauthorizationExecution;
        private System.Windows.Forms.ComboBox cmb_AuthorizationExecution;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label9;
        private System.Windows.Forms.Label label8;
        private System.Windows.Forms.Label label10;
        public System.Windows.Forms.TextBox txt_Log;
        private System.Windows.Forms.Label label13;
        private System.Windows.Forms.ComboBox cmb_CommunicationInterface;
        private System.Windows.Forms.Label label14;
        private System.Windows.Forms.GroupBox groupBox2;
        private System.Windows.Forms.Button btn_AddCard;
        private System.Windows.Forms.TextBox txt_RealCard;
        private System.Windows.Forms.Button btn_Generate;
        private System.Windows.Forms.Button btn_Listen;
        private System.Windows.Forms.TextBox txt_listenPort;
        private System.Windows.Forms.Label label17;
        private System.Windows.Forms.TextBox txt_IP;
        private System.Windows.Forms.Label label15;
        private System.Windows.Forms.Button btn_Open;
        private System.Windows.Forms.TextBox txt_Port;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label16;
        private System.Windows.Forms.TextBox txt_VirtualCard;
        private System.Windows.Forms.Label label18;
        private System.Windows.Forms.Label label19;
        private System.Windows.Forms.GroupBox groupBox3;
        private System.Windows.Forms.Button btn_SynchronizeWhitelist;
        private System.Windows.Forms.Button btn_CleanCard;
        private System.Windows.Forms.Button btn_CleanLog;
        private System.Windows.Forms.Label lbl_Message;
    }
}

