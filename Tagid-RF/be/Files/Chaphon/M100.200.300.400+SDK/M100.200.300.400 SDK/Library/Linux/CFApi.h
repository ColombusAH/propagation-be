#ifndef _CFAPI_H_
#define _CFAPI_H_

#include <stdint.h>
#include <stdio.h>
#include <wchar.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <strings.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <errno.h>       
#include <dirent.h>       
#include <time.h>         
#include <semaphore.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <iostream>
#include <sstream>
#include <vector>
#include <time.h>
#include <termios.h>
#include <signal.h>
#include <pthread.h>
#include <assert.h>

struct PARA
{
	unsigned char RFIDPRO;
	unsigned short STRATFREI;
	unsigned short STRATFRED;
	unsigned short STEPFRE;
	unsigned char CN;
	unsigned char POWER;
	unsigned char ANTENNA;
	unsigned char REGION;
	unsigned char RESERVED;
};

typedef struct
{
	unsigned char firmVersion[32];
	unsigned char hardVersion[32];
	unsigned char SN[12];
	unsigned char PARAS[12];
}DeviceInfo;

typedef struct
{
	unsigned char DevicehardVersion[32];
	unsigned char DevicefirmVersion[32];
	unsigned char DeviceSN[12];
	unsigned char hardVersion[32];
	unsigned char firmVersion[32];
	unsigned char SN[12];
}DeviceFullInfo;

typedef struct
{
	unsigned char DEVICEARRD;
	unsigned char RFIDPRO;
	unsigned char WORKMODE;
	unsigned char INTERFACE;
	unsigned char BAUDRATE;
	unsigned char WGSET;
	unsigned char ANT;
	unsigned char REGION;
	unsigned char STRATFREI[2];
	unsigned char STRATFRED[2];
	unsigned char STEPFRE[2];
	unsigned char CN;
	unsigned char RFIDPOWER;
	unsigned char INVENTORYAREA;
	unsigned char QVALUE;
	unsigned char SESSION;
	unsigned char ACSADDR;
	unsigned char ACSDATALEN;
	unsigned char FILTERTIME;
	unsigned char TRIGGLETIME;
	unsigned char BUZZERTIME;
	unsigned char INTENERLTIME;
}DevicePara;

typedef struct
{
	unsigned char CodeEn;
	unsigned char Code[4];
	unsigned char MaskEn;
	unsigned char StartAdd;
	unsigned char MaskLen;
	unsigned char MaskData[12];
	unsigned char MaskCondition;
}PermissonPara;

typedef struct
{
	unsigned char CodeEn;
	unsigned char Code[4];
	unsigned char MaskEn;
	unsigned char StartAdd;
	unsigned char MaskLen;
	unsigned char MaskData[31];
	unsigned char MaskCondition;
}LongPermissonPara;

typedef struct
{
	unsigned char KCEn;
	unsigned char RelayTime;
	unsigned char KCPowerEn;
	unsigned char TriggleMode;
	unsigned char BufferEn;
	unsigned char ProtocolEn;
	unsigned char ProtocolType;
	unsigned char ProtocolFormat[10];
}GpioPara;

typedef struct
{
	short BasciRssi;
	unsigned char  AntDelta[16];
}RssiPara;

typedef struct
{
	unsigned char wifiEn;
	unsigned char SSID[32];
	unsigned char PASSWORD[64];
	unsigned char IP[4];
	unsigned char PORT[2];
}WiFiPara;

typedef struct
{
	unsigned char IP[4];
	unsigned char MAC[6];
	unsigned char PORT[2];
	unsigned char NetMask[4];
	unsigned char Gateway[4];
}NetInfo;

typedef struct
{
	unsigned char Enable;
	unsigned char IP[4];
	unsigned char PORT[2];
	unsigned char HeartTime;
}RemoteNetInfo;

typedef struct
{
	unsigned char region;
	unsigned short StartFreq;
	unsigned short StopFreq;
	unsigned short StepFreq;
	unsigned char cnt;
}FreqInfo;

typedef struct
{
	unsigned short addr;
	unsigned char  val;
}RFIcRegs;

typedef struct
{
	unsigned char tc;
	unsigned char blf;
	unsigned char miller;
	unsigned char trext;
	unsigned char modu;
}GBRFParam;

typedef struct
{
	unsigned char target;
	unsigned char action;
	unsigned char memBank;
	unsigned short maskPtr;
	unsigned char maskLen;
	unsigned char maskData[255];
}GBSortParam;

typedef struct
{
	unsigned char condition;
	unsigned char session;
	unsigned char target;
}QueryParam;

typedef struct
{
	unsigned short NO;
	short rssi;
	unsigned char antenna;
	unsigned char channel;
	unsigned char crc[2];
	unsigned char pc[2];
	unsigned char codeLen;
	unsigned char code[255];
}TagInfo;

typedef struct
{
	unsigned char tagStatus;
	unsigned char antenna;
	unsigned char crc[2];
	unsigned char pc[2];
	unsigned char codeLen;
	unsigned char code[255];
}TagResp;

typedef struct
{
	float tari;
	float rtcal;
	float trcal;
	unsigned char dr;
	unsigned char miller;
	unsigned char trext;
	unsigned char modu;
}ISORFParam;

typedef struct
{
	unsigned char resv;
	unsigned char trucate;
	unsigned char target;
	unsigned char action;
	unsigned char membank;
	unsigned short ptr;
	unsigned char len;
	unsigned char mask[240];
}ISOSelectParam;

typedef struct
{
	unsigned char sel;
	unsigned char session;
	unsigned char target;
}ISOQueryParam;

typedef struct
{
	unsigned char readlock;
	unsigned char membank;
	unsigned short blockPtr;
	unsigned char blockRange;
	unsigned char mask[247];
}ISOPermalockParam;

typedef struct
{
	unsigned long blf;
	unsigned char miller;
	unsigned char trext;
	unsigned short rxDelay;
	unsigned short rxLen;
	unsigned long rxNum;
	unsigned char autoMode;
}CP_Sensi_Prm_Typ;

typedef struct
{
	unsigned long frame_err;
	unsigned long frame_total;
	unsigned long blf;
	unsigned char miller;
	unsigned char trext;
	unsigned char freqOffset;
}CP_Sensi_Result_Typ;

typedef struct
{
	unsigned char i_start;
	unsigned char i_stop;
	unsigned char q_start;
	unsigned char q_stop;
}IQ_Axial_Typ;

typedef struct
{
	unsigned char i_origin;
	unsigned char q_origin;
	unsigned char size;
	unsigned char step;
}JSC_AUTO_SCAN_PRM_Typ;

typedef struct
{
	unsigned char number;
	unsigned char dataLen;
	unsigned char data[253];
}JSC_Data_Typ;

typedef struct
{
	unsigned char option;
	unsigned short addr;
	unsigned short val;
	unsigned short interval;
}Read_Write_Reg_Cmd_Item_Typ;

typedef struct
{
	unsigned char items;
	unsigned short regs;
	unsigned short val[126];
}Read_Regs_Result_Typ;

typedef struct
{
	unsigned char status;
	unsigned long time;
}Int_Status_Item_Typ;

typedef struct
{
	unsigned short addr;
	unsigned char value;
	unsigned long time;
}CR_Log_Item_Typ;

typedef struct
{
	unsigned char target;
	unsigned char trucate;
	unsigned char action;
	unsigned char membank;
	unsigned short m_ptr;
	unsigned char len;
	unsigned char mask[31];
}SelectSortParam;

typedef struct
{
	unsigned char Enable;
	unsigned char AntPower[8];
}AntPower;

typedef struct {
	unsigned char Mode;
	unsigned char GPIEnable;
	unsigned char InLevel;
	unsigned char GPOEnable;
	unsigned char PutLevel;
	unsigned char PutTime[8];
}GPIOWorkParam;

typedef struct {
	unsigned char GateMode;
	unsigned char GateGPI1;
	unsigned char GateGPI2;
	unsigned char GatePower;
	unsigned char GateRead;
	unsigned char EASMode;
	unsigned char EASGPO;
}GateWorkParam;

typedef struct {
	unsigned char DIR;
	unsigned char GPI;
	unsigned char SYSTIME[4];
}GateParam;

typedef struct {
	unsigned char Addr;
	unsigned char Len;
	unsigned char Data[32];
}EASMask;

typedef struct {
	unsigned char Enable;
	unsigned char Time;
	unsigned char Len;
	unsigned char Data[32];
}Heartbeat;

typedef struct {
	unsigned char STATE;
	unsigned short CUSTOMERCOUNT;
}AccessInfo;

typedef struct {
	unsigned char STATUS;
	unsigned short FRAMENUM;
	unsigned char INFOCOUNT;
	unsigned char WHITELIST[4096];
}WhiteList;

typedef struct {
	unsigned char LISTENABLE;
	unsigned char READGPIFUNC;
	unsigned char FRONTGPIFUNC;
	unsigned char BACKGPIFUNC;
	unsigned char BUTTONGPIFUNC;
	unsigned char RECVGPIEXEFUNC[4];
	unsigned char ACCESSCTRLEXEPART;
	unsigned char RECVACTIONEXEPART[7];
}AccessOperateParam;

//========================动态库对外错误码=================================
#define STAT_OK								0x00000000
#define STAT_PORT_HANDLE_ERR				0xFFFFFF01    // 句柄错误，或者输入的串口参数错误 Handle error or input serial port parameter error
#define STAT_PORT_OPEN_FAILED				0xFFFFFF02	  // 打开串口失败 Failed to open serial port
#define STAT_DLL_INNER_FAILED				0xFFFFFF03    // 动态库内部错误 Internal error in dynamic library
#define STAT_CMD_PARAM_ERR					0xFFFFFF04    // 参数值错误或越界，或者模块不支持该参数值 The parameter value is incorrect or out of range, or the module does not support the parameter value
#define STAT_CMD_SERIAL_NUM_EXIT			0xFFFFFF05    // 序列号已存在 Serial number already exists
#define STAT_CMD_INNER_ERR					0xFFFFFF06    // 由于模块内部错误导致命令执行失败 Command execution failed due to internal module error
#define STAT_CMD_INVENTORY_STOP				0xFFFFFF07    // 没有盘点到标签或盘点已结束 Inventory not found on label or completed
#define STAT_CMD_TAG_NO_RESP				0xFFFFFF08    // 标签响应超时 Label response timeout
#define STAT_CMD_DECODE_TAG_DATA_FAIL		0xFFFFFF09    // 解调标签数据错误 Demodulation label data error
#define STAT_CMD_CODE_OVERFLOW				0xFFFFFF0A    // 标签数据超出串口最大传输长度 Label data exceeds the maximum transmission length of the serial port
#define STAT_CMD_AUTH_FAIL					0xFFFFFF0B    // 认证失败 Authentication failed
#define STAT_CMD_PWD_ERR					0xFFFFFF0C    // 口令错误 password error
#define STAT_CMD_SAM_NO_RESP				0xFFFFFF0D    // SAM卡无响应 SAM card not responding
#define STAT_CMD_SAM_CMD_FAIL				0xFFFFFF0E    // PSAM卡命令执行失败 PSAM card command execution failed
#define STAT_CMD_RESP_FORMAT_ERR			0xFFFFFF0F    // 读写器响应格式错误 Reader/writer response format error
#define STAT_CMD_HAS_MORE_DATA				0xFFFFFF10    // 命令执行成功，但是还有后续数据未传输完成 The command execution was successful, but there are still subsequent data transfers that have not been completed
#define STAT_CMD_BUF_OVERFLOW				0xFFFFFF11    // 传入缓存太小，数据溢出 Incoming cache too small, data overflow
#define STAT_CMD_COMM_TIMEOUT				0xFFFFFF12    // 等待阅读器响应超时 Timed out waiting for reader response
#define STAT_CMD_COMM_WR_FAILED				0xFFFFFF13    // 向串口写数据失败 Failed to write data to the serial port
#define STAT_CMD_COMM_RD_FAILED				0xFFFFFF14    // 读串口数据失败 Failed to read serial port data
#define STAT_CMD_NOMORE_DATA				0xFFFFFF15    // 没有更多数据 No more data available
#define STAT_DLL_UNCONNECT       			0xFFFFFF16    // 网络连接尚未建立 The network connection has not been established yet
#define STAT_DLL_DISCONNECT       			0xFFFFFF17    // 网络已经断开 The network has been disconnected
#define STAT_CMD_RESP_CRC_ERR				0xFFFFFF18    // 读写器响应CRC校验错误 Reader/writer response CRC verification error
#define STAT_CMD_IAP_CRC_ERR				0xFFFFFF21    // 下载程序CRC校验错误 Download program CRC verification error
#define STAT_CMD_DOWMLOAD_ERR				0xFFFFFF22    // 下载数据错误 Download data error
#define STAT_CMD_DOWM_NONE_ERR				0xFFFFFF23    // 用户区下载未完成 User area download incomplete

//========================标签状态码================================= 
#define STAT_GB_TAG_LOW_POWER				0xFFFFFF40    // 标签供电不足, 标签没有足够的能量完成操作 Insufficient power supply to the tag, the tag does not have enough energy to complete the operation
#define STAT_GB_TAG_OPR_LIMIT				0xFFFFFF41    // 标签操作权限不足,未授权的访问 Insufficient permission for label operation, unauthorized access
#define STAT_GB_TAG_MEM_OVF					0xFFFFFF42    // 标签操作存储区溢出,或目标存储区不存在 Label operation storage area overflow, or target storage area does not exist
#define STAT_GB_TAG_MEM_LCK					0xFFFFFF43    // 标签存储区锁定,对被锁定为不可写的存储区进行写操作或者擦除操作，对被锁定为不可读的存储区进行读操作 Label storage area locking, performing write or erase operations on storage areas that are locked as non writable, and reading operations on storage areas that are locked as unreadable
#define STAT_GB_TAG_PWD_ERR					0xFFFFFF44    // 标签操作口令错误,访问命令口令错误 标签操作口令错误,访问命令口令错误
#define STAT_GB_TAG_AUTH_FAIL				0xFFFFFF45    // 标签鉴别失败,未通过鉴别 Label authentication failed, failed authentication
#define STAT_GB_TAG_UNKNW_ERR				0xFFFFFF46    // 标签操作未知错误,发生不能确定的错误 Unknown error in label operation, an undetermined error occurred
#define STAT_ISO_TAG_OTHER_ERR				0xFFFFFF50    // 其他错误 Other errors
#define STAT_ISO_TAG_NOT_SUPPORT			0xFFFFFF51    // 标签不支持该参数 The tag does not support this parameter
#define STAT_ISO_TAG_OPR_LIMIT				0xFFFFFF52    // 权限不足 Insufficient permissions
#define STAT_ISO_TAG_MEM_OVF				0xFFFFFF53    // 存储区溢出 Storage Area Overflow
#define STAT_ISO_TAG_MEM_LCK				0xFFFFFF54    // 存储区锁定 Store Lock
#define STAT_ISO_TAG_CRYPTO_ERR				0xFFFFFF55    // 标签加密套件错误 Label encryption kit error
#define STAT_ISO_TAG_NOT_ENCAP				0xFFFFFF56    // 空口命令未封装 Empty command not encapsulated
#define STAT_ISO_TAG_RESP_OVF				0xFFFFFF57    // 标签响应缓存溢出 Label response cache overflow
#define STAT_ISO_TAG_SEC_TIMEOUT			0xFFFFFF58    // 标签处于安全超时状态 The label is in a security timeout state
#define STAT_ISO_TAG_LOW_POWER				0xFFFFFF59    // 供电不足 Insufficient power supply
#define STAT_ISO_TAG_UNKNW_ERR				0xFFFFFF5A    // 标签响应未知错误 Label response unknown error
#define STAT_ISO_TAG_SENSOR_CFG				0xFFFFFF5B    // 传感器定时任务配置超出上限 Sensor timed task configuration exceeds upper limit
#define STAT_ISO_TAG_TAG_BUSY				0xFFFFFF5C    // 标签繁忙 Label busy
#define STAT_ISO_TAG_MEASU_NOT_SUPPORT		0xFFFFFF5D    // 传感器不支持该测量类型 The sensor does not support this measurement type

#define	DEF_READ_TIMEOUT					50
#define	DEF_WRITE_TIMEOUT					1000
#define COMMON_TIMEOUT						2000
#define SPECIAL_TIMEOUT						300
#define TIMEOUT_1500						1500
#define TIMEOUT_2000						2000
#define TIMEOUT_4000						4000
#define TIMEOUT_5000						5000
#define TIMEOUT_10000						10000
#define READER_INIT							0x0050
#define GET_INFO							0x0051
#define REBOOT								0x0052
#define SET_PWR								0x0053
#define GET_PWR								0x0054
#define SET_FRE								0x0055
#define GET_FRE								0x0056
#define SET_ANTENNA							0x0057
#define GET_ANTENNA							0x0058
#define SET_GET_RFID_TYPE					0x0059
#define SET_GET_BAUD						0x005A
#define SET_GET_BUZZER						0x005B
#define SET_GET_ADDR						0x005C
#define SET_INFO							0x005D
#define ANT_AUTOSCAN						0x005E
#define SET_GET_NET							0x005F
#define TEMPERATURE_SET						0x0060
#define TEMPERATURE_GET						0x0061
#define SET_GET_POWER_DELTA					0x0062
#define SET_GET_ANT_POWER					0x0063
#define SET_GET_REMOTE_NETPARA				0x0064
#define GET_DEVIDE_INFO						0x0070
#define SET_DEVIDE_ALLPARAM					0x0071
#define GET_DEVICE_ALLPARAM					0x0072
#define SET_SET_PERMISSION_PARAM			0x0073
#define GET_SET_GPIO_PARAM					0x0074
#define SET_SET_WIFI_PARAM					0x0075
#define SET_SET_PERMISSION_PARAM_L			0x0076
#define RELEASE_CLOSE_RELAY     			0x0077
#define SET_GET_RSSI_FILTER     			0x0079
#define ISO_INVENTORY_CONTINUE				0x0001
#define ISO_INVENTORY_STOP					0x0002
#define ISO_READ_TAG						0x0003
#define ISO_WRITE_TAG						0x0004
#define ISO_LOCK_TAG						0x0005
#define ISO_KILL_TAG						0x0006
#define ISO_SET_SELECTMASK					0x0007
#define ISO_SET_COIL_PARAM					0x0008
#define ISO_GET_COIL_PARAM					0x0009
#define MULTI_SET_SORT						0x0010
#define MULTI_GET_SORT						0x0011
#define MULTI_SET_QUERY						0x0012
#define MULTI_GET_QUERY						0x0013
#define JUMP2_BOOTER						0x1000
#define IAP_INIT 							0x1001
#define IAP_ERASE_USER 						0x1002
#define IAP_WRITE_USER 						0x1003
#define IAP_CHECK_CRC 						0x1004
#define IAP_DOWNLOAD_VERIFY 				0x1005
#define IAP_JUMP2USER						0x1006
#define IAP_CHIP_ENBABLE					0x1007
#define HUB_LOOP_TEST  						0x1101
#define HUB_SET_GET_PORT 					0x1102
#define GET_EXCEP							0x0002
#define SET_GET_MODU						0x000A
#define SAVE_SETTING						0x000E
#define RESTORE_SETTING						0x000F
#define SLEEPTIME_SET						0x0019
#define SLEEPTIME_GET						0x001A
#define NETWORKINFO_SET						0x001B
#define NETWORKINFO_GET						0x001C
#define DUTY_SET							0x0010
#define DUTY_GET							0x0011
#define UPDATE								0x0012
#define GET_SET_HEARTBEAT					0x0030
#define GB_SET_RF_PRM						0x0031
#define GB_GET_RF_PRM						0x0032
#define GB_SET_SORT_PARAM					0x0033
#define GB_GET_SORT_PARAM					0x0034
#define GB_SET_QUERY_PARAM					0x0035
#define GB_GET_QUERY_PARAM					0x0036
#define GB_SET_COIL_PARAM					0x0037
#define GB_GET_COIL_PARAM					0x0038
#define GB_SET_AUTH_PARAM					0x0039
#define GB_GET_AUTH_PARAM					0x003A
#define GB_SAVE_SETTING						0x003B
#define GB_INVENTORY_CONTINUE				0x003C
#define GB_INVENTORY_STOP					0x003D
#define GB_READ_TAG							0x003E
#define GB_WRITE_TAG						0x003F
#define GB_ERASE_TAG						0x0040
#define GB_LOCK_TAG							0x0041
#define GB_KILL_TAG							0x0042
#define GB_STAG_GET_SPRM					0x0046
#define GB_STAG_MSAUTH						0x0047
#define GB_TEST_TRANS						0x004A
#define GB_SET_SORTMASK						0x004B
#define ISO_SET_RF_PRM						0x0051
#define ISO_GET_RF_PRM						0x0052
#define ISO_SET_SEL_PRM						0x0053
#define ISO_GET_SEL_PRM						0x0054
#define ISO_SET_QUERY_PARAM					0x0055
#define ISO_GET_QUERY_PARAM					0x0056
#define ISO_SET_AUTH_PARAM					0x0059
#define ISO_GET_AUTH_PARAM					0x005A
#define ISO_SAVE_SETTING					0x005B
#define ISO_BLOCKWRITE_TAG					0x0062
#define ISO_BLOCKERASE_TAG					0x0063
#define ISO_BLOCK_PERMALOCK					0x0064
#define ISO_STAG_GET_SPRM					0x0067
#define ISO_STAG_MSAUTH						0x0068
#define GET_GPIO_WORKPARAM					0x0080
#define GET_GPIO_LEVELS 					0x0081
#define GET_GPI_STATUS 						0x0082
#define GET_GATE_WORKPARAM 					0x0083
#define GET_EAS_MASK						0x0084
#define GET_SET_ACCESS_OPART_PARAM			0x0089
#define GET_ACCESSINFO						0x008A
#define BEGIN_WHITELIST						0x008B
#define GET_SET_WHITELIST					0x008C
#define END_WHITELIST						0x008D
#define ISO_TEST_TRANS						0x006A
#define MULTI_SET_RF_PRM					0x0083
#define MULTI_GET_RF_PRM					0x0084
#define CP_INIT								0x00C1
#define CP_EPC_SENS_TEST					0x00C2
#define CP_GB_SENS_TEST						0x00C3
#define CP_GJB_SENS_TEST					0x00C4
#define CP_EPC_QUERY_TEST					0x00C5
#define CP_GB_QUERY_TEST					0x00C6
#define CP_GJB_QUERY_TEST					0x00C7
#define CP_MANU_SJC_TEST					0x00C8
#define CP_AUTO_SJC_TEST					0x00C9
#define TEST_ENTER_SHELL					0x00D1
#define TEST_BATCH_RDWR_REGS				0x00D2
#define TEST_SET_WATCH_CR					0x00D3
#define TEST_SWITCH_WATCH_CR				0x00D4
#define TEST_READ_CR_STATUS					0x00D5
#define TEST_SET_WATCH_INT					0x00D6
#define TEST_SWITCH_WATCH_INT				0x00D7
#define TEST_READ_INT_STATUS				0x00D8
#define TEST_SET_WATCH_FIFO					0x00D9
#define TEST_SWITCH_WATCH_FIFO				0x00DA
#define TEST_READ_FIFO						0x00DB
#define TEST_SET_LOG_LEN					0x00DC
#define TEST_READ_LOG						0x00DD
#define TEST_SWITCH_SELECT					0x00DE
#define TEST_SEND_CONTINUEDATA				0x00DF
#define TEST_TEST1							0x00E1
#define TEST_TEST2							0x00E2
#define TEST_TXPOWER						0x00E3
#define TEST_SJC							0x00E4
#define TEST_FREQCFG						0x00E5
#define TEST_BLPOWER						0x00E6
#define TEST_SENSITIVITY					0x00E7
#define TEST_RFPOWER						0x00E8
#define SET_SORT_PARAM						0x0008
#define GET_SORT_PARAM						0x0009
#define SET_QUERY_PARAM						0x000A
#define GET_QUERY_PARAM						0x000B
#define SET_AUTH_PARAM						0x000C
#define GET_AUTH_PARAM						0x000D
#define SAVE_PARAMS							0x000E
#define RESTORE_DEFAULT_PARAM				0x000F
#define EN_DIS_PWR							0x0011
#define INVENTORY_CONTINUE					0x0012
#define INVENTORY_STOP						0x0013
#define SET_PSAM_INTERFACE					0x0031
#define PSAM_POWER_DOWN						0x0032
#define PSAM_RESET							0x0033
#define PSAM_COMMAND						0x0034
#define GET_PSAM_INTERFACE					0x0035
#define TEST_SET_WORK_MODE					0x00F1
#define TEST_SET_RF_REG						0x00F2
#define TEST_GET_RF_REG						0x00F3
#define TEST_QUERY_TAG						0x00F4
#define TEST_TRANS							0x00F5
#define TEST_CONTINUE_TRANS					0x00F6
#define TEST_DEBUG_PRINT					0x00F7
#define TEST_GET_SPARAM						0x00F8
#define TEST_SET_WORK_MODE_PWD				0x00F9
#define TEST_SET_SNO						0x00FA
#define TEST_QUERY_ACK						0x00FC
#define R_RES_OK							0x00
#define R_RES_PARAM_ERR						0x01
#define R_RES_OPR_ERR						0x02
#define R_RES_SERIAL_NUM_ERR				0x03
#define R_RES_INVENT_END					0x12
#define R_RES_TAG_NO_RESP					0x14
#define R_RES_TAG_CRC_ERR					0x15
#define R_RES_AUTH_FAILED				    0x16
#define R_RES_TAG_PWD_ERR				    0x17
#define R_RES_SAM_NO_RESP					0x21
#define R_RES_SAM_OPRT_ERR					0x22
#define R_RES_NOMORE_DATA					0xFF
#define T_GB_RES_LOW_POWER					0x83
#define T_GB_RES_OPR_LIMIT					0x81
#define T_GB_RES_MEM_OVF					0x82
#define T_GB_RES_MEM_LCK					0x85
#define T_GB_RES_PWD_ERR					0x86
#define T_GB_RES_AUTH_FAIL					0x87
#define T_GB_RES_UNKNW_ERR					0x88
#define T_ISO_RES_OTHER_ERR					0x00
#define T_ISO_RES_NOT_SUPPORT				0x01
#define T_ISO_RES_OPR_LIMIT					0x02
#define T_ISO_RES_MEM_OVF					0x03
#define T_ISO_RES_MEM_LCK					0x04
#define T_ISO_RES_CRYPTO_ERR				0x05
#define T_ISO_RES_NOT_ENCAP					0x06
#define T_ISO_RES_RESP_OVF					0x07
#define T_ISO_RES_SEC_TIMEOUT				0x08
#define T_ISO_RES_LOW_POWER					0x0B
#define T_ISO_RES_UNKNW_ERR					0x88
#define T_ISO_RES_SENSOR_CFG				0x81
#define T_ISO_RES_TAG_BUSY					0x82
#define T_ISO_RES_MEASU_NOT_SUPPORT			0x83
#define HEAD_BYTE					        0xCF
#define DEVICE_ADDR					        0xFF
#define RSP_PKT_INDEX_LEN					0x04    
#define RSP_PKT_INDEX_STATUS				0x05
#define RSP_PKT_INDEX_PAYLOAD				0x06
#define TYPE_SET							0x01
#define TYPE_GET							0x02
#define MSB3(a)								((unsigned char)((a)>>24))
#define MSB2(a)								((unsigned char)((a)>>16))
#define MSB(a)								((unsigned char)((a)>>8))
#define LSB(a)								((unsigned char)(a))
#define U16(msb,lsb)						(((unsigned short)(msb)<<8) +lsb)
#define U32(msb3,msb2,msb,lsb)				(((unsigned long)(msb3)<<24)+((unsigned long)(msb2)<<16)+((unsigned short)(msb)<<8)+lsb)
#define DATA_TYPE_SHOW_CMD					0x00
#define DATA_TYPE_SHOW_RSP					0x01
#define PRESET_VALUE						0xFFFF
#define POLYNOMIAL							0x8408
#define INVALID_HANDLE_VALUE				-1

#ifdef __cplusplus
extern "C" {
#endif

	/// <summary>
	/// Connect serial port
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="ComPort"></param>
	/// <param name="Baudrate"></param>
	/// <returns></returns>
	int OpenDevice(int64_t* hComm, char* pcCom, int iBaudRate);
	/// <summary>
	/// Connection network port
	/// </summary>
	/// <param name="hComm">The handle of the return type is used for the following interface to pass parameters</param>
	/// <param name="strIP">ip</param>
	/// <param name="wPort">prot</param>
	/// <param name="timeoutMs">waiting time</param>
	/// <returns></returns>
	int OpenNetConnection(int64_t* hComm, char* strIP, unsigned short wPort, long timeoutMs);
	/// <summary>
	/// Close reader connection
	/// </summary>
	/// <param name="hComm"></param>
	/// <returns>0x00 Success</returns>
	int CloseDevice(int64_t hComm);
	/// <summary>
	/// Obtain USB quantity
	/// </summary>
	/// <param name=""></param>
	/// <returns></returns>
	int CFHid_GetUsbCount();
	/// <summary>
	/// Obtain USB information
	/// </summary>
	/// <param name="index"></param>
	/// <param name="pucDeviceInfo"></param>
	/// <returns></returns>
	int CFHid_GetUsbInfo(unsigned short index, char* pucDeviceInfo);
	/// <summary>
	/// usb connection
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="index"></param>
	/// <returns></returns>
	int OpenHidConnection(int64_t* hComm, unsigned short index);
	/// <summary>
	/// Command to obtain reader/writer module information
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="devInfo"></param>
	/// <returns></returns>
	int GetInfo(int64_t hComm, DeviceInfo* devInfo);
	/// <summary>
	/// Command to obtain the information of the reader/writer integrated machine
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="devInfo">Reader information for return type</param>
	/// <returns>0x00 success</returns>
	int GetDeviceInfo(int64_t hComm, DeviceFullInfo* devInfo);
	/// <summary>
	/// Command to obtain device parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="devInfo">Device parameters of return type</param>
	/// <returns>0x00 success</returns>
	int GetDevicePara(int64_t hComm, DevicePara* devInfo);
	/// <summary>
	/// Set Device Parameter Command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="devInfo">Equipment parameters</param>
	/// <returns>0x00 success</returns>
	int SetDevicePara(int64_t hComm, DevicePara devInfo);
	/// <summary>
	/// Set Device Parameter Command By Java
	/// </summary>
	/// <param name="hComm"></param>
	/// <returns>0x00 success</returns>
	int SetDevicePara_J(int64_t hComm, unsigned char DEVICEARRD, unsigned char RFIDPRO, unsigned char WORKMODE, unsigned char INTERFACE, unsigned char BAUDRATE, unsigned char WGSET, unsigned char ANT, unsigned char REGION, unsigned char STRATFREI1, unsigned char STRATFREI2,
		unsigned char STRATFRED1, unsigned char STRATFRED2, unsigned char STEPFRE1, unsigned char STEPFRE2, unsigned char CN, unsigned char RFIDPOWER, unsigned char INVENTORYAREA, unsigned char QVALUE, unsigned char SESSION, unsigned char ACSADDR, unsigned char ACSDATALEN, unsigned char FILTERTIME,
		unsigned char TRIGGLETIME, unsigned char BUZZERTIME, unsigned char INTENERLTIME);
	/// <summary>
	/// Obtain card reading permission parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="PermissonPara">LongPermission of return type</param>
	/// <returns>0x00 success</returns>
	int GetLongPermissonPara(int64_t hComm, LongPermissonPara* PermissonPara);
	/// <summary>
	/// Set card reading permission parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="PermissonPara">LongPermisson</param>
	/// <returns>0x00 success</returns>
	int SetLongPermissonPara(int64_t hComm, LongPermissonPara PermissonPara);
	/// <summary>
	/// Obtain card reading permission parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="PermissonPara">Permission of return type</param>
	/// <returns>0x00 success</returns>
	int GetPermissonPara(int64_t hComm, PermissonPara* PermissonPara);
	/// <summary>
	/// Set card reading permission parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="PermissonPara">Permisson</param>
	/// <returns>0x00 success</returns>
	int SetPermissonPara(int64_t hComm, PermissonPara PermissonPara);
	/// <summary>
	/// Obtain input and output parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="GpioPara">Gpio of return type</param>
	/// <returns>0x00 success</returns>
	int GetGpioPara(int64_t hComm, GpioPara* GpioPara);
	/// <summary>
	/// Set input and output parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="GpioPara">Gpio</param>
	/// <returns>0x00 success</returns>
	int SetGpioPara(int64_t hComm, GpioPara GpioPara);
	/// <summary>
	/// Obtain remote network parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="type">Net of return type</param>
	/// <returns>0x00 success</returns>
	int GetNetInfo(int64_t hComm, NetInfo* type);
	/// <summary>
	/// Set remote network parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="type">Net</param>
	/// <returns>0x00 success</returns>
	int SetNetInfo(int64_t hComm, NetInfo type);
	/// <summary>
	/// Obtain power command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="power">RFPower of return type</param>
	/// <param name="reserved"></param>
	/// <returns>0x00 success</returns>
	int GetRFPower(int64_t hComm, unsigned char* power, unsigned char* reserved);
	/// <summary>
	/// Set power command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="power"></param>
	/// <param name="reserved"></param>
	/// <returns></returns>
	int SetRFPower(int64_t hComm, unsigned char power, unsigned char reserved);
	/// <summary>
	/// Obtain operating frequency command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="freqInfo"></param>
	/// <returns></returns>
	int GetFreq(int64_t hComm, FreqInfo* freqInfo);
	/// <summary>
	/// Set operating frequency command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="freqInfo"></param>
	/// <returns></returns>
	int SetFreq(int64_t hComm, const FreqInfo* freqInfo);
	/// <summary>
	/// Obtain antenna configuration commands
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="antenna">Antenna of return type</param>
	/// <returns>0x00 success</returns>
	int GetAntenna(int64_t hComm, unsigned char* antenna);
	/// <summary>
	/// Set antenna configuration command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="antenna">Antenna</param>
	/// <returns>0x00 success</returns>
	int SetAntenna(int64_t hComm, unsigned char* antenna);
	/// <summary>
	/// Obtain WIFI
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="WiFiPara"></param>
	/// <returns></returns>
	int GetwifiPara(int64_t hComm, WiFiPara* WiFiPara);
	/// <summary>
	/// Set up WIFI
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="WiFiPara"></param>
	/// <returns></returns>
	int SetwifiPara(int64_t hComm, WiFiPara WiFiPara);
	/// <summary>
	/// Get Protocol Type Command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="type"></param>
	/// <returns></returns>
	int GetRFIDType(int64_t hComm, unsigned char* type);
	/// <summary>
	/// Set Protocol Type Command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="type"></param>
	/// <returns></returns>
	int SetRFIDType(int64_t hComm, unsigned char type);
	/// <summary>
	/// Obtain remote network parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="type"></param>
	/// <returns></returns>
	int GetRemoteNetInfo(int64_t hComm, RemoteNetInfo* type);
	/// <summary>
	/// Set remote network parameters
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="type"></param>
	/// <returns></returns>
	int SetRemoteNetInfo(int64_t hComm, RemoteNetInfo type);
	/// <summary>
	/// Get temperature threshold command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="pTempCur"></param>
	/// <param name="pTempLimit"></param>
	/// <returns></returns>
	int GetTemperature(int64_t hComm, unsigned char* pTempCur, unsigned char* pTempLimit);
	/// <summary>
	/// Set temperature threshold command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="tempLimit"></param>
	/// <param name="resv"></param>
	/// <returns></returns>
	int SetTemperature(int64_t hComm, unsigned char tempLimit, unsigned char resv);
	/// <summary>
	/// Device Factory reset Command
	/// </summary>
	/// <param name="hComm"></param>
	/// <returns>0x00 success</returns>
	int RebootDevice(int64_t hComm);
	/// <summary>
	/// Set relay release
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="time"></param>
	/// <returns></returns>
	int Release_Relay(int64_t hComm, unsigned char time);
	/// <summary>
	/// Set relay closure
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="time"></param>
	/// <returns></returns>
	int Close_Relay(int64_t hComm, unsigned char time);
	/// <summary>
	/// Inquiry command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="btInvCount"></param>
	/// <param name="dwInvParam"></param>
	/// <returns>0x00 success</returns>
	int InventoryContinue(int64_t hComm, unsigned char btInvCount, unsigned long dwInvParam);
	/// <summary>
	/// Obtain label information and return it in TagInfo format
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="tag_info">TagInfo of return type</param>
	/// <param name="timeout">waiting time</param>
	/// <returns>0x00 success</returns>
	int GetTagUii(int64_t hComm, TagInfo* tag_info, unsigned short timeout);
	/// <summary>
	/// Stop Inventory
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="timeout">waiting time</param>
	/// <returns>0x00 success</returns>
	int InventoryStop(int64_t hComm, unsigned short timeout);
	/// <summary>
	/// Read Data Command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="option"></param>
	/// <param name="accPwd"></param>
	/// <param name="memBank"></param>
	/// <param name="wordPtr"></param>
	/// <param name="wordCount"></param>
	/// <returns></returns>
	int ReadTag(int64_t hComm, unsigned char option, unsigned char* accPwd, unsigned char memBank, unsigned short wordPtr, unsigned char wordCount);
	/// <summary>
	/// Obtain read instruction response command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="resp"></param>
	/// <param name="wordCount"></param>
	/// <param name="readData"></param>
	/// <param name="timeout"></param>
	/// <returns></returns>
	int GetReadTagResp(int64_t hComm, TagResp* resp, unsigned char* wordCount, unsigned char* readData, unsigned short timeout);
	/// <summary>
	/// Get Tag Reply Command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="cmd"></param>
	/// <param name="resp"></param>
	/// <param name="timeout"></param>
	/// <returns></returns>
	int GetTagResp(int64_t hComm, unsigned short cmd, TagResp* resp, unsigned short timeout);
	/// <summary>
	/// Block Write Command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="option"></param>
	/// <param name="accPwd"></param>
	/// <param name="memBank"></param>
	/// <param name="wordPtr"></param>
	/// <param name="wordCount"></param>
	/// <param name="writeData"></param>
	/// <returns></returns>
	int WriteTag(int64_t hComm, unsigned char option, unsigned char* accPwd, unsigned char memBank, unsigned short wordPtr, unsigned char wordCount, unsigned char* writeData);
	/// <summary>
	/// Lock label command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="accPwd"></param>
	/// <param name="erea"></param>
	/// <param name="action"></param>
	/// <returns></returns>
	int LockTag(int64_t hComm, unsigned char* accPwd, unsigned char erea, unsigned char action);
	/// <summary>
	/// Inactivation label command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="accPwd"></param>
	/// <returns></returns>
	int KillTag(int64_t hComm, unsigned char* accPwd);
	/// <summary>
	/// Select Label Command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="maskPtr"></param>
	/// <param name="maskBits"></param>
	/// <param name="mask"></param>
	/// <returns></returns>
	int SetSelectMask(int64_t hComm, unsigned short maskPtr, unsigned char maskBits, unsigned char* mask);
	/// <summary>
	/// Get Q value command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="pqVal"></param>
	/// <param name="reserved"></param>
	/// <returns></returns>
	int GetCoilPRM(int64_t hComm, unsigned char* pqVal, unsigned char* reserved);
	/// <summary>
	/// Set Q value command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="qVal"></param>
	/// <param name="reserved"></param>
	/// <returns></returns>
	int SetCoilPRM(int64_t hComm, unsigned char qVal, unsigned char reserved);
	/// <summary>
	/// Obtain inventory label Selcet command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="proto"></param>
	/// <param name="param"></param>
	/// <returns></returns>
	int SelectOrSortGet(int64_t hComm, unsigned char proto, SelectSortParam* param);
	/// <summary>
	/// Set inventory label Selcet command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="proto"></param>
	/// <param name="param"></param>
	/// <returns></returns>
	int SelectOrSortSet(int64_t hComm, unsigned char proto, SelectSortParam* param);
	/// <summary>
	/// Query command to obtain inventory labels
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="proto"></param>
	/// <param name="param"></param>
	/// <returns></returns>
	int QueryCfgGet(int64_t hComm, unsigned char proto, QueryParam* param);
	/// <summary>
	/// Set Inventory Tag Query Command
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="proto"></param>
	/// <param name="param"></param>
	/// <returns></returns>
	int QueryCfgSet(int64_t hComm, unsigned char proto, QueryParam* param);
	/// <summary>
	/// Obtain antenna frequency
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="type"></param>
	/// <returns></returns>
	 int GetAntPower(int64_t hComm, AntPower* type);
	/// <summary>
	/// Set antenna frequency
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="type"></param>
	/// <returns></returns>
	 int SetAntPower(int64_t hComm, AntPower type);

	/// <summary>
	/// 获取GPIO工作参数
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="mode"></param>
	/// <returns></returns>
	int GetGPIOWorkParam(int64_t hComm, GPIOWorkParam* gpio);
	/// <summary>
	/// 设置GPIO工作参数
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="mode"></param>
	/// <returns></returns>
	int SetGPIOWorkParam(int64_t hComm, GPIOWorkParam gpio);
	/// <summary>
	/// 获取门通道输出参数
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="gpo"></param>
	/// <returns></returns>
	int GetGateWorkParam(int64_t hComm, GateWorkParam* gate);
	/// <summary>
	/// 设置门通道输出参数
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="gpo"></param>
	/// <returns></returns>
	int SetGateWorkParam(int64_t hComm, GateWorkParam gate);
	/// <summary>
	/// 获取通道门状态
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="status"></param>
	/// <returns></returns>
	int GetGateStatus(int64_t hComm, GateParam* status, unsigned short timeout);
	/// <summary>
	/// 获取EAS数据匹配
	/// </summary>
	int GetEASMask(int64_t hComm, EASMask* eas);
	/// <summary>
	/// 设置EAS数据匹配
	/// </summary>
	int SetEASMask(int64_t hComm, EASMask eas);
	/// <summary>
	/// 获取心跳包
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="heart"></param>
	/// <returns></returns>
	int GetHeartbeat(int64_t hComm, Heartbeat* heart);
	/// <summary>
	/// 设置心跳包
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="heart"></param>
	/// <returns></returns>
	int SetHeartbeat(int64_t hComm, Heartbeat heart);
	/// <summary>
	/// 获取门禁信息
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="access"></param>
	/// <returns></returns>
	int GetAccessInfo(int64_t hComm, AccessInfo* access);
	/// <summary>
	/// 通知设备进入白名单数据更新或获取流程
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="infoCount"></param>
	/// <returns></returns>
	int BeginWhiteList(int64_t hComm, unsigned char  Option, unsigned short infoCount);
	/// <summary>
	/// 获取白名单
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="whiteList"></param>
	/// <returns></returns>
	int GetWhiteList(int64_t hComm, WhiteList* whiteList, unsigned short timeout);
	/// <summary>
	/// 设置白名单
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="whiteList"></param>
	/// <returns></returns>
	int SetWhiteList(int64_t hComm, unsigned short len, const unsigned char * pParam);
	/// <summary>
	/// 结束设置白名单
	/// </summary>
	/// <param name="hComm"></param>
	/// <returns></returns>
	int EndWhiteList(int64_t hComm, unsigned short* infoCount);
	/// <summary>
	/// 获取门禁操作参数
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="aParam"></param>
	/// <returns></returns>
	int GetAccessOperateParam(int64_t hComm, AccessOperateParam* aParam);
	/// <summary>
	/// 获取门禁操作参数
	/// </summary>
	/// <param name="hComm"></param>
	/// <param name="aParam"></param>
	/// <returns></returns>
	int SetAccessOperateParam(int64_t hComm, AccessOperateParam aParam);

#ifdef __cplusplus
}
#endif

#endif

