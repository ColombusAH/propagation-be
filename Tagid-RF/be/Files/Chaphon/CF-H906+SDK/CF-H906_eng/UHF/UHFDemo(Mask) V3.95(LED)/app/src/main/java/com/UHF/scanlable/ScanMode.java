package com.UHF.scanlable;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;

import com.UHF.scanlable.R;
import com.rfid.trans.MaskClass;
import com.rfid.trans.ReadTag;
import com.rfid.trans.TagCallback;
//import com.UHF.scanlable.UHfData.InventoryTagMap;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.ActivityGroup;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.device.DeviceManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.os.SystemClock;
import android.text.TextUtils;
import android.util.Log;
import android.view.ContextMenu;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.AdapterView.OnItemSelectedListener;
import android.widget.CompoundButton.OnCheckedChangeListener;
import android.widget.ArrayAdapter;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.PopupWindow;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.SimpleAdapter;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

public class ScanMode extends Activity implements OnClickListener, OnItemClickListener{

	public static int cwDelayTime=5;
	private int inventoryFlag = 1;
	Handler handler;
	private ArrayList<HashMap<String, String>> tagList;
	SimpleAdapter adapter;
	Button BtClear;
	TextView tv_count;
	TextView tv_time;
	TextView tv_alltag;
	TextView tv_speed;
	RadioGroup RgInventory;
	RadioButton RbInventorySingle;
	RadioButton RbInventoryLoop;
	Button Btimport;
	Button Btfilter;
	Button BtInventory;
	ListView LvTags;
	CheckBox chkled;
	String items[]=null;
	boolean chk[]=null;
	private Spinner spfactory;

	LinearLayout lyoutled;

	public static String epc;
	//private Button btnFilter;//过滤
	private LinearLayout llContinuous;
	private HashMap<String, String> map;
	PopupWindow popFilter;
	public boolean isStopThread=false;
	MsgCallback callback = new MsgCallback();
	private static final int MSG_UPDATE_LISTVIEW = 0;
	private static final int MSG_UPDATE_TIME = 1;
	private static final int MSG_UPDATE_SPEED = 2;
	private static final int MSG_UPDATE_STOP = 3;
	private Timer timer;
	public long beginTime;
	public long CardNumber;
	public static List<String> mlist = new ArrayList<String>();
	public long lastTime=0;
	public int lastCount=0;
	public boolean keyPress =false;
	public class FilterLed
	{
		String epc;
		boolean isChedk;
	}
	public static List<String> ledlist = new ArrayList<String>();
	public static int runtime=0;
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		// TODO Auto-generated method stub
		super.onCreate(savedInstanceState);
		getWindow().setFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
				WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
		try
		{

			setContentView(R.layout.query);
			chkled = (CheckBox) findViewById(R.id.chkLed);
			chkled.setOnClickListener(this);
			lyoutled = (LinearLayout) findViewById(R.id.layoutled);
			lyoutled.setVisibility(View.GONE);

			spfactory=(Spinner)findViewById(R.id.spfactory);
			ArrayAdapter<CharSequence> spada_Mem = ArrayAdapter.createFromResource(this, R.array.arrayfactory, android.R.layout.simple_spinner_item);
			spada_Mem.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
			spfactory.setAdapter(spada_Mem);
			spfactory.setSelection(0,false);

			tagList = new ArrayList<HashMap<String, String>>();
			BtClear = (Button) findViewById(R.id.BtClear);
			Btfilter =  (Button) findViewById(R.id.Btfilter);
			Btimport = (Button)findViewById(R.id.BtImport);
			tv_count = (TextView)findViewById(R.id.tv_count);
			tv_time = (TextView)findViewById(R.id.tv_times);
			tv_alltag = (TextView)findViewById(R.id.tv_alltag);
			tv_speed = (TextView)findViewById(R.id.tv_tagspeed);
			RgInventory = (RadioGroup) findViewById(R.id.RgInventory);
			String tr = "";
			RbInventorySingle = (RadioButton) findViewById(R.id.RbInventorySingle);
			RbInventoryLoop = (RadioButton) findViewById(R.id.RbInventoryLoop);

			BtInventory = (Button)findViewById(R.id.BtInventory);
			LvTags = (ListView) findViewById(R.id.LvTags);
			LvTags.setOnCreateContextMenuListener(lvjzwOnCreateContextMenuListener);
			llContinuous = (LinearLayout)findViewById(R.id.llContinuous);

			adapter = new SimpleAdapter(this, tagList, R.layout.listtag_items,
					new String[]{"tagUii", "tagLen", "tagCount", "tagRssi"},
					new int[]{R.id.TvTagUii, R.id.TvTagLen, R.id.TvTagCount,
							R.id.TvTagRssi});

			Btfilter.setOnClickListener(this);
			BtClear.setOnClickListener(this);
			Btimport.setOnClickListener(this);
			RgInventory.setOnCheckedChangeListener(new RgInventoryCheckedListener());
			BtInventory.setOnClickListener(this);

			Reader.rrlib.SetCallBack(callback);

			LvTags.setAdapter(adapter);
			clearData();
			Log.i("MY", "UHFReadTagFragment.EtCountOfTags=" + tv_count.getText());
			handler = new Handler() {
				@SuppressLint("HandlerLeak")
				@Override
				public void handleMessage(Message msg) {
					try{
						switch (msg.what) {
							case MSG_UPDATE_LISTVIEW:
								String result = msg.obj+"";
								String[] strs = result.split(",");
								if(strs.length==2)
								{
									addEPCToList(strs[0], strs[1]);
								}
								else
								{
									addEPCToList(strs[0]+","+strs[1], strs[2]);
								}

								break;
							case MSG_UPDATE_TIME:
								String ReadTime = msg.obj+"";
								long CurTime = Integer.valueOf(ReadTime);
								long hour=CurTime/(60*60*1000);
								long min=(CurTime/1000 - (hour*60*60))/60;
								long sec=(CurTime/1000-hour*60*60-min*60);
								String strHour = String.valueOf(hour);
								if(strHour.length()<2) strHour="0"+strHour;
								String strmin = String.valueOf(min);
								if(strmin.length()<2) strmin="0"+strmin;
								String strsec = String.valueOf(sec);
								if(strsec.length()<2) strsec="0"+strsec;
								tv_time.setText(strHour+":"+strmin+":"+strsec);
								break;
							case MSG_UPDATE_SPEED:
								String readSpeed = msg.obj+"";
								tv_speed.setText(readSpeed);
								break;
							case MSG_UPDATE_STOP:
								if(timer != null){
									timer.cancel();
									timer = null;
									BtInventory.setText(getString(R.string.btStoping));
								}
								setViewEnabled(true);
								BtInventory.setText(getString(R.string.btInventory));

								if(ledlist.size()==0)
								{
									items=new String[tagList.size()];
									chk=new boolean[tagList.size()];
									for(int i=0;i<tagList.size();i++)
									{
										items[i]=tagList.get(i).get("tagUii");
										chk[i]=false;
									}
								}

								break;
							default:
								break;
						}
					}catch(Exception ex)
					{ex.toString();}
				}
			};
		}
		catch(Exception e)
		{

		}
	}

	public class RgInventoryCheckedListener implements RadioGroup.OnCheckedChangeListener {
		@Override
		public void onCheckedChanged(RadioGroup group, int checkedId) {
			if (checkedId == RbInventorySingle.getId()) {
				inventoryFlag = 0;
			} else if (checkedId == RbInventoryLoop.getId()) {
				inventoryFlag = 1;
			}
		}
	}

	private void setViewEnabled(boolean enabled) {
		RbInventorySingle.setEnabled(enabled);
		RbInventoryLoop.setEnabled(enabled);
		//   btnFilter.setEnabled(enabled);
		BtClear.setEnabled(enabled);
		chkled.setEnabled(enabled);
		if(enabled)
		{
			Btfilter.setEnabled(enabled);
			BtInventory.setEnabled(enabled);
		}
	}


	public int checkIsExist(String strEPC) {
		int existFlag = -1;
		if (strEPC==null ||strEPC.length()==0) {
			return existFlag;
		}
		String tempStr = "";
		for (int i = 0; i < tagList.size(); i++) {
			HashMap<String, String> temp = new HashMap<String, String>();
			temp = tagList.get(i);
			tempStr = temp.get("tagUii");
			if (strEPC.equals(tempStr)) {
				existFlag = i;
				break;
			}
		}
		return existFlag;
	}

	private void clearData() {
		tv_count.setText("0");
		tv_time.setText("00:00:00");
		tv_alltag.setText("0");
		tv_speed.setText("0");
		tagList.clear();
		mlist.clear();
		CardNumber =0;
		items=null;
		chk=null;
		ledlist.clear();
		Log.i("MY", "tagList.size " + tagList.size());
		adapter.notifyDataSetChanged();
	}
	/**
	 * 添加EPC到列表中
	 *
	 * @param
	 */
	private void addEPCToList(String rfid, String rssi) {
		if (!TextUtils.isEmpty(rfid)) {
			String epc="";
			String[] data = rfid.split(",");
			if(data.length==1)
			{
				epc = data[0];
			}
			else
			{
				epc = "EPC:"+data[0]+"\r\nMem:"+data[1];
			}

			int index = checkIsExist(epc);
			map = new HashMap<String, String>();

			map.put("tagUii", epc);
			map.put("tagCount", String.valueOf(1));
			map.put("tagRssi", rssi);
			CardNumber++;
			if (index == -1) {
				tagList.add(map);
				LvTags.setAdapter(adapter);
				tv_count.setText("" + adapter.getCount());
				mlist.add(data[0]);
			} else {
				int tagcount = Integer.parseInt(
						tagList.get(index).get("tagCount"), 10) + 1;

				map.put("tagCount", String.valueOf(tagcount));

				tagList.set(index, map);

			}
			tv_alltag.setText(String.valueOf(CardNumber));
			adapter.notifyDataSetChanged();

		}
	}
	/**
	 *  是否开启 手柄按钮 扫码二维码 （扫描头出光）
	 *  在自己的业务逻辑需要关闭或打开之前，调用该方法（注意：不能在按下手柄按钮后调用，因为按钮按下后就会触发出光扫码）。
	 * @param isopen     true:开启   false:关闭
	 */
	private void setOpenScan523(boolean isopen) {
		try{
			DeviceManager mDeviceManager = new DeviceManager();
			if (mDeviceManager != null) {
				if (isopen) {
					//TODO 设置触发 523键值(手柄按钮) 扫描出光
					mDeviceManager.setSettingProperty("persist-persist.sys.rfid.key", "0-");
					mDeviceManager.setSettingProperty("persist-persist.sys.scan.key", "520-521-522-523-");//这里入参传入了哪些键值，在按下键值的的时候就会调起扫描头出光
				}else {
					//TODO 设置触发 523键值(手柄按钮) 不扫描出光
					mDeviceManager.setSettingProperty("persist-persist.sys.rfid.key", "0-");
					mDeviceManager.setSettingProperty("persist-persist.sys.scan.key", "520-521-522-");//这里入参传入了哪些键值，在按下键值的的时候就会调起扫描头出光
				}
			}
		}catch(Exception ex)
		{}
	}
	@Override
	protected void onResume() {
		// TODO Auto-generated method stub
		super.onResume();
		setOpenScan523(false);
		isStopThread =false;
	}

	@Override
	public void onClick(View arg0) {
		try
		{
			if(arg0 == BtInventory)
			{
				readTag();
			}
			else if(arg0 == BtClear)
			{
				clearData();
			}
			else if(arg0 ==chkled)
			{
				if(chkled.isChecked())
				{
					lyoutled.setVisibility(View.VISIBLE);
				}
				else
				{
					lyoutled.setVisibility(View.GONE);
				}
			}
			else if(arg0==Btfilter)
			{
				AlertDialog.Builder dialog = new AlertDialog.Builder(this);
				dialog.setTitle(getString(R.string.strselecttag));
				dialog.setPositiveButton(getString(R.string.strcancle), null);
				dialog.setPositiveButton(getString(R.string.strok), null);


				dialog.setMultiChoiceItems(items, chk, new DialogInterface.OnMultiChoiceClickListener() {

					@Override
					public void onClick(DialogInterface dialog, int which, boolean isChecked) {
						FilterLed led = new FilterLed();
						led.epc = items[which];
						led.isChedk = isChecked;
						if(isChecked)
						{
							if(ledlist.indexOf(led.epc)==-1)
							{
								ledlist.add(led.epc);
							}
						}
						else
						{
							if(ledlist.indexOf(led.epc)!=-1)
								ledlist.remove(led.epc);
						}
						chk[which] = isChecked;
					}
				}).create();
				dialog.show();
			}
			else if(arg0 == Btimport)
			{
				if(tagList.size()==0) {
					Toast.makeText(getApplicationContext(),getString(R.string.msgNodata),Toast.LENGTH_SHORT).show();
					return;
				}
				boolean re = FileImport.daochu("", tagList);
				if (re) {
					Toast.makeText(getApplicationContext(),getString(R.string.msgImportsuc),Toast.LENGTH_SHORT).show();
					//clearData();
				}
				else
				{
					Toast.makeText(getApplicationContext(),getString(R.string.msgImportfailed),Toast.LENGTH_SHORT).show();
				}
			}
		}
		catch(Exception e)
		{
			stopInventory();
		}
	}

	private void readTag() {
		epc="";
		if (BtInventory.getText().equals(getString(R.string.btInventory)))// 识别标签
		{
			switch (inventoryFlag) {
				case 0:// 单步
				{
					List<ReadTag> newlist = new ArrayList<ReadTag>();
					//int result =Reader.rrlib.InventoryOnce((byte)0,(byte)4,(byte)0,(byte)0,(byte)0x80,(byte)0,(byte)10,newlist);
					Reader.rrlib.ScanRfid();
				}
				break;
				case 1:
				{
					int result =-1;
					if(chkled.isChecked()) {
						{
							int mtype = spfactory.getSelectedItemPosition();
							List<MaskClass> MaskList = null;
							if(ledlist.size()>0)
							{
								MaskList = new ArrayList<MaskClass>();
								for(int k=0;k<ledlist.size();k++)
								{
									MaskClass mask= new MaskClass();
									mask.MaskAdr[0]=0;
									mask.MaskAdr[1]=0x20;
									mask.MaskMem=1;
									mask.MaskLen = (byte)(ledlist.get(k).length()*4);
									mask.MaskData = Util.hexStringToBytes(ledlist.get(k));
									MaskList.add(mask);
								}
							}

							byte opt=1;
							byte cfgNo = 0x16;
							byte[]cfgData = new byte[256];
							int len=1;
							cfgData[0]=0;//不关CW
							int fCmdRet = Reader.rrlib.SetCfgParameter(opt,cfgNo,cfgData,len);
							cfgNo = 0x15;
							len=1;
							cfgData[0]=(byte)(cwDelayTime);
							fCmdRet = Reader.rrlib.SetCfgParameter(opt,cfgNo,cfgData,len);
							result = Reader.rrlib.StartInventoryLed(mtype, MaskList);
						}
					}
					else
						result = Reader.rrlib.StartRead();
					if(result==0)
					{
						Btfilter.setEnabled(false);
						lastTime = System.currentTimeMillis();
						lastCount=0;
						BtInventory.setText(getString(R.string.title_stop_Inventory));
						setViewEnabled(false);
						if(timer == null) {
							beginTime = System.currentTimeMillis();
							timer = new Timer();
							timer.schedule(new TimerTask() {
								@Override
								public void run() {
									long ReadTime = System.currentTimeMillis() - beginTime;
									Message msg = handler.obtainMessage();
									msg.what = MSG_UPDATE_TIME;
									msg.obj = String.valueOf(ReadTime) ;
									handler.sendMessage(msg);
									if(runtime!=0)
									{
										if(ReadTime>(runtime*1000))
										{
											stopInventory();
										}
									}
								}
							}, 0, 200);
						}
					}
				}
				break;
				default:
					break;
			}
		} else {// 停止识别

			stopInventory();
		}
	}
	private void stopInventory(){
		if(chkled.isChecked())
		{

			Reader.rrlib.StopInventoryLed();
			SystemClock.sleep(100);
			byte opt=1;
			byte cfgNo = 0x16;
			byte[]cfgData = new byte[256];
			int len=1;
			cfgData[0]=1;//关CW
			int fCmdRet = Reader.rrlib.SetCfgParameter(opt,cfgNo,cfgData,len);
			cfgNo = 0x15;
			len=1;
			cfgData[0]=(byte)(cwDelayTime/100);
			fCmdRet = Reader.rrlib.SetCfgParameter(opt,cfgNo,cfgData,len);
		}
		else
			Reader.rrlib.StopRead();
	}

	public class MsgCallback implements TagCallback {

		@Override
		public void tagCallback(ReadTag arg0) {

			// TODO Auto-generated method stub
			String epc="";
			String mem="";
			if(arg0.epcId!=null)
				epc = arg0.epcId.toUpperCase();
			if(arg0.memId!=null)
				mem = arg0.memId.toUpperCase();

			String rssi = String.valueOf(arg0.rssi);
			Message msg = handler.obtainMessage();

			msg.what = MSG_UPDATE_LISTVIEW;
			if(mem.length()==0)
				msg.obj =epc+","+rssi ;
			else
				msg.obj =epc+","+mem+","+rssi ;
			handler.sendMessage(msg);

			lastCount++;
			if(System.currentTimeMillis() - lastTime>=1000)
			{
				msg = handler.obtainMessage();
				msg.what = MSG_UPDATE_SPEED;
				msg.obj = ((lastCount*1000)/(System.currentTimeMillis() - lastTime)) + "";
				handler.sendMessage(msg);
				lastTime = System.currentTimeMillis();
				lastCount=0;
			}
		}

		@Override
		public void StopReadCallBack() {
			// TODO Auto-generated method stub

			Message msg = handler.obtainMessage();
			msg.what = MSG_UPDATE_STOP;
			msg.obj ="" ;
			handler.sendMessage(msg);
		}
	};

	@Override
	public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {

	}

	/**
	 * 长按弹出下拉菜单 ,此事件中可弹出下拉框
	 */
	View.OnCreateContextMenuListener lvjzwOnCreateContextMenuListener = new View.OnCreateContextMenuListener()
	{

		@Override
		public void onCreateContextMenu(ContextMenu menu, View v, ContextMenu.ContextMenuInfo menuInfo)
		{
			menu.setHeaderTitle(getString(R.string.strtagoperate));//标题
			menu.add(0, 1, 0, getString(R.string.strreadandwrite));//下拉菜单
			menu.add(0, 2, 1, getString(R.string.strfindtag));//下拉菜单
		}
	};

	/**
	 * 长按菜单响应函数 并获取选中的listview行内容
	 */
	@Override
	public boolean onContextItemSelected(MenuItem item) {

		ContextMenu.ContextMenuInfo info = item.getMenuInfo();
		AdapterView.AdapterContextMenuInfo contextMenuInfo = (AdapterView.AdapterContextMenuInfo) info;
		int position = contextMenuInfo.position;
		epc = tagList.get(position).get("tagUii");
		if(item.getItemId()==1)
		{
			MainActivity.myTabHost.setCurrentTab(2);
		}
		else
		{
			MainActivity.myTabHost.setCurrentTab(1);
		}


		return false;
	}

	@Override
	protected void onPause() {
		// TODO Auto-generated method stub
		super.onPause();
		setOpenScan523(true);
		stopInventory();
	}

	@Override
	protected void onDestroy() {
		// TODO Auto-generated method stub
		super.onDestroy();
	}

	/**
	 *按键扫描RFID
	 **/
	@Override
	public boolean onKeyDown(int keyCode, KeyEvent event) {
		if(keyCode==523 && !keyPress)
		{
			keyPress = true;
			readTag();
		}
		else if (keyCode == KeyEvent.KEYCODE_BACK) {
			finish();
			return true;
		}
		return super.onKeyDown(keyCode, event);
	}

	/**
	 *按键扫描RFID
	 **/
	@Override
	public boolean onKeyUp(int keyCode, KeyEvent event) {
		if(keyCode==523)
		{
			keyPress =false;
		}
		return super.onKeyUp(keyCode, event);
	}

}
