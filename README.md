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

Requirements:
1. Python 3
with the following libraries
(to be completed with a venv and freeze requirements command)

2. Raspberry Pi OS

2. a) optional, setup secure SSH to remote into raspberry pi
SSH with key auth
https://www.raspberrypi.org/documentation/configuration/security.md
https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md#copy-your-public-key-to-your-raspberry-pi
https://debian-administration.org/article/530/SSH_with_authentication_key_instead_of_password

3. Install inky pHAT from Pimodoro
https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat
Open a new terminal, and type the following, making sure to type y or n when prompted:
<pre>
curl https://get.pimoroni.com/inky | bash
</pre>
Once that's done, it probably a good idea to reboot your Pi to let the changes propagate, if the installer doesn't prompt you to reboot.

4. Install node-red
https://nodered.org/docs/getting-started/raspberrypi

Running the following command will download and run the script. If you want to review the contents of the script first, you can view it here.
(https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
<pre>
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
</pre>
This script will:
*remove the pre-packaged version of Node-RED and Node.js if they are present
*install the current Node.js LTS release using the NodeSource. If it detects Node.js is already installed from NodeSource, it will ensure it is at least Node 8, but otherwise leave it alone
*install the latest version of Node-RED using npm
*optionally install a collection of useful Pi-specific nodes
*setup Node-RED to run as a service and provide a set of commands to work with the service
