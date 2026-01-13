package com.UHF.scanlable;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.device.DeviceManager;
import android.os.Handler;
import android.os.Message;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.rfid.trans.ReadTag;



public class Finding extends Activity implements View.OnClickListener {
    private CircleProgress mCircleProgress;
    TextView epcid;
    Button btFinding;
    private volatile boolean mWorking = true;
    private volatile Thread mThread=null;
    Handler handler;
    int rssi=0;
    public boolean keyPress =false;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_finding);
        mCircleProgress = (CircleProgress) findViewById(R.id.circle_progress);
        epcid =(TextView)findViewById(R.id.epc_id);
        btFinding = (Button)findViewById(R.id.btfind);
        btFinding.setOnClickListener(this);
        handler = new Handler() {
            @SuppressLint("HandlerLeak")
            @Override
            public void handleMessage(Message msg) {
                try{
                    switch (msg.what) {
                        case 0:
                            String rssistr = msg.obj+"";
                            int rssi = (int)Integer.valueOf(rssistr);
                            mCircleProgress.setValue((float)rssi);
                            break;
                        default:
                            break;
                    }
                }catch(Exception ex)
                {ex.toString();}
            }
        };
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
        epcid.setText(ScanMode.epc);
        mCircleProgress.setValue(0.00f);
        setOpenScan523(false);
        super.onResume();
    }

    @Override
    protected void onPause() {
        // TODO Auto-generated method stub
        super.onPause();
        setOpenScan523(true);
    }

    @Override
    public void onClick(View v) {
        if(v == btFinding)
        {
            readTag();

        }
    }

    private void readTag()
    {
        if(btFinding.getText().toString().equals(getString(R.string.finding)))
        {
            if(mThread==null)
            {
                mWorking = true;
                btFinding.setText(R.string.btstop);
                mThread = new Thread(new Runnable() {
                    @Override
                    public void run() {
                        while(mWorking)
                        {
                            ReadTag mtag = Reader.rrlib.FindEPC(ScanMode.epc);
                            if(mtag!=null)
                            {
                                rssi = mtag.rssi;
                                Reader.rrlib.playSound();
                                Message msg = handler.obtainMessage();
                                msg = handler.obtainMessage();
                                msg.what = 0;
                                msg.obj = rssi + "";
                                handler.sendMessage(msg);
                            }
                            else
                            {
                                if(rssi>0)
                                    rssi -=2;
                                if(rssi<0) rssi=0;
                                Message msg = handler.obtainMessage();
                                msg = handler.obtainMessage();
                                msg.what = 0;
                                msg.obj = rssi + "";
                                handler.sendMessage(msg);
                            }
                        }
                    }
                });
                mThread.start();
            }
        }
        else
        {
            if(mThread!=null)
            {
                mWorking=false;
                try {
                    mThread.join();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                mThread=null;
                btFinding.setText(R.string.finding);
            }
        }
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