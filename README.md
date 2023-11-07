# Hacking Tuya Zigbee Ethernet Gateway

Hello, I want you to present the method of hacking Tuya Zigbee Gateway. This time we will be talking about ethernet model.
I`m in possession of DMD2CC-V1.0 gateway. There is a lot of other devices with same PCB board. Including LIDL Gateway.
Just open your model and check if board is similar.

![Picture of gatewa](/images/gateway.jpg)

I have marked few things on picture.
- Yellow dot - our target, CPU, realtek one. Responsible for the logic. Tuya Linux is working on it.
- Pink dot - Zigbee Module. Details: [TYZS Datasheet](https://developer.tuya.com/en/docs/iot/zigbeetyzs4module?id=K989rhycrz23f).
- Red dot - Flash module, contains bootloader and linux opearting system. This flash module uses SPI interface to communication.
            Can be easily read by CH341a Programmer. [Reading flash](https://www.youtube.com/watch?v=4qX2zihB6UE).
            In my case i had to desolder chip from board
- Blue dot - Connector. Exposes serial interface and SWD for TYZS module.
## Communicating with device
To be able to do some unusuall stuff you need to buy a USB<>RS232 Converter with 3.3V,
You also will need to buy goldpins/cables to connect converter to board. Some
soldering skills are required.
## Bootloader
Once you connect your converter, run program to communicate. In my case i have used Putty or GNU Screen.
Default bitrate 38400.
Once you connect it, you should see something similar
ending discover...

    Booting...

    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @
    @ chip__no chip__id mfr___id dev___id cap___id size_sft dev_size chipSize
    @ 0000000h 0XXXXXXh 0000XXXh 0000040h 0000018h 0000000h 0000018h 1000000h
    @ blk_size blk__cnt sec_size sec__cnt pageSize page_cnt chip_clk chipName
    @ 0010000h 0000100h 0001000h 0001000h 0000100h 0000010h 000004eh GD25Q128
    @
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    DDR1:32MB

    ---RealTek(RTL8196E)at 2022.03.29-15:59+0800 v3.4T-pre2 [16bit](380MHz)
    P0phymode=01, embedded phy
    check_image_header  return_addr:05010000 bank_offset:00000000
    no sys signature at 00010000!
    get uboot flag failed
    Jump to image start=0x80c00000...
    decompressing kernel:
    Uncompressing Linux... done, booting the kernel.
    done decompressing kernel.
    start address: 0x80003780
    Linux version 3.10.90 (wsj@LAPTOP-MO8FQJRA) (gcc version 4.6.4 (Realtek RSDK-4.6.4 Build 2080) ) #8 Tue Mar 29 16:04:50 CST 2022`
    ...
    ...
    Creating 5 MTD partitions on "flash_bank_1":
    0x000000000000-0x000000020000 : "boot+cfg"
    0x000000020000-0x000000200000 : "linux"
    0x000000200000-0x000000400000 : "rootfs"
    0x000000400000-0x000000420000 : "tuya-label"
    0x000000420000-0x000001000000 : "jffs2-fs"


You finally will get a Linux login. Unfortunately, password is not known and in many cases is unique to each device.
Most probably, password assigment is done on connection to Tuya cloud (when you have added your device to tuya)
In some cases you can break the boot procedure and you can try to manipulate flash memory. To do this, hit ESC at the begining of boot.
In my case bootloader has been locked (checked bootloader code). I had to use SPI Flash reader device to hack this gateway for the first time.

## ESC key is not giving you realtek prompt
Still, I`m suggeting you to check all other possible ways for getting prompt. If nothing is working for you, there is a huge chance that
you have Zigbee gateway with locked bootloader.

Fortunately, there is a way to get Realtek boot prompt even if it is locked. Boot program is doing initial configuration and it is performing Linux kernel loading
to memory, verification and running Image from memory. We will get prompt when something has fail. For me, easiet method was to "corrupt" FLASH :-).
To do this you will need following stuff:
- thin wire or wire with pins.
- a hand

Connect one end of wire somewhere you have a ground. I just attatched it to ethernet port. There is a shield around ethernet port. This
shield is grounded. **Do not connect** second end of cable.
![Hack](/images/hack.jpg)

This method might wont work out of the box. All you need is practice.
Regarding second end of cable: we will be trying to do a glich. You need to do it when bootloader starts. Once you will see some bootloader text from screen
you will need to connect second end of wire to SPI Flash memory. Check your flash and connect it to SCLK interface.

When you do it properly you will get following text on terminal:

    ---RealTek(RTL8196E)at 2022.03.29-15:59+0800 v3.4T-pre2 [16bit](380MHz)
    P0phymode=01, embedded phy
    check_image_header  return_addr:05010000 bank_offset:00000000
    no sys signature at 00010000!
    […]
    no sys signature at 0003D000!
    no sys signature at 0003E000!
    no sys signature at 0003F000!
    no sys signature at 00040000!
    get uboot flag failed
    P0phymode=01, embedded phy


    ---Ethernet init Okay!
    <RealTek>

Hooray.

Next, we will need to get root password.
Now depending on your device you may need to read tuya-label flash or decode file.

## Method 1 AUZKEY is stored on Tuya-Label
This is simple situation. Your key is stored on part of flash memory called tuya-label.
All you need to to is to read a flash memory section with key.
Creating 5 MTD partitions on "flash_bank_1":

    0x000000400000-0x000000420000 : "tuya-label"
Follow procedure described in:
[Hacking Lidl Gateway](https://community.openhab.org/t/hacking-the-lidl-silvercrest-zigbee-gateway-a-step-by-step-tutorial/129660).

## Method 2 We dont care about AUZKEY
In this method you will not need to have AUZKEY. You will write your own password.
Follow [Paul Banks Hack](https://paulbanks.org/projects/lidl-zigbee/#firmware-hacking)

## Method 3 We care about AUZKEY
If method 2 fails, you can try method 3. Get AUZKEY from `jffs2-fs` section of memory.
I did little research on tuyamd executable and I have succesfully extracted (or decoded) auzkey.
To extract auzkey you need to:
- dump jffs2 partition (you can dump memory by using previous method or using programmer)
- extract jffs2 partition - [Jefferson github](https://github.com/sviehb/jefferson)
- get two files: config/License.file1 and config/License.key

Then, use following program to decode.

[AUZKEY decode script](scripts/decode.py)

It will give you output:


    Decrypted data:

    b'{"bsn":"XXXX","master_mac":"XXXXXX","auzkey":"XXXXXXXXXXXXX","uuid":"XXXXXXXXXX","prodtest_exit":"true"}\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f'
Also file License.out with decrypted data will be produced.

Last 8 digits of AUZKEY is your password

Once you get root, you can adopt device to your needs.
