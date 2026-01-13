package com.UHF.scanlable;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Message;
import android.os.SystemClock;
import android.support.v4.app.ActivityCompat;
import android.view.View;
import android.os.Handler;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.security.InvalidParameterException;
import java.sql.Date;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;

public class FSTActivity extends Activity implements OnClickListener {

    Button selectButton;
    Button TranButton;
    Button ShowButton;
    private ArrayAdapter<String> spada_epc;
    Spinner spepc;
    TextView tvResult;
    byte[]TranData =null;
    Handler handler;
    Thread mThread=null;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_fst);
        initView();
        checkAndRequestPermission();

        handler = new Handler() {
            @Override
            public void handleMessage(Message msg) {
                try{
                    switch (msg.what) {
                        case 0x01:
                            String arg = msg.obj+"";
                            tvResult.setText(arg);
                            break;
                        case 0x02:
                            TranButton.setEnabled(true);
                            ShowButton.setEnabled(true);
                            break;
                        case 0x03:
                            break;
                        case 0x04:
                            break;
                        default:
                            break;
                    }
                }catch(Exception ex)
                {ex.toString();}
            }
        };
    }
    private void initView()
    {
        spepc = (Spinner)findViewById(R.id.fst_spinner);
        tvResult = (TextView)findViewById(R.id.fst_result);



        selectButton = (Button)findViewById(R.id.button_fst_select);
        TranButton = (Button)findViewById(R.id.button_fst_tran);
        ShowButton = (Button)findViewById(R.id.button_fst_show);
        selectButton.setOnClickListener(this);
        TranButton.setOnClickListener(this);
        ShowButton.setOnClickListener(this);
    }

    @SuppressLint("SuspiciousIndentation")
    @Override
    protected void onResume() {
        // TODO Auto-generated method stub
        int epcCount = ScanMode.mlist.size();
        String[]epcdata = new String[epcCount];

        for (int i = 0; i < ScanMode.mlist.size(); i++) {
            String temp = ScanMode.mlist.get(i);
            epcdata[i] = temp;
        }

      //  if(epcCount>0)
        {
            spada_epc = new ArrayAdapter<String>(FSTActivity.this,
                    android.R.layout.simple_spinner_item, epcdata);
            spada_epc.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
            spepc.setAdapter(spada_epc);
            if(epcCount>0)
            spepc.setSelection(0,false);
        }

        super.onResume();
    }

    @Override
    public void onClick(View view) {
        if(view ==selectButton)
        {
            Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
            intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);//关键！多选参数
            intent.setType("text/plain");//指定文件类型
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            startActivityForResult(Intent.createChooser(intent, "选择文件"), 101);
        }
        else if(view == TranButton)
        {
            if(TranData==null || TranData.length!=4736)
            {
                Reader.writelog("没有选择文件",tvResult);
                return;
            }
            if(mThread==null)
            {
                TranButton.setEnabled(false);
                ShowButton.setEnabled(false);
                mThread = new Thread(new Runnable() {
                    @Override
                    public void run() {
                        if(TranImage())
                        {
                            SendMessage("文件传输成功",1);
                        }
                        else
                        {
                            SendMessage("文件传输失败",1);
                        }
                        handler.removeMessages(2);
                        handler.sendEmptyMessage(2);
                        mThread=null;
                    }
                });
                mThread.start();
            }
        }
        else if(view == ShowButton)
        {
            if(mThread==null)
            {
                TranButton.setEnabled(false);
                ShowButton.setEnabled(false);
                String strEPC ="";
                byte[]EPC=null;
                if(spepc.getSelectedItem()!=null)
                    strEPC = spepc.getSelectedItem().toString();
                if(strEPC.length()>0)
                {
                    EPC = Util.hexStringToBytes(strEPC);
                }
                final byte[] finalEPC = EPC;
                mThread = new Thread(new Runnable() {
                    @Override
                    public void run() {
                        SendMessage("等待命令执行",1);
                        byte ENum =0;
                        if(finalEPC!=null)
                            ENum = (byte)(finalEPC.length/2);
                        int result = Reader.rrlib.FST_ShowImage(ENum, finalEPC);
                        if(result==0)
                        {
                            SendMessage("命令执行成功",1);
                        }
                        else
                        {
                            SendMessage("命令执行失败",1);
                        }
                        handler.removeMessages(2);
                        handler.sendEmptyMessage(2);
                        mThread=null;
                    }
                });
                mThread.start();
            }
        }
    }

    private boolean TranImage()
    {
        byte[]data = null;
        byte[]StartAdd = new byte[2];
        boolean success = false;
        for(int m=0;m<23;m++)
        {
            data = new byte[200];
            System.arraycopy(TranData,m*200,data,0,200);
            StartAdd[0] = (byte)((200*m)>>8);
            StartAdd[1] = (byte)((200*m)& 255);
            success=false;
            for(int n=0;n<3;n++)
            {
                int result = Reader.rrlib.FST_TranImage((byte)200,StartAdd,data);
                if(result==0){
                    success = true;
                    String bfb = "文件已传输: "+(m+1)*100/24+"％";
                    SendMessage(bfb,1);
                    break;
                }
            }
            if(!success)
            {
                return false;
            }
        }

        //最后136字节
        success=false;
        StartAdd[0] = (byte)(4600>>8);
        StartAdd[1] = (byte)(4600& 255);
        System.arraycopy(TranData,4600,data,0,136);
        for(int n=0;n<3;n++)
        {
            int result = Reader.rrlib.FST_TranImage((byte)136,StartAdd,data);
            if(result==0){
                success = true;
                String bfb = "文件已传输: "+100+"％";
                SendMessage(bfb,1);
                break;
            }
        }
        return success;
    }
    public  void checkAndRequestPermission() {
        if (Build.VERSION.SDK_INT >= 23) {
            //Manifest.permission.READ_EXTERNAL_STORAGE读取权限
            List<String> lackedPermission = new ArrayList<String>();
            if (!(this.checkSelfPermission(Manifest.permission.READ_EXTERNAL_STORAGE)== PackageManager.PERMISSION_GRANTED)) {
                lackedPermission.add(Manifest.permission.READ_EXTERNAL_STORAGE);
            }

            // 权限都已经有了，那么直接调用SDK
            if (lackedPermission.size() == 0) {
            } else {
                // 请求所缺少的权限，在onRequestPermissionsResult中再看是否获得权限，如果获得权限就可以调用SDK，否则不要调用SDK。
                String[] requestPermissions = new String[lackedPermission.size()];
                lackedPermission.toArray(requestPermissions);
                ActivityCompat.requestPermissions(this, requestPermissions,1);
               // this.requestPermissions(requestPermissions, 102);
            }
        }
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 101 && data != null) {
            String[] split = data.getDataString().split(":");
            if (split != null && split.length >= 2) {
                String p =  split[1];
                File file = new File(p);
                if(file!=null)
                {

                    FileInputStream fis = null;
                    try {
                        InputStreamReader isr = new InputStreamReader(new FileInputStream(file));
                        BufferedReader br = new BufferedReader(isr);
                        String lineTxt = null;
                        String reds="";
                        while ((lineTxt = br.readLine()) != null) { //
                            if (!"".equals(lineTxt)) {
                                reds = lineTxt.split("\\+")[0]; //java 正则表达式
                            }
                        }
                        isr.close();
                        br.close();
                        if(reds.length()>0) {
                            TranData = Util.hexStringToBytes(reds);
                            SendMessage("图片已选择",0x01);
                        }
                    } catch (FileNotFoundException e) {
                        SendMessage("图片选择失败",0x01);
                        e.printStackTrace();
                    } catch (IOException e) {
                        SendMessage("图片选择失败",0x01);
                        e.printStackTrace();
                    }

                }
            }
        }

    }

    private void SendMessage(String msgdata,int mtype)
    {
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("HH:mm:ss");// HH:mm:ss
        Date date = new Date(System.currentTimeMillis());
        String textlog = simpleDateFormat.format(date)+" "+msgdata;
        Message msg = handler.obtainMessage();
        msg.what = mtype;
        msg.obj = textlog;
        handler.sendMessage(msg);
    }
    /** 申请结果
     * @param requestCode
     * @param permissions
     * @param grantResults
     */
    @Override
    public void onRequestPermissionsResult(int requestCode,  String[] permissions,  int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        switch (requestCode){
            case 102:
                if (grantResults.length>0){
                    List<String> deniedPermissions = new ArrayList<>();
                    List<String> grantedPermissions = new ArrayList<>();
                    for (int i = 0; i < grantResults.length; i++) {
                        int grantResult = grantResults[i];
                        if (grantResult != PackageManager.PERMISSION_GRANTED){
                            String permission = permissions[i];
                            deniedPermissions.add(permission);
                        }else{
                            String permission = permissions[i];
                            grantedPermissions.add(permission);
                        }
                    }
                    if (deniedPermissions.isEmpty()){


                    }else{

                    }
                }
                break;
        }
    }
}
