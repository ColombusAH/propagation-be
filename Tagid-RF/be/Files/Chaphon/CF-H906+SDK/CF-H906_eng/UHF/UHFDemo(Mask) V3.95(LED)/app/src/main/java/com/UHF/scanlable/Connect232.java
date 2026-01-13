package com.UHF.scanlable;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.security.InvalidParameterException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import com.UHF.scanlable.R;
import com.rfid.trans.RFIDLogCallBack;
import com.rfid.trans.ReaderParameter;

import android.Manifest;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.media.AudioManager;
import android.media.SoundPool;
import android.os.Bundle;
import android.app.Activity;
import android.content.Intent;
import android.os.SystemClock;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.WindowManager;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.RadioButton;
import android.widget.Spinner;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Toast;
public class Connect232 extends AppCompatActivity {


		private static final String TAG = "COONECTRS232";
		private static String devport = "/dev/ttyHSL0";
		private static final boolean DEBUG = true;
		private TextView mConectButton;

		private RadioButton mBaud57600View,mBaud115200View;

		private int mPosPort = -1;

		public static int baud = 115200;
		@Override
		protected void onCreate(Bundle savedInstanceState) {
			super.onCreate(savedInstanceState);
			getWindow().setFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
					WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
			setContentView(R.layout.activity_connect232);
			mVirtualKeyListenerBroadcastReceiver = new VirtualKeyListenerBroadcastReceiver();
			IntentFilter intentFilter = new IntentFilter(Intent.ACTION_CLOSE_SYSTEM_DIALOGS);
			this.registerReceiver(mVirtualKeyListenerBroadcastReceiver, intentFilter);
			initSound();
			verifyStoragePermissions(this);
			mConectButton = (TextView) findViewById(R.id.textview_connect);


			mBaud57600View =  (RadioButton) findViewById(R.id.baud_57600);
			mBaud115200View =  (RadioButton) findViewById(R.id.baud_115200);

			baud = 115200;
			mBaud57600View.setOnClickListener(new OnClickListener() {
				@Override
				public void onClick(View v) {
					baud = 57600;
				}
			});
			mBaud115200View.setOnClickListener(new OnClickListener() {
				@Override
				public void onClick(View v) {
					baud = 115200;
				}
			});

			mConectButton.setOnClickListener(new OnClickListener() {
				@Override
				public void onClick(View v) {
					try {
						int result = Reader.rrlib.Connect(devport, 57600,1);
						if(result==0){
							baud = 57600;
							mBaud57600View.setChecked(true);
							initRfid();
							Intent intent;
							intent = new Intent().setClass(Connect232.this, MainActivity.class);
							startActivity(intent);
						}
						else
						{
							result = Reader.rrlib.Connect(devport, 115200,1);
							if(result==0){
								baud = 115200;
								mBaud115200View.setChecked(true);
								initRfid();
								Intent intent;
								intent = new Intent().setClass(Connect232.this, MainActivity.class);
								startActivity(intent);
							}
							else
							{
								Toast.makeText(
										getApplicationContext(),
										getString(R.string.openport_failed),
										Toast.LENGTH_SHORT).show();
							}
						}
					}catch (Exception e) 
					{
						Toast.makeText(
								getApplicationContext(),
								getString(R.string.openport_failed),
								Toast.LENGTH_SHORT).show();
					}
				}
			});
		}
	private void initRfid()
	{
		int ReaderType = Reader.rrlib.GetReaderType();
		ReaderParameter param = Reader.rrlib.GetInventoryPatameter();
		if(ReaderType==0x21 || ReaderType==0x28 || ReaderType==0x23 || ReaderType==0x37 || ReaderType==0x36)//R2000
		{
			param.Session=1;
		}
		else if(ReaderType==0x70 || ReaderType==0x71 || ReaderType ==0x31)//Ex10
		{
			param.Session=254;
		}
		else if(ReaderType==0x61 || ReaderType==0x63 || ReaderType==0x65 || ReaderType==0x66)//C6
		{
			param.Session=1;
		}
		else
		{
			param.Session=0;
		}
		Reader.rrlib.SetInventoryPatameter(param);
	}
	private static final int REQUEST_EXTERNAL_STORAGE = 1;
	private static String[] PERMISSIONS_STORAGE = {
			Manifest.permission.READ_EXTERNAL_STORAGE,
			Manifest.permission.WRITE_EXTERNAL_STORAGE
	};

	public static void verifyStoragePermissions(Activity activity) {

		// Check if we have write permission
		int permission = ActivityCompat.checkSelfPermission(activity, Manifest.permission.WRITE_EXTERNAL_STORAGE);

		if (permission != PackageManager.PERMISSION_GRANTED) {
			ActivityCompat.requestPermissions(
					activity,
					PERMISSIONS_STORAGE,
					REQUEST_EXTERNAL_STORAGE
			);
		}
	}

    static HashMap<Integer, Integer> soundMap = new HashMap<Integer, Integer>();
    private static SoundPool soundPool;
    private static float volumnRatio;
    private static AudioManager am;
    private  void initSound(){
        soundPool = new SoundPool(10, AudioManager.STREAM_MUSIC, 5);
        soundMap.put(1, soundPool.load(this, R.raw.barcodebeep, 1));
        am = (AudioManager) this.getSystemService(AUDIO_SERVICE);// 实例化AudioManager对象
        Reader.rrlib.SetSoundID(soundMap.get(1),soundPool);
    }

	@Override
	protected void onResume() {
		// TODO Auto-generated method stub
		//Reader.rrlib.PowerControll(null,true);
		OtgUtils.setPOGOPINEnable(true);
		super.onResume();
	}
		public boolean onKeyDown(int keyCode, KeyEvent event) {
			if (keyCode == KeyEvent.KEYCODE_BACK) {
				
				finish();

				return true;
			}
			return super.onKeyDown(keyCode, event);
		}
		
		@Override
		protected void onDestroy() {
			// TODO Auto-generated method stub
			//Reader.rrlib.PowerControll(null,false);
			OtgUtils.setPOGOPINEnable(false);
			this.unregisterReceiver(mVirtualKeyListenerBroadcastReceiver);
			super.onDestroy();
		}


	private VirtualKeyListenerBroadcastReceiver mVirtualKeyListenerBroadcastReceiver;
	public  static boolean mSwitchFlag = false;
	private class VirtualKeyListenerBroadcastReceiver extends BroadcastReceiver {
		private final String SYSTEM_REASON = "reason";
		private final String SYSTEM_HOME_KEY = "homekey";
		private final String SYSTEM_RECENT_APPS = "recentapps";

		@Override
		public void onReceive(Context context, Intent intent) {
			String action = intent.getAction();
			if (action.equals(Intent.ACTION_CLOSE_SYSTEM_DIALOGS)) {
				String systemReason = intent.getStringExtra(SYSTEM_REASON);
				if (systemReason != null) {
					mSwitchFlag = true;
					if (systemReason.equals(SYSTEM_HOME_KEY)) {
						System.out.println("Press HOME key");
						OtgUtils.setPOGOPINEnable(false);
					} else if (systemReason.equals(SYSTEM_RECENT_APPS)) {
						System.out.println("Press RECENT_APPS key");
						OtgUtils.setPOGOPINEnable(true);
						//Reader.rrlib.PowerControll(null,false);
						//mSwitchFlag = true;
					}

				}
			}
		}
	}
}
