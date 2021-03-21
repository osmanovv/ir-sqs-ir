# IR-SQS-IR
Remote IR control via AWS SQS FIFO queue.

![IR AWS SQS](https://github.com/osmanovv/ir-sqs-ir/blob/main/images/IR-SQS-IR.png)

## Amazon AWS SQS FIFO Queue setup

1. [Create an AWS account](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-setting-up.html)
2. [Create a queue](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-getting-started.html)

Don't forget to copy or download a file with your **Access key ID** and **Secret access key**.

While creating a queue name it `IRCommands.fifo` and choose `FIFO` _type_. Set `1 minute` as value for _Message retention period_ and `1 KB` for _Maximum message size_. Do not forget to *enable long polling* by changing _Receive message wait time_ to `20` seconds. This will reduce the service polling rate and allow more economical use of the request limit available in the free tier.

With _Amazon SQS Free Tier_ you can get started with Amazon SQS for free. All customers can make **1 million Amazon SQS requests for free each month**. Some applications might be able to operate within this Free Tier limit. [Amazon SQS pricing](https://aws.amazon.com/sqs/pricing/)

## IR receiver setup

![IR receiver](https://github.com/osmanovv/ir-sqs-ir/blob/main/images/IR-receiver.png)

Follow this detailed article [Raspberry Pi IR Receiver](https://blog.gordonturner.com/2020/05/31/raspberry-pi-ir-receiver/) by Gordon Turner to learn about alternate hardware options (IR receiver sensor, breadboard prototyping) and for verbose command output examples when testing functionality.

### Infrared receiver wiring diagram

I'm using a [KY-022](https://www.thegeekpub.com/wiki/sensor-wiki-ky-022-infrared-sensor/) module connected as follows:
```
KY-022 (IR receiver) pinout:
 A) Signal = GPIO 14 [Pin 08]
 B) Vсс+ = 3.3V [Pin 01]
 C) GND = GND [Pin 06]

Raspberry Pi pinout:
      Pin 01 Pin 02
    +3V3 [B] [ ] +5V
 GPIO 02 [ ] [ ] +5V
 GPIO 03 [ ] [C] GND (Pin 06)
 GPIO 04 [ ] [A] GPIO 14 (Pin 08)
     GND [ ] [ ] GPIO 15 (Pin 10)
         ... ...
```

### Raspberry Pi setup

Use the latest Raspberry Pi OS Lite (2020-12-02-raspios-buster-armhf-lite.zip) with the new kernel drivers for IR communication (no more LIRC).

Update the config variables:

    $ sudo nano /boot/config.txt

Add the following to the end:

    dtoverlay=gpio-ir,gpio_pin=14
    dtoverlay=gpio-ir-tx,gpio_pin=15

**Note:** As part of this configuration, IR **transmission** is also configured. If transmission is not needed, exclude `dtoverlay=gpio-ir-tx,gpio_pin=15`.

Reboot:

    $ sudo reboot

Confirm gpio modules are loaded:

    $ lsmod | grep gpio
    gpio_ir_recv           16384  0
    gpio_ir_tx             16384  0

Install `ir-keytable`:

    $ sudo apt install ir-keytable -y

To confirm install, run:

    $ ir-keytable

Enable all the kernel protocols:

    $ sudo ir-keytable -p all

**Note:** It's necessary to re-enable all protocols after reboot, so we will schedule this later using `cron`:

    $ sudo ir-keytable -s rc0 -p all
    $ sudo ir-keytable -s rc1 -p all

Test remote with `rc0` (if the receiver device is assigned to `/sys/class/rc/rc1` use `rc1`):

    $ ir-keytable -t -s rc0

Install Python and [python-evdev](https://github.com/gvalkov/python-evdev) package:

    $ sudo apt install python3-pip python3-dev python3-setuptools python3-wheel
    $ pip3 install evdev
	
Install boto3 - [The AWS SDK for Python](https://github.com/boto/boto3):

    $ pip3 install boto3

[Set up AWS Credentials and Region for Development](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html)

Create `.aws` directory in your home directory:

    $ mkdir .aws

Create AWS credentials file:

    $ nano ~/.aws/credentials

Replace `YOUR_KEY` and `YOUR_SECRET` with your credentials obtained from IAM (see "Amazon AWS SQS FIFO Queue setup" section):
```
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

Create simple AWS config file:

    $ nano .aws/config

Provide region:
```
[default]
region=us-east-1
```

Copy `sender.py` to your home directory.

To test run:

    $ python3 sender.py

Register script to run at startup with `crontab`:

    $ crontab -e
	
Add the following to the end:
```
@reboot sudo ir-keytable -s rc1 -p all
@reboot python3 /home/pi/sender.py
```
**Note:** Instead of `rc1` you may need to register `rc0`. I have noticed that executing both commands may not work at startup:
```
@reboot sudo ir-keytable -s rc0 -p all
@reboot sudo ir-keytable -s rc1 -p all
@reboot python3 /home/pi/sender.py &
```

After reboot you will be able to send IR commands to the remote queue. To stop it execute `$ sudo pkill -f python3`.



## IR transmitter setup

![IR transmitter](https://github.com/osmanovv/ir-sqs-ir/blob/main/images/IR-transmitter.png)

Follow this detailed article [Raspberry Pi IR Transmitter](https://blog.gordonturner.com/2020/06/10/raspberry-pi-ir-transmitter/) by Gordon Turner to learn about alternate hardware options (IR LEDs, breadboard prototyping) and for verbose command output examples when testing functionality.

### Infrared transmitter wiring diagram

IR transmitter module [KY-005](https://www.thegeekpub.com/wiki/sensor-wiki-ky-005-infrared-ir-transmitter/) connected like this:

```
KY-005 (IR transmitter) pinout:
 A) GND = GND [Pin 06]
 B) Vсс+ = 3.3V [Pin 01]
 C) Signal = GPIO 15 [Pin 10]

Raspberry Pi pinout:
      Pin 01 Pin 02
    +3V3 [B] [ ] +5V
 GPIO 02 [ ] [ ] +5V
 GPIO 03 [ ] [A] GND (Pin 06)
 GPIO 04 [ ] [ ] GPIO 14 (Pin 08)
     GND [ ] [C] GPIO 15 (Pin 10)
         ... ...
```

### Raspberry Pi setup

Use the latest Raspberry Pi OS Lite (2020-12-02-raspios-buster-armhf-lite.zip) with the new kernel drivers for IR communication (no more LIRC).

Update the config variables:

    $ sudo nano /boot/config.txt

Add the following to the end:

    dtoverlay=gpio-ir,gpio_pin=14
    dtoverlay=gpio-ir-tx,gpio_pin=15

**Note:** As part of this configuration, IR **receiver** is also configured. If receiving is not needed, exclude `dtoverlay=gpio-ir,gpio_pin=14`.

Reboot:

    $ sudo reboot

Confirm gpio modules are loaded:

    $ lsmod | grep gpio
    gpio_ir_recv           16384  0
    gpio_ir_tx             16384  0

Actually, that's it, now you can send IR commands with `ir-ctl -d /dev/lirc0 -S nec:0x408`, but we need to receive them from our queue.

Install Python:

    $ sudo apt install python3-pip python3-dev python3-setuptools python3-wheel
	
Install boto3 - [The AWS SDK for Python](https://github.com/boto/boto3):

    $ pip3 install boto3

[Set up AWS Credentials and Region for Development](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html)

Create `.aws` directory in your home directory:

    $ mkdir .aws

Create AWS credentials file:

    $ nano ~/.aws/credentials

Replace `YOUR_KEY` and `YOUR_SECRET` with your credentials obtained from IAM (see "Amazon AWS SQS FIFO Queue setup" section):
```
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

Create simple AWS config file:

    $ nano .aws/config

Provide region:
```
[default]
region=us-east-1
```

Copy `receiver.py` to your home directory.

**Note:** Used IR protocol hardcoded in the variable `protocol`. To determine the protocol your IR remote uses execute (on a device with IR receiver, see "IR receiver setup" section) `ir-keytable -t -s rc0` and capture few button presses.

To test run:

    $ python3 receiver.py

Register script to run at startup with `crontab`:

    $ crontab -e
	
Add the following to the end:
```
@reboot python3 /home/pi/receiver.py &
```

After reboot you will be able to receive IR commands from the remote queue and transmit them to a device. To stop it execute `$ sudo pkill -f python3`.

## References
The following are references that I found helpful:
* General instructions:
  * [Raspberry Pi IR Receiver](https://blog.gordonturner.com/2020/05/31/raspberry-pi-ir-receiver/)
  * [Raspberry Pi IR Transmitter](https://blog.gordonturner.com/2020/06/10/raspberry-pi-ir-transmitter/)
  * [Using Bare Metal IR on the Orange Pi Zero](https://www.sigmdel.ca/michel/ha/opi/ir_01_en.html)
  * [ir-keytable on the Orange Pi Zero](https://www.sigmdel.ca/michel/ha/opi/ir_03_en.html)
  * [Sending Infrared Commands From a Raspberry Pi Without LIRC](https://blog.bschwind.com/2016/05/29/sending-infrared-commands-from-a-raspberry-pi-without-lirc/)
  * [ir-ctl - a swiss-knife tool to handle raw IR and to set lirc options](http://manpages.ubuntu.com/manpages/bionic/man1/ir-ctl.1.html)
  * [Remote control media player without lirc using ir-keytable](https://madaboutbrighton.net/articles/2015/remote-control-media-player-without-lirc-using-ir-keymap)
* Amazon AWS SQS:
  * [Setting up Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-setting-up.html)
  * [Getting started with Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-getting-started.html)
  * [Set up AWS Credentials and Region for Development](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html)
  * [Displaying AWS SQS Message Counts on a Raspberry Pi](https://www.linkedin.com/pulse/displaying-aws-sqs-message-counts-raspberry-pi-james-matson/)
  * [Boto3 - The AWS SDK for Python](https://github.com/boto/boto3)
  * [Boto3 Docs - Developer guide - Configuration](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)
  * [Boto3 Docs - Developer guide - Resources](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html)
* Additional packages:
  * [python-evdev - Docs - Tutorial](https://python-evdev.readthedocs.io/en/latest/tutorial.html)
  * [python-evdev - API Reference - events](https://python-evdev.readthedocs.io/en/latest/apidoc.html#module-evdev.events)
* Alternative Python packages:
  * [pigpio](https://github.com/joan2937/pigpio)
  * [ircodec - A Python package that simplifies sending and receiving IR signals for the Raspberry Pi using pigpiod](https://github.com/kentwait/ircodec)
