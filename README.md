# creds

## Description
Creds is made to be extremely simple to use.

Creds is a helper script for penetration testing and CTFs. It allows you to quickly save found credentials directly from your terminal and split them up into three files - CREDSpasswords.txt, CREDSusers.txt, CREDScredentials.txt. These are simple files on disk and you can edit them by hand. Got a list of usernames during Active Directory enumeration? Paste them in your CREDSusers.txt file! You can then use these files as you would if you manually kept pasting stuff into them.

The purpose of the tool is to minimize the time your eyes strays off target so you don't have to locate the corressponding textfiles to save the output or to go look for passwords or users. You just simply work directly via command-line and continue on your path to compromise.

## Installation
Copy the creds.py file to your path of choice. Rename it to `creds`, set permissions and make it executable with `chmod 7400 ./creds.py && chmod +x ./creds.py`. I personally make a symbolic link to it so i can use it from /usr/bin: `sudo ln -s /home/kali/creds /usr/bin/creds` but it should work if it's in $PATH also.

## Usage
Invoking creds without any arguments shows you the full usage help, the state of the environment variables if set, and the configuration file paths. It will also count the number of each logged value. If no current configuration is set, **It will also create the config.ini in `/home/USERNAME/.config/creds/config.ini` and set the paths based on the current working directory if it does not exist already**. If you are starting a new engagement or CTF I highly recommend you set the paths so that creds saves the files in the directory where you keep your loot. You can use `creds --set-paths /PATH/TO/LOOT` to start fresh with a new set of files. Creds does not overwrite files so you can point it to an old engagement and continue where you left off!

```bash
~/Documents $ creds
usage: creds [-h] [--list [{all,creds,passwords,users}]] [--set-paths DIR] [-u] [-p] [-c] [value]

Store users/passwords/credentials quickly from the command line. creds is a CTF-tool to keep track of found usernames and passwords.

positional arguments:
  value                 Value to store

options:
  -h, --help            show this help message and exit
  --list [{all,creds,passwords,users}]
                        List saved entries
  --set-paths DIR       Set all creds paths to DIR, create files, and write env/config
  -u                    Treat value as username
  -p                    Treat value as password
  -c                    Treat value as full credential

Hack all the things! /Eric Marsh (swesecnerd)

Environment variable state:
- CREDS_PASSWORDS is not set
- CREDS_USERS is not set
- CREDS_CREDENTIALS is not set
- CREDS_SEPARATOR is not set

Configured file paths:
- users: /home/kali/Documents/CREDSusers.txt
- passwords: /home/kali/Documents/CREDSpasswords.txt
- credentials: /home/kali/Documents/CREDScredentials.txt
- separator: :
- config file: /home/kali/.config/creds/config.ini

Current counts:
- users: 0
- passwords: 0
- credentials: 0

```
## Examples

You found something that looks like a password in a powershell script. Quickly add it with creds. The `-p` argument tells creds that this is explicitly a password:
```bash
$ creds -p 'FoundPassw0rd!!!'                
stored as password
```

You keep searching and two usernames, `alice` and `bob` catches your eyes. Lets add them as BOTH username and password since we may want to test that against a service. When no argument is given, and no separator (`:` or `%`) is found in the string, creds automatically saves it both ways.
```bash
$ creds 'alice'                              
no separator/flag found; stored in users and passwords

$ creds 'bob'  
no separator/flag found; stored in users and passwords
```

To print all stored values you can use the argument `--list` followed by nothing (which prints everything) or by your choice of 'creds', 'passwords', or 'users' to print the corresponding list.
Let's see what we have so far. Invoke creds with the `--list` argument:

```bash
$ creds --list               
[users]
alice
bob

[passwords]
FoundPassw0rd!!!
alice
bob

[creds]
```
Nice!
You test the `alice` username with the `FoundPassw0rd!!!` password against SSH and it's successful! Let's add this as a known credential:
Note that creds is stupidly simple (and simply stupid) and will add duplicates to your lists if you are not careful. The easiest way to add a credential that you have already tried is with the `-c` argument:

```bash
$ creds -c 'alice':'FoundPassw0rd!!!' 
stored as credential
```

Let's see the new stored data:

```bash
$ creds --list                        
[users]
alice
bob

[passwords]
FoundPassw0rd!!!
alice
bob

[creds]
alice:FoundPassw0rd!!!
```
Tip! you can use `-c` if you want to add `NTLM hashes`, `JWT-tokens`, or any other odd credential to creds as it should not mind at all. Adding explicit credentials also allow you to write whatever you want...

```bash
$ creds -c 'JWT-token for Administrator at http://example.com: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30'

$ creds --list creds
[creds]
alice:FoundPassw0rd!!!
joeadmin:MySeCr3tPassw0rd!!!
NTLM for svc_mysql: eed224b4784bb040aab50b8856fe9f02
JWT-token for Administrator at http://example.com: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30
```

Back to the story...
You also discover a set of valid credentials in a .php file and obviously want to test both the username and the password separately in the future. We'll let creds automate that for us:

```bash
$ creds 'joeadmin':'MySeCr3tPassw0rd!!!'
stored as username, password, and credential using separator ':'

$ creds --list                          
[users]
alice
bob
joeadmin

[passwords]
FoundPassw0rd!!!
alice
bob
MySeCr3tPassw0rd!!!

[creds]
alice:FoundPassw0rd!!!
joeadmin:MySeCr3tPassw0rd!!!
```
Note that creds stored that as a complete credential and also split the username and password into their corresponding files for future use!
When adding credentials without any arguments, creds tries to identify if it's a complete credential or if it should be saved as both username and password. Creds assumes that a complete credential looks something like 'USERNAME':'PASSWORD' or 'USERNAME'%'PASSWORD' but you can force it to save whatever you want using arguments!

Let's use our current credentials in other tools! We can use the path to the files directly, or we can use environment variables if we have them set. Let's see our current config by running creds without any arguments again:

```bash
$ creds                                                                                                
usage: creds [-h] [--list [{all,creds,passwords,users}]] [--set-paths DIR] [-u] [-p] [-c] [value]

...

Environment variable state:
- CREDS_PASSWORDS is not set
- CREDS_USERS is not set
- CREDS_CREDENTIALS is not set
- CREDS_SEPARATOR is not set

Configured file paths:
- users: /home/kali/Documents/CREDSusers.txt
- passwords: /home/kali/Documents/CREDSpasswords.txt
- credentials: /home/kali/Documents/CREDScredentials.txt
- separator: :
- config file: /home/kali/.config/creds/config.ini

...
```
We can clearly see the configured file paths, but we'll let creds fill in the environment variables for us. For clarity, we'll use the absolute path but you can also use a relative path. If we run  `creds --set-paths DIRECTORY` to point to our configured file paths above, creds will simply add a `/home/USERNAME/.config/creds/creds.env` file with the correct info for our current engagement:

```bash
$ creds --set-paths /home/kali/Documents/
Updated paths to:
- CREDS_USERS=/home/kali/Documents/CREDSusers.txt
- CREDS_PASSWORDS=/home/kali/Documents/CREDSpasswords.txt
- CREDS_CREDENTIALS=/home/kali/Documents/CREDScredentials.txt
- config written: /home/kali/.config/creds/config.ini
- env file written: /home/kali/.config/creds/creds.env
Run: source /home/kali/.config/creds/creds.env
usage: creds [-h] [--list [{all,creds,passwords,users}]] [--set-paths DIR] [-u] [-p] [-c] [value]

Store users/passwords/credentials quickly from the command line. creds is a CTF-tool to keep track of found usernames and passwords.

positional arguments:
  value                 Value to store

options:
  -h, --help            show this help message and exit
  --list [{all,creds,passwords,users}]
                        List saved entries
  --set-paths DIR       Set all creds paths to DIR, create files, and write env/config
  -u                    Treat value as username
  -p                    Treat value as password
  -c                    Treat value as full credential

Hack all the things! /Eric Marsh (swesecnerd)

Environment variable state:
- CREDS_PASSWORDS is set (/home/kali/Documents/CREDSpasswords.txt)
- CREDS_USERS is set (/home/kali/Documents/CREDSusers.txt)
- CREDS_CREDENTIALS is set (/home/kali/Documents/CREDScredentials.txt)
- CREDS_SEPARATOR is not set

Configured file paths:
- users: /home/kali/Documents/CREDSusers.txt
- passwords: /home/kali/Documents/CREDSpasswords.txt
- credentials: /home/kali/Documents/CREDScredentials.txt
- separator: :
- config file: /home/kali/.config/creds/config.ini

Current counts:
- users: 3
- passwords: 4
- credentials: 2
```
Great! We are almost there. In the output creds tells us to Run: `source /home/kali/.config/creds/creds.env` so let's do that. There is no output but by using the `env` command we can view our current environment settings:

```bash
$ env
COLORFGBG=15;0
COLORTERM=truecolor
...
CREDS_USERS=/home/kali/Documents/CREDSusers.txt
CREDS_PASSWORDS=/home/kali/Documents/CREDSpasswords.txt
CREDS_CREDENTIALS=/home/kali/Documents/CREDScredentials.txt
CREDS_SEPARATOR=:
...
```
Done! We can now substitute the full path to our files by using the environment variable $CREDS_USERS, $CREDS_PASSWORDS, or even $CREDS_CREDENTIALS. Let's test this in our current scenario!

During our enumeration we come across a password-protected zip archive, `info.zip`. We'll try to crack it using john with our current list of passwords:

First, we create a hash using zip2john `zip2john info.zip > hash.info.zip`. Then we attempt to crack it by setting $CREDS_PASSWORDS as our wordlist:
```bash
$ john --wordlist=$CREDS_PASSWORDS hash.info.zip
Using default input encoding: UTF-8
Loaded 1 password hash (ZIP, WinZip [PBKDF2-SHA1 512/512 AVX512BW 16x])
Cost 1 (HMAC size) is 296698 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
Warning: Only 4 candidates left, minimum 64 needed for performance.
MySeCr3tPassw0rd!!! (info.zip/info.pdf)     
1g 0:00:00:00 DONE (2026-02-28 22:57) 50.00g/s 200.0p/s 200.0c/s 200.0C/s FoundPassw0rd!!!..MySeCr3tPassw0rd!!!
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```
BAM SON!

Be aware that environment variables are set in the current session. If you open a second terminal you will need to run `source /home/kali/.config/creds/creds.env` again if you want to use environment variables. However, the config file is still there so creds still works in new terminals and will continue to use the same files for storage when you add creds.

### Configuration and setup
Simply running `creds` in a directory of your choice will set the current configuration file to that directory if it doesen't exist. You can configure the files location in the config file or via environment variables, which will take precedence if set.


#### Using the environment variables
Environment variables are bound to your current session. Set them in your .bashrc (or equivalent) to make them permanent or simply run `--set-paths` and then source the env-file at the start of a new engagement. For every new terminal session you can then source the environment variables since they are stored beside the config file. Run `creds` without arguments to see current paths.
Since the environment variables point to files on disk, you can use them in other tools. You can use '$CREDS_PASSWORDS' and '$CREDS_USERS' for password spraying or in your credential test loop.

### Dividing character
If no dividing character is found (':' or '%' or USER-DEFINED) the script falls back to the script arguments to identify if the added credential is a '-u' USERNAME, '-p' PASSWORD, '-c' CREDENTIAL, or if no argument, will place the string in both CREDSpasswords.txt and CREDSusers.txt. This is by design since we definately want to test if a user has set their username as a password!

## Note!
Creds is stupid simple (and simply stupid) and can make misstakes now and then. Make sure you check that everything saved as you intended when you have edge cases. A password with separator characters can trick creds into believing that you actually gave it a complete credential. To avoid this, use the `-p` flag to save a password as just a password.

## Note on passwords with shell-breaking characters
A password containing single quotes and double quotes can break standard input and leave you hanging with a `quote>`. The workaround is adding a `$` before the single quoted string and escaping breaking characters with a backslash. In the example below we escape the double quote after the word "Pass" and the single quote after the word "quote".

```bash
creds 'username':$'Pass\"word!With quote\''
stored as credential using separator ':'
$ creds --list creds

[creds]
...
username:Pass"word!With quote'
```

### TODO / Future improvements: 
I kind of like how creds is working right now so I don't really feel the need for changes. But maybe I could...
- Add support for comments for usernames and passwords aswell. This will most likely require an extra file to ensure that the files still work with any normal cracking-/brute force tool.
- I'm deeply in love with Netexec and I might add the option of syncing creds with the credentials stored in the workspaces in Netexec... We'll see :-)

