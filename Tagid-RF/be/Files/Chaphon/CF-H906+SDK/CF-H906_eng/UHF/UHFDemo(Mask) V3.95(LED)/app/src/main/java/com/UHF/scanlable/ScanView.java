package com.UHF.scanlable;

import java.sql.Date;
import java.text.SimpleDateFormat;

import com.UHF.scanlable.R;
import com.rfid.trans.ReaderParameter;
import com.rfid.trans.ReaderHelp;
import android.app.Activity;
import android.media.SoundPool;
import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.WindowManager;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;

public class ScanView extends Activity implements OnClickListener{
	
	private TextView tvVersion;
	private TextView tvResult;
	private Spinner tvpowerdBm;
	private Spinner spType;
	private Spinner spMem;


	private Button bSetting;
	private Button bRead;
	
	private Button paramRead;
	private Button paramSet;

	private Button measure_loss;
	private Button getRange;
	private Button setRange;
	private int soundid;
	private int tty_speed = 57600;
	private byte addr = (byte) 0xff; 
	private String[] strBand =new String[6];
    private String[] strmaxFrm =null; 
    private String[] strminFrm =null;
	private String[] strtime =new String[256];

	private String[] strjtTime =new String[7];
	private String[] strBaudRate =new String[2];

	private String[] dwelltime =new String[254];

    private String[] strProfile =new String[12];
	private String[] strRange =new String[101];
	Spinner jgTime;
	private ArrayAdapter<String> spada_jgTime;

	Spinner spBand;
    Spinner spmaxFrm;
	Spinner spminFrm;
	Spinner sptime;
	Spinner spqvalue;
	Spinner spsession;
	Spinner sptidaddr;
	Spinner sptidlen;
	Spinner spbaudRate;
	Spinner spDwell;
	Spinner spTagfocus;
	Spinner spAntCheck;
    Spinner spProfilr;
	Spinner spRange;
	Spinner spCWtime;
	Button Setparam;
	Button Getparam;
	Button btSetBaud;
	Button btOpenrf;
	Button btCloserf;
	Button btAnswer;
	Button btActive;
	Button btSetFocus;
	Button btGetFocus;
    Button btSetPro;

	Button btSetAntCheck;
	Button btGetAntCheck;

    private TextView tvTemp;
    private TextView tvLoss;
    Button btReadTemp;
    Button btReadLoss;
    private ArrayAdapter<String> spada_Band;
    private ArrayAdapter<String> spada_maxFrm; 
    private ArrayAdapter<String> spada_minFrm;
	private ArrayAdapter<String> spada_time;
	private ArrayAdapter<String> spada_lowPwr;
	private ArrayAdapter<String> spada_qvalue;
    private ArrayAdapter<String> spada_session; 
    private ArrayAdapter<String> spada_tidaddr; 
    private ArrayAdapter<String> spada_tidlen;
	private ArrayAdapter<String> spada_baudrate;
	private ArrayAdapter<String> spada_cw;

	private ArrayAdapter<String> spada_dwell;
	private ArrayAdapter<String> spada_tagfocus;
    private ArrayAdapter<String> spada_profile;
	private ArrayAdapter<String> spada_range;
	private static final String TAG = "SacnView";
	private int ReaderType=-1;
	private int ModuleType=-1;

	private LinearLayout linefocus;
	private LinearLayout lineprofile;
	private LinearLayout linerange;
	private LinearLayout lineloss;
	private LinearLayout lineantcheck;
	EditText tvRun;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		// TODO Auto-generated method stub  properties
		super.onCreate(savedInstanceState);
		getWindow().setFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
				WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
		setContentView(R.layout.scan_view);
		initView();
		if(ModuleType==0)//953/963
		{
			ReaderParameter param = Reader.rrlib.GetInventoryPatameter();
			param.Session=0;
			Reader.rrlib.SetInventoryPatameter(param);
			ReadParam();
		}
		else if(ModuleType==1)//r2000
		{
			ReaderParameter param = Reader.rrlib.GetInventoryPatameter();
			param.Session=1;
			Reader.rrlib.SetInventoryPatameter(param);
			ReadParam();
		}
		else if(ModuleType==2)//ex10
		{
			ReaderParameter param = Reader.rrlib.GetInventoryPatameter();
			param.Session=254;
			Reader.rrlib.SetInventoryPatameter(param);
			ReadParam();
		}
		else if(ModuleType==3 || ModuleType==4)//c6
		{
			ReaderParameter param = Reader.rrlib.GetInventoryPatameter();
			param.Session=1;
			Reader.rrlib.SetInventoryPatameter(param);
			ReadParam();
		}
	}

	@Override
	protected void onResume() {
		// TODO Auto-generated method stub

		super.onResume();

		switch (Connect232.baud)
		{
			case 57600:
				spbaudRate.setSelection(0,true);
				break;
			case 115200:
				spbaudRate.setSelection(1,true);
				break;
		}
		if(ModuleType==0)//953/963
		{
			ReadParam();
			ReadInformation();
			getRangeControll();
		}
		else if(ModuleType==1)//r2000
		{
			ReadParam();
			ReadInformation();
			ReadProfile();
			ReadCheckAnt();
		}
		else if(ModuleType==2)//ex10
		{
			ReadParam();
			ReadInformation();
			ReadFocus();
			ReadProfile();
			ReadCheckAnt();
			getRangeControll();
		}
		else if(ModuleType==3)//c6
		{
			ReadParam();
			ReadInformation();
			ReadProfile();
		}
		else if(ModuleType==4)//FD
		{
			ReadParam();
			ReadInformation();
			ReadProfile();
		}

	}
	private void initView(){

        tvTemp = (TextView)findViewById(R.id.txt_tempe);
        tvLoss= (TextView)findViewById(R.id.txt_loss);
		tvRun = (EditText) findViewById(R.id.tv_runtime);

        btReadTemp = (Button)findViewById(R.id.bt_Readtemp);
        btReadLoss = (Button)findViewById(R.id.bt_Readloss);


        tvVersion = (TextView)findViewById(R.id.version);
		tvResult = (TextView)findViewById(R.id.param_result);

		tvpowerdBm = (Spinner)findViewById(R.id.power_spinner);
		ArrayAdapter<CharSequence> adapter3 =  ArrayAdapter.createFromResource(this, R.array.Power_select, android.R.layout.simple_spinner_item);
		adapter3.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		tvpowerdBm.setAdapter(adapter3);

		tvpowerdBm.setSelection(33, true);

		bSetting = (Button)findViewById(R.id.pro_setting);
		bRead = (Button)findViewById(R.id.pro_read);
		paramRead = (Button)findViewById(R.id.ivt_read);
		paramSet = (Button)findViewById(R.id.ivt_setting);
		btOpenrf = (Button)findViewById(R.id.ivt_open);
		btCloserf = (Button)findViewById(R.id.ivt_close);
		btAnswer = (Button)findViewById(R.id.bt_answer);
		btActive = (Button)findViewById(R.id.bt_active);
		btSetBaud = (Button)findViewById(R.id.bt_SetBdRate);
		btSetAntCheck = (Button)findViewById(R.id.bt_setantcheck);
		btGetAntCheck = (Button)findViewById(R.id.bt_getantcheck);
		btSetFocus = (Button)findViewById(R.id.bt_SetFocus);
		btGetFocus = (Button)findViewById(R.id.bt_GetFocus);
        btSetPro = (Button)findViewById(R.id.bt_SetProfile);
		getRange = (Button)findViewById(R.id.bt_GetRange);
		setRange = (Button)findViewById(R.id.bt_SetRange);

		btSetAntCheck.setOnClickListener(this);
		btGetAntCheck.setOnClickListener(this);
		bSetting.setOnClickListener(this);
		bRead.setOnClickListener(this);
		paramRead.setOnClickListener(this);
		paramSet.setOnClickListener(this);
		btOpenrf.setOnClickListener(this);
		btCloserf.setOnClickListener(this);
		btAnswer.setOnClickListener(this);
		btActive.setOnClickListener(this);
		btSetBaud.setOnClickListener(this);
        btReadLoss.setOnClickListener(this);
        btReadTemp.setOnClickListener(this);
		getRange.setOnClickListener(this);
		setRange.setOnClickListener(this);

		btSetFocus.setOnClickListener(this);
		btGetFocus.setOnClickListener(this);
        btSetPro.setOnClickListener(this);

		linefocus = (LinearLayout) findViewById(R.id.linetagfocus);
		lineprofile = (LinearLayout) findViewById(R.id.lineprogile);
		linerange = (LinearLayout) findViewById(R.id.linerange);
		lineloss = (LinearLayout) findViewById(R.id.lineloss);
		lineantcheck = (LinearLayout) findViewById(R.id.linecheckant);
		linefocus.setVisibility(View.GONE);
		linerange.setVisibility(View.GONE);
		lineprofile.setVisibility(View.GONE);
		lineloss.setVisibility(View.GONE);
		lineantcheck.setVisibility(View.GONE);
		//最大询查时间
		for(int index=0;index<256;index++)
		{
			strtime[index] = String.valueOf(index)+"*100ms";
		}
		sptime = (Spinner)findViewById(R.id.time_spinner);
		spada_time = new ArrayAdapter<String>(ScanView.this,
				android.R.layout.simple_spinner_item, strtime);
		spada_time.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		sptime.setAdapter(spada_time);
		sptime.setSelection(50,false);

		spCWtime = (Spinner)findViewById(R.id.timedelay_spinner);
		spada_cw = new ArrayAdapter<String>(ScanView.this,
				android.R.layout.simple_spinner_item, strtime);
		spada_cw.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		spCWtime.setAdapter(spada_cw);
		spCWtime.setSelection(5,false);

		////////////Ƶ��ѡ��
		strBand[0]="Chinese band2";
		strBand[1]="US band";
		strBand[2]="Korean band";
		strBand[3]="EU band";
		strBand[4]="Chinese band1";
		strBand[5]="ALL band";

		strBaudRate[0] = "57600bps";
		strBaudRate[1] = "115200bps";


		spBand=(Spinner)findViewById(R.id.band_spinner);  
		spada_Band = new ArrayAdapter<String>(ScanView.this,  
	             android.R.layout.simple_spinner_item, strBand);  
		spada_Band.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
		spBand.setAdapter(spada_Band);  
		spBand.setSelection(1,false); 
		SetFre(2);////��ʼ��Ƶ��
		 // ���Spinner�¼�����  
		spBand.setOnItemSelectedListener(new Spinner.OnItemSelectedListener() {  
        public void onItemSelected(AdapterView<?> arg0, View arg1,  
                int arg2, long arg3) {  
            // TODO Auto-generated method stub  
            // ������ʾ��ǰѡ�����  
            arg0.setVisibility(View.VISIBLE);  
            if(arg2==0)SetFre(1);
            if(arg2==1)SetFre(2);
            if(arg2==2)SetFre(3);
            if(arg2==3)SetFre(4);
            if(arg2==4)SetFre(8);
			if(arg2==5)SetFre(0);
            //ѡ��Ĭ��ֵ����ִ��  
        }  
        public void onNothingSelected(AdapterView<?> arg0) {  
            // TODO Auto-generated method stub  
        	}  
		});


		//strjtTime[0]="无间隔";
		for(int index=0;index<7;index++)
		{
			strjtTime[index] = String.valueOf(index*10)+"ms";
		}
		jgTime=(Spinner)findViewById(R.id.jgTime_spinner);
		spada_jgTime = new ArrayAdapter<String>(ScanView.this,
				android.R.layout.simple_spinner_item, strjtTime);
		spada_jgTime.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		jgTime.setAdapter(spada_jgTime);
		jgTime.setSelection(3,false);

		spqvalue=(Spinner)findViewById(R.id.qvalue_spinner);  
		ArrayAdapter<CharSequence> adapter =  ArrayAdapter.createFromResource(this, R.array.men_q, android.R.layout.simple_spinner_item);
		adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		spqvalue.setAdapter(adapter); 
		spqvalue.setSelection(6, true);
		
		
		spsession=(Spinner)findViewById(R.id.session_spinner);  
		ArrayAdapter<CharSequence> adapter1 =  ArrayAdapter.createFromResource(this, R.array.men_s, android.R.layout.simple_spinner_item);
		adapter1.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		spsession.setAdapter(adapter1); 
		spsession.setSelection(5, true);
		
		sptidaddr=(Spinner)findViewById(R.id.tidptr_spinner);  
		sptidlen=(Spinner)findViewById(R.id.tidlen_spinner);  
		ArrayAdapter<CharSequence> adapter2 =  ArrayAdapter.createFromResource(this, R.array.men_tid, android.R.layout.simple_spinner_item);
		adapter2.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		sptidaddr.setAdapter(adapter2); 
		sptidaddr.setSelection(0, true);
		sptidlen.setAdapter(adapter2); 
		sptidlen.setSelection(6, true);

		spbaudRate=(Spinner)findViewById(R.id.baud_spinner);
		spada_baudrate= new ArrayAdapter<String>(ScanView.this,
				android.R.layout.simple_spinner_item, strBaudRate);
		spada_baudrate.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		spbaudRate.setAdapter(spada_baudrate);



		////////////查询类型
		spType=(Spinner)findViewById(R.id.IvtType_spinner);
		ArrayAdapter<CharSequence> spada_Type = ArrayAdapter.createFromResource(this, R.array.IvtType_select, android.R.layout.simple_spinner_item);
		spada_Type.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		spType.setAdapter(spada_Type);
		spType.setSelection(0,false);


		////////////查询区域
		spMem=(Spinner)findViewById(R.id.mixmem_spinner);
		ArrayAdapter<CharSequence> spada_Mem = ArrayAdapter.createFromResource(this, R.array.readmen_select, android.R.layout.simple_spinner_item);
		spada_Mem.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		spMem.setAdapter(spada_Mem);
		spMem.setSelection(1,false);


		for(int index=2;index<256;index++)
		{
			dwelltime[index-2] = String.valueOf(index*100)+"ms";
		}
		spDwell=(Spinner)findViewById(R.id.dwell_spinner);
		spada_dwell = new ArrayAdapter<String>(ScanView.this,
				android.R.layout.simple_spinner_item, dwelltime);
		spada_dwell.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		spDwell.setAdapter(spada_dwell);
		spDwell.setSelection(48,false);


		spTagfocus=(Spinner)findViewById(R.id.focus_spinner);
		ArrayAdapter<CharSequence> spada_focus = ArrayAdapter.createFromResource(this, R.array.en_select, android.R.layout.simple_spinner_item);
		spada_focus.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		spTagfocus.setAdapter(spada_focus);
		spTagfocus.setSelection(0,false);

		spAntCheck=(Spinner)findViewById(R.id.checkant_spinner);
		ArrayAdapter<CharSequence> spada_antcheck = ArrayAdapter.createFromResource(this, R.array.en_select, android.R.layout.simple_spinner_item);
		spada_antcheck.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		spAntCheck.setAdapter(spada_antcheck);
		spAntCheck.setSelection(1,false);


		ReaderType = Reader.rrlib.GetReaderType();

		if(ReaderType==0x21 || ReaderType==0x28 || ReaderType==0x23 || ReaderType==0x37 || ReaderType==0x36)//R2000
		{
			strProfile =new String[4];
			strProfile[0]=" 0:40K, FM0,25us";
			strProfile[1]=" 1:250K,M4, 25us";
			strProfile[2]=" 2:300K,M4, 25us";
			strProfile[3]=" 3:400K,FM0,6.25us";
			ModuleType=1;
			lineprofile.setVisibility(View.VISIBLE);
		}
		else if(ReaderType==0x70 || ReaderType==0x71 || ReaderType ==0x31
		|| ReaderType==0xE3 || ReaderType==0xE5 || ReaderType ==0xE7)//Ex10
		{
			strProfile =new String[12];
			strProfile[0]="11:640K,FM0,7.5us";
			strProfile[1]=" 1:640K, M2,7.5us";
			strProfile[2]="15:640K, M4,7.5us";
			strProfile[3]="12:320K, M2, 15us";
			strProfile[4]=" 3:320K, M2, 20us";
			strProfile[5]=" 5:320K, M4, 20us";
			strProfile[6]=" 7:250K, M4, 20us";
			strProfile[7]="13:160K, M8, 20us";
			strProfile[8]="103:640K,FM0,6.25us";
			strProfile[9]="120:640K, M2,6.25us";
			strProfile[10]="202:426K,FM0, 15us";
			strProfile[11]="345:640K, M4,7.5us";
			ModuleType=2;
			linefocus.setVisibility(View.VISIBLE);
			lineprofile.setVisibility(View.VISIBLE);
			lineloss.setVisibility(View.VISIBLE);
			lineantcheck.setVisibility(View.VISIBLE);
			linerange.setVisibility(View.VISIBLE);
		}
		else if(ReaderType==0x61 || ReaderType==0x63 || ReaderType==0x65 || ReaderType==0x66)//C6
		{
			ModuleType=3;
			strProfile =new String[5];
			strProfile[0]=" 0:160K,FM0,12.5us";
			strProfile[1]=" 1:160K, M8,12.5us";
			strProfile[2]=" 2:250K,FM0,12.5us";
			strProfile[3]=" 3:320K, M4,6.25us";
			strProfile[4]=" 4:160K, M4,12.5us";
			lineprofile.setVisibility(View.VISIBLE);
		}
		else if(ReaderType==0x91)
		{
			ModuleType=4;
			strProfile =new String[9];
			strProfile[0]="0:80kHZ,FM0    ,Tari 25 us";
			strProfile[1]="1:250kHZ,Miller4,Tari 25 us";
			strProfile[2]="2:300kHZ,Miller4,Tari 25 us";
			strProfile[3]="3:400kHZ,FM0    ,Tari 6.25us";
			strProfile[4]="4:300kHZ,Miller2,Tari 25 us";
			strProfile[5]="5:300kHZ,Miller8,Tari 25 us";
			strProfile[6]="6: 80kHZ,Miller4,Tari 25 us";
			strProfile[7]="7:160kHZ,Miller4,Tari 25 us";
			strProfile[8]="8:400kHZ,Miller2,Tari 6.25us";
			lineprofile.setVisibility(View.VISIBLE);
			linerange.setVisibility(View.GONE);
		}
		else
		{
			ModuleType=0;
			linerange.setVisibility(View.VISIBLE);
		}

        spProfilr=(Spinner)findViewById(R.id.prof_spinner);
        spada_profile = new ArrayAdapter<String>(ScanView.this,
                android.R.layout.simple_spinner_item, strProfile);
        spada_profile.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spProfilr.setAdapter(spada_profile);
		if(ModuleType==2)
        	spProfilr.setSelection(5,false);
		else if(ModuleType==1)
			spProfilr.setSelection(1,false);
		else if(ModuleType==3)
			spProfilr.setSelection(3,false);
		else if(ModuleType== 4)
			spProfilr.setSelection(1,false);



		for(int index=0;index<=100;index++)
		{
			strRange[index] = String.valueOf(index);
		}
		spRange=(Spinner)findViewById(R.id.range_spinner);
		spada_range = new ArrayAdapter<String>(ScanView.this,
				android.R.layout.simple_spinner_item, strRange);
		spada_range.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		spRange.setAdapter(spada_range);
		spRange.setSelection(100,false);

	}

	private void ReadParam()
	{
		ReaderParameter param = Reader.rrlib.GetInventoryPatameter();
		sptidlen.setSelection(param.Length, true);
		sptidaddr.setSelection(param.WordPtr, true);
		spqvalue.setSelection(param.QValue,true);
		sptime.setSelection(param.ScanTime,true);
		int mRtype = param.IvtType;
		if(mRtype==0x11)mRtype=3;

		spType.setSelection(mRtype,true);
		spMem.setSelection(param.Memory-1,true);
		spCWtime.setSelection(ScanMode.cwDelayTime,true);

		int sessionindex = param.Session;
		if(sessionindex==255) sessionindex=4;
		if(sessionindex==254) sessionindex=5;
		if(sessionindex==253) sessionindex=6;
		if(sessionindex==252) sessionindex=7;
		if(sessionindex==251) sessionindex=8;
		spsession.setSelection(sessionindex,true);
		if(Reader.rrlib.ModuleType==2)
		{
			byte[]data = new byte[30];
			int[]len = new int[1];
			int fCmdRet = Reader.rrlib.GetCfgParameter((byte)7,data,len);
			if(fCmdRet==0 && len[0]==3)
			{
				jgTime.setSelection( data[0],true);
				spDwell.setSelection(data[1]-2,true);
			}
		}
		tvRun.setText(ScanMode.runtime+"");
		Reader.writelog(getString(R.string.get_success),tvResult);
	}

	private int ReaderCode=0;
	private int curband =0;
	private void ReadInformation()
	{
		byte[]Version=new byte[2];
		byte[]Power=new byte[1];
		byte[]band=new byte[1];
		byte[]MaxFre=new byte[1];
		byte[]MinFre=new byte[1];
		int result = Reader.rrlib.GetReaderInformation(Version, Power, band, MaxFre, MinFre);
		if(result==0)
		{
			String hvn = String.valueOf(Version[0]&255);
			if(hvn.length()==1)hvn="0"+hvn;
			String lvn = String.valueOf(Version[1]&255);
			if(lvn.length()==1)lvn="0"+lvn;
			ReaderCode = Reader.rrlib.GetReaderType();
			String ModuleInfo = "";
			if(ReaderCode==0x70 || ReaderCode==0x71 || ReaderCode==0x31) {
				byte[]Describe = new byte[16];
				result =  Reader.rrlib.GetModuleDescribe(Describe);
				String dscInfo = "";
				if(Describe[0]==0x00)
					dscInfo="S";
				else if(Describe[0]==0x01)
					dscInfo="Plus";
				else if(Describe[0]==0x02)
					dscInfo="Pro";
				ModuleInfo = hvn + "." + lvn + " (" + Integer.toHexString(ReaderCode)+"-"+dscInfo+ ")";
			}
			else
				ModuleInfo = hvn+"."+lvn+" ("+Integer.toHexString(ReaderCode)+")";
			tvVersion.setText(ModuleInfo);
			tvpowerdBm.setSelection(Power[0],true);
			curband = band[0];
			SetFre(band[0]);
			int bandindex = band[0];
			if(bandindex ==8)
			{
				bandindex=bandindex-4;
			}
			else if(bandindex==0)
			{
				bandindex = 5;
			}
			else
			{
				bandindex=bandindex-1;
			}
			spBand.setSelection(bandindex,true);
			spminFrm.setSelection(MinFre[0],true);
			spmaxFrm.setSelection(MaxFre[0],true);
			//sptime.setSelection(ScanTime[0]&255,true);
			Reader.writelog(getString(R.string.get_success),tvResult);
		}
		else
		{
			Reader.writelog(getString(R.string.get_failed),tvResult);
		}
	}
	private void ReadFocus()
	{
		byte[]data = new byte[250];
		int[] len = new int[1];
		int fCmdRet = Reader.rrlib.GetCfgParameter((byte)8,data,len);
		if(fCmdRet==0 && len[0]==1)
		{
			spTagfocus.setSelection(data[0],true);
			Reader.writelog(getString(R.string.get_success),tvResult);
		}
		else
		{
			Reader.writelog(getString(R.string.get_failed),tvResult);
		}
	}

	private void ReadCheckAnt()
	{
		byte[]AntCheck = new byte[1];
		int fCmdRet = Reader.rrlib.GetCheckAnt(AntCheck);
		if(fCmdRet==0)
		{
			spAntCheck.setSelection(AntCheck[0],true);
			Reader.writelog(getString(R.string.get_success),tvResult);
		}
		else
		{
			Reader.writelog(getString(R.string.get_failed),tvResult);
		}
	}
	private void getRangeControll()
	{
		byte[]data = new byte[250];
		int[] len = new int[1];
		int fCmdRet = Reader.rrlib.GetCfgParameter((byte)16,data,len);
		if(fCmdRet==0 && len[0]==4)
		{
			spRange.setSelection(data[3]&255,true);
			Reader.writelog(getString(R.string.get_success),tvResult);
		}
		else
		{
			Reader.writelog(getString(R.string.get_failed),tvResult);
		}
	}

	private void ReadProfile()
	{
		byte[]Profile= new byte[1];
		int result = Reader.rrlib.GetProfile(Profile);
		if(result==0)
		{
			int index = 0;
			if(ModuleType==2)
			{
				switch(Profile[0]&255)
				{
					case 11:
						index = 0;
						break;
					case 1:
						index = 1;
						break;
					case 15:
						index = 2;
						break;
					case 12:
						index = 3;
						break;
					case 3:
						index = 4;
						break;
					case 5:
						index = 5;
						break;
					case 7:
						index = 6;
						break;
					case 13:
						index = 7;
						break;
					case 50:
						index = 8;
						break;
					case 51:
						index = 9;
						break;
					case 52:
						index = 10;
						break;
					case 53:
						index = 11;
						break;
				}
				spProfilr.setSelection(index,true);
			}
			else if(ModuleType==3)
			{
				spProfilr.setSelection((Profile[0]&255)-0x10,true);
			}
			else if(ModuleType==4)
			{
				spProfilr.setSelection((Profile[0]&255)-0x20,true);
			}
			else
			{
				spProfilr.setSelection(Profile[0]&255,true);
			}
			Reader.writelog(getString(R.string.set_success),tvResult);
		}
		else if(ModuleType==3)
		{
			spProfilr.setSelection((Profile[0]&255)-0x10,true);
		}
		else if(ModuleType==4)
		{
			spProfilr.setSelection((Profile[0]&255)-0x20,true);
		}
		else
		{
			Reader.writelog(getString(R.string.set_failed),tvResult);
		}
	}
	@Override
	public void onClick(View view) {
		try{
			if(view == paramRead)
			{
				ReadParam();
			}
			else if(view == paramSet)
			{
				ScanMode.cwDelayTime = spCWtime.getSelectedItemPosition();
				ScanMode.runtime = (int)(Integer.valueOf(tvRun.getText().toString()));
				ReaderParameter param = Reader.rrlib.GetInventoryPatameter();
				param.Length = sptidlen.getSelectedItemPosition();
				param.WordPtr = sptidaddr.getSelectedItemPosition();
				param.QValue = spqvalue.getSelectedItemPosition();
				param.ScanTime = sptime.getSelectedItemPosition();
				int mRtype = spType.getSelectedItemPosition();
				if(mRtype==3)mRtype=0x11;
				param.IvtType = mRtype;
				param.Memory = spMem.getSelectedItemPosition()+1;
				int Session = spsession.getSelectedItemPosition();
				if(Session==4)Session=255;
				if(Session==5)Session=254;
				if(Session==6)Session=253;
				if(Session==7)Session=252;
				if(Session==8)Session=251;
				param.Session = Session;

				param.Interval = 0;
				Reader.rrlib.SetInventoryPatameter(param);
				if(Reader.rrlib.ModuleType==2)
				{
					int jgTimes = jgTime.getSelectedItemPosition();
					int dwell = spDwell.getSelectedItemPosition();
					param.Interval = 0;
					Reader.rrlib.SetInventoryPatameter(param);
					byte[]data = new byte[3];
					data[0] = (byte)jgTimes;
					data[1] = (byte)(dwell+2);
					data[2] = 2;
					int len = 3;
					int fCmdRet = Reader.rrlib.SetCfgParameter((byte)0,(byte)7,data,len);
				}
				Reader.writelog(getString(R.string.set_success),tvResult);
			}
			else if (view == bSetting){
				
				int MaxFre=0;
				int MinFre=0;
				int Power= tvpowerdBm.getSelectedItemPosition();
				int fband = spBand.getSelectedItemPosition();
				int band=0;
				if(fband==0)band=1;
				if(fband==1)band=2;
				if(fband==2)band=3;
				if(fband==3)band=4;
				if(fband==4)band=8;
				if(fband==5)band=0;
				int Frequent= spminFrm.getSelectedItemPosition();
				MinFre = Frequent;
				Frequent= spmaxFrm.getSelectedItemPosition();
				MaxFre = Frequent;
				int Antenna=0;

				String temp="";
				int result = Reader.rrlib.SetRfPower((byte)Power);
				if(result!=0)
				{
					temp=getString(R.string.power_error);
				}
				result = Reader.rrlib.SetRegion((byte)band,(byte)MaxFre,(byte)MinFre);
				if(result!=0)
				{
					if(temp=="")
					temp=getString(R.string.frequent_error);
					else
						temp+=(",\r\n"+getString(R.string.frequent_error));
				}
				if(temp!="")
				{
					Reader.writelog(temp,tvResult);
				}
				else
				{
					Reader.writelog(getString(R.string.set_success),tvResult);
				}
			}
			else if (view == setRange){
				int index = spRange.getSelectedItemPosition();
				byte[]data = new byte[4];
				data[0]=data[1]=data[2]=0;
				data[3] = (byte)index;
				int len = 4;
				int fCmdRet = Reader.rrlib.SetCfgParameter((byte)0,(byte)16,data,len);
				if(fCmdRet==0)
				{
					Reader.writelog(getString(R.string.set_success),tvResult);
				}
				else
				{
					Reader.writelog(getString(R.string.set_failed),tvResult);
				}
			}else if (view == getRange){
				getRangeControll();
			}
			else if(view == btGetAntCheck)
			{
				ReadCheckAnt();
			}
			else if(view == btSetAntCheck)
			{
				byte antcheck = (byte)spAntCheck.getSelectedItemPosition();
				int fCmdRet = Reader.rrlib.SetCheckAnt(antcheck);
				if(fCmdRet==0)
				{
					Reader.writelog(getString(R.string.set_success),tvResult);
				}
				else
				{
					Reader.writelog(getString(R.string.set_failed),tvResult);
				}
			}
			else if (view == bRead){
				try
				{
					ReadInformation();
				}catch(Exception ex)
				{}

			}
			else if(view == btSetBaud)
			{
				int index = spbaudRate.getSelectedItemPosition();
				int baudRate=57600;
				switch(index)
				{
					case 0:
						baudRate = 57600;
						break;
					case 1:
						baudRate = 115200;
						break;
				}
				int result = Reader.rrlib.SetBaudRate(baudRate);
				if(result==0)
				{
					Reader.writelog(getString(R.string.set_success),tvResult);
				}
				else
				{
					Reader.writelog(getString(R.string.set_failed),tvResult);
				}
			}
			else if(view == btSetFocus)
			{
				int index = spTagfocus.getSelectedItemPosition();
				byte[]data = new byte[1];
				data[0]=(byte)index;
				int len = 1;
				int fCmdRet = Reader.rrlib.SetCfgParameter((byte)0,(byte)8,data,len);
				if(fCmdRet==0)
				{
					Reader.writelog(getString(R.string.set_success),tvResult);
				}
				else
				{
					Reader.writelog(getString(R.string.set_failed),tvResult);
				}
			}
			else if(view == btGetFocus)
			{
				ReadFocus();

			}
			else if(view == btReadLoss)
			{
				byte[]Freq = new byte[4];
				byte[] loss = new byte[1];
				if(curband==4)
				{
					Freq[0]=(byte)0x00;
					Freq[1]=(byte)0x0D;
					Freq[2]=(byte)0x33;
					Freq[3]=(byte)0x4C;
				}
				else
				{
					Freq[0]=(byte)0x00;
					Freq[1]=(byte)0x0D;
					Freq[2]=(byte)0xF7;
					Freq[3]=(byte)0x32;
				}

				int fCmdRet = Reader.rrlib.MeasureReturnLoss(Freq,(byte)0x00,loss);
				if(fCmdRet==0)
				{
					tvLoss.setText(loss[0]+"");
					Reader.writelog(getString(R.string.get_success),tvResult);
				}
				else
				{
					Reader.writelog(getString(R.string.get_failed),tvResult);
				}
			}
            else if(view == btSetPro)
            {
                int index = spProfilr.getSelectedItemPosition();
				int Profile=5;
				if(ModuleType==2)
				{
					switch(index)
					{
						case 0:
							Profile = 11;
							break;
						case 1:
							Profile = 1;
							break;
						case 2:
							Profile = 15;
							break;
						case 3:
							Profile = 12;
							break;
						case 4:
							Profile = 3;
							break;
						case 5:
							Profile = 5;
							break;
						case 6:
							Profile = 7;
							break;
						case 7:
							Profile = 13;
							break;
						case 8:
							Profile = 50;
							break;
						case 9:
							Profile = 51;
							break;
						case 10:
							Profile = 52;
							break;
						case 11:
							Profile = 53;
							break;
					}
				}
				else if(ModuleType==3)
				{
					Profile = index+0x10;
				}
				else if(ModuleType==4)
				{
					Profile = index+0x20;
				}
				else
				{
					Profile = index;
				}

                int result = Reader.rrlib.SetProfile((byte)Profile);
                if(result==0)
                {
                    Reader.writelog(getString(R.string.set_success),tvResult);
                }
                else
                {
                    Reader.writelog(getString(R.string.set_failed),tvResult);
                }
            }
		}catch(Exception ex)
		{}
	}
	
	
	private void SetFre(int m)
	{
		if(m==1){ 
		    strmaxFrm=new String[20];
         	strminFrm=new String[20];
         	for(int i=0;i<20;i++){
         		String temp="";
         		float values=(float) (920.125 + i * 0.25);
         		temp=String.valueOf(values)+"MHz";
         		strminFrm[i]=temp;
         		strmaxFrm[i]=temp;
         	}
         	spmaxFrm=(Spinner)findViewById(R.id.max_spinner);  
         	spada_maxFrm = new ArrayAdapter<String>(ScanView.this,  
                      android.R.layout.simple_spinner_item, strmaxFrm);  
         	spada_maxFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
         	spmaxFrm.setAdapter(spada_maxFrm);  
         	spmaxFrm.setSelection(19,false);
         	
         	spminFrm=(Spinner)findViewById(R.id.min_spinner);  
         	spada_minFrm = new ArrayAdapter<String>(ScanView.this,  
                      android.R.layout.simple_spinner_item, strminFrm);  
         	spada_minFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
         	spminFrm.setAdapter(spada_minFrm);  
         	spminFrm.setSelection(0,false);
     }else if(m==2){
     	strmaxFrm=new String[50];
     	strminFrm=new String[50];
     	for(int i=0;i<50;i++){
     		String temp="";
     		float values=(float) (902.75 + i * 0.5);
     		temp=String.valueOf(values)+"MHz";
     		strminFrm[i]=temp;
     		strmaxFrm[i]=temp;
     	}
     	spmaxFrm=(Spinner)findViewById(R.id.max_spinner);  
     	spada_maxFrm = new ArrayAdapter<String>(ScanView.this,  
                  android.R.layout.simple_spinner_item, strmaxFrm);  
     	spada_maxFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
     	spmaxFrm.setAdapter(spada_maxFrm);  
     	spmaxFrm.setSelection(49,false);
     	
     	spminFrm=(Spinner)findViewById(R.id.min_spinner);  
     	spada_minFrm = new ArrayAdapter<String>(ScanView.this,  
                  android.R.layout.simple_spinner_item, strminFrm);  
     	spada_minFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
     	spminFrm.setAdapter(spada_minFrm);  
     	spminFrm.setSelection(0,false);
     }else if(m==3){
      	strmaxFrm=new String[32];
      	strminFrm=new String[32];
      	for(int i=0;i<32;i++){
      		String temp="";
      		float values=(float) (917.1 + i * 0.2);
      		temp=String.valueOf(values)+"MHz";
      		strminFrm[i]=temp;
      		strmaxFrm[i]=temp;
      	}
      	spmaxFrm=(Spinner)findViewById(R.id.max_spinner);  
      	spada_maxFrm = new ArrayAdapter<String>(ScanView.this,  
                   android.R.layout.simple_spinner_item, strmaxFrm);  
      	spada_maxFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
      	spmaxFrm.setAdapter(spada_maxFrm);  
      	spmaxFrm.setSelection(31,false);
      	
      	spminFrm=(Spinner)findViewById(R.id.min_spinner);  
      	spada_minFrm = new ArrayAdapter<String>(ScanView.this,  
                   android.R.layout.simple_spinner_item, strminFrm);  
      	spada_minFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
      	spminFrm.setAdapter(spada_minFrm);  
      	spminFrm.setSelection(0,false);
      }else if(m==4){
       	strmaxFrm=new String[15];
       	strminFrm=new String[15];
       	for(int i=0;i<15;i++){
       		String temp="";
       		float values=(float) (865.1 + i * 0.2);
       		temp=String.valueOf(values)+"MHz";
       		strminFrm[i]=temp;
       		strmaxFrm[i]=temp;
       	}
       	spmaxFrm=(Spinner)findViewById(R.id.max_spinner);  
       	spada_maxFrm = new ArrayAdapter<String>(ScanView.this,  
                    android.R.layout.simple_spinner_item, strmaxFrm);  
       	spada_maxFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
       	spmaxFrm.setAdapter(spada_maxFrm);  
       	spmaxFrm.setSelection(14,false);
       	
       	spminFrm=(Spinner)findViewById(R.id.min_spinner);  
       	spada_minFrm = new ArrayAdapter<String>(ScanView.this,  
                    android.R.layout.simple_spinner_item, strminFrm);  
       	spada_minFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
       	spminFrm.setAdapter(spada_minFrm);  
       	spminFrm.setSelection(0,false);
       }else if(m==8){
		    strmaxFrm=new String[20];
         	strminFrm=new String[20];
         	for(int i=0;i<20;i++){
         		String temp="";
         		float values=(float) (840.125 + i * 0.25);
         		temp=String.valueOf(values)+"MHz";
         		strminFrm[i]=temp;
         		strmaxFrm[i]=temp;
         	}
         	spmaxFrm=(Spinner)findViewById(R.id.max_spinner);  
         	spada_maxFrm = new ArrayAdapter<String>(ScanView.this,  
                      android.R.layout.simple_spinner_item, strmaxFrm);  
         	spada_maxFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
         	spmaxFrm.setAdapter(spada_maxFrm);  
         	spmaxFrm.setSelection(19,false);
         	
         	spminFrm=(Spinner)findViewById(R.id.min_spinner);  
         	spada_minFrm = new ArrayAdapter<String>(ScanView.this,  
                      android.R.layout.simple_spinner_item, strminFrm);  
         	spada_minFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);  
         	spminFrm.setAdapter(spada_minFrm);  
         	spminFrm.setSelection(0,false);
       }
		else if(m==0){
			strmaxFrm=new String[61];
			strminFrm=new String[61];
			for(int i=0;i<61;i++){
				String temp="";
				float values=(float) (840 + i * 2);
				temp=String.valueOf(values)+"MHz";
				strminFrm[i]=temp;
				strmaxFrm[i]=temp;
			}
			spmaxFrm=(Spinner)findViewById(R.id.max_spinner);
			spada_maxFrm = new ArrayAdapter<String>(ScanView.this,
					android.R.layout.simple_spinner_item, strmaxFrm);
			spada_maxFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
			spmaxFrm.setAdapter(spada_maxFrm);
			spmaxFrm.setSelection(60,false);

			spminFrm=(Spinner)findViewById(R.id.min_spinner);
			spada_minFrm = new ArrayAdapter<String>(ScanView.this,
					android.R.layout.simple_spinner_item, strminFrm);
			spada_minFrm.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
			spminFrm.setAdapter(spada_minFrm);
			spminFrm.setSelection(0,false);
		}
	}
}
