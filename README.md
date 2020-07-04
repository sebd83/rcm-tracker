# rcm-tracker
This project is a simple python code to track and predict the next passes of RCM satellites and display the results on a inky pHAT on a Raspberry Pi. Data from NORAD lines.
<pre>
  _____   _____ __  __   _______ _____            _____ _  ________ _____  
 |  __ \ / ____|  \/  | |__   __|  __ \     /\   / ____| |/ /  ____|  __ \ 
 | |__) | |    | \  / |    | |  | |__) |   /  \ | |    | ' /| |__  | |__) |
 |  _  /| |    | |\/| |    | |  |  _  /   / /\ \| |    |  < |  __| |  _  / 
 | | \ \| |____| |  | |    | |  | | \ \  / ____ \ |____| . \| |____| | \ \ 
 |_|  \_\\_____|_|  |_|    |_|  |_|  \_\/_/    \_\_____|_|\_\______|_|  \_\
</pre>

==== Requirements ====
1. Python 3
with the following libraries
(to be completed with a venv and freeze requirements command)

2. Raspberry Pi OS

2a) optional, setup secure SSH to remote into raspberry pi
SSH with key auth
https://www.raspberrypi.org/documentation/configuration/security.md
https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md#copy-your-public-key-to-your-raspberry-pi
https://debian-administration.org/article/530/SSH_with_authentication_key_instead_of_password

3. Install inky pHAT from Pimodoro
https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat
<em>Open a new terminal, and type the following, making sure to type y or n when prompted:</em>
<pre>
curl https://get.pimoroni.com/inky | bash
</pre>
<em>Once that's done, it probably a good idea to reboot your Pi to let the changes propagate, if the installer doesn't prompt you to reboot.</em>


5. Install missing python dependancies
5a) SCIPY
https://raspberrypi.stackexchange.com/questions/8308/how-to-install-latest-scipy-version-on-raspberry-pi
<pre>
pip3 install pip --upgrade
</pre>
<pre>
wget https://www.piwheels.org/simple/scipy/scipy-1.5.0rc1-cp37-cp37m-linux_armv6l.whl#sha256=7385847629c084ab601c9e204078ed350741ad378d13550e0053ba48a3b8e91e
</pre>
<pre>
pip3 install scipy-1.5.0rc1-cp37-cp37m-linux_armv6l.whl
</pre>
<pre>
sudo apt-get install libopenblas-base
sudo apt-get install libopenblas-dev
sudo apt-get install libatlas-base-dev
</pre>

6. Setup Raspberry Pi to launch the script at bootup
https://www.raspberrypi.org/documentation/linux/usage/cron.md
<pre>
crontab -e
</pre>
add the following line at the end of the file
<pre>
@reboot python3 /home/pi/rcm-tracker/pi_boot_main.py
</pre>

==== BOM ====
PI-ZERO-WH Raspberry Pi Zero W Version 1.1 with Headers
PIM367 Yellow/Black/White – Inky pHAT (ePaper/eInk/EPD)
DC-5250-MUSB Adaptateur mural Alimentation 5V DC 2.5A (connecteur micro B USB)
COMP-130B Micro-B USB Câble OTG
COMP-520 Mini HDMI to Standard HDMI Adapter

===== Last Details =====
To stop the infinite loop that refreshes the raspberry pi every X seconds, connect to the pi via SSH and send the kill command:
<pre>
ps -ef|grep python
</pre>
Identify the process id that runs the loop (5445 in the example below)
<pre>
root      1006     1  0 Jun27 ?        00:03:10 /usr/bin/python3 /usr/bin/fail2ban-server -xf start
pi        5445  4772 14 09:22 pts/2    00:03:28 python3 pi_boot_main.py
pi        5482  5469  0 09:46 pts/3    00:00:00 grep --color=auto python
</pre>
Then kill the process
<pre>
kill 5445
</pre>
