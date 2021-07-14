# Space Bot

<p align="center">
    <a href="https://github.com/HackerSpace-PESU/spacebot/issues" alt="issues">
    <img alt="GitHub forks" src="https://img.shields.io/github/issues/HackerSpace-PESU/spacebot"></a>
    <a href="https://github.com/HackerSpace-PESU/spacebot/stargazers" alt="Stars">
    <img alt="GitHub stars" src="https://img.shields.io/github/stars/HackerSpace-PESU/spacebot"></a>
    <a href="https://github.com/HackerSpace-PESU/spacebot/contributors" alt="Contributors">
    <img src="https://img.shields.io/github/contributors/HackerSpace-PESU/spacebot"/></a>
</p>

Space Bot, a Discord bot built for HackerSpace Club of PES University

## What can Space Bot do?

1. Space Bot allows you to lookup any mentor or topic
2. It updates you about Instagram posts made by HackerSpace clubs
3. You can also code - It supports over 20 languages!
4. You can post questions and answers anonymously 

Run `!help` to check out all the features.
## How to run Space Bot?

1. Clone the repository
```bash
git clone git@github.com:HackerSpace-PESU/spacebot.git
```

2. Create a separate virtual environment to install the dependencies. You can use virtualenv -- it is simple to setup and use.
```bash
cd spacebot
virtualenv bot
```

3. Activate the virtual environment
    * Windows 
        ```bash
        .\bot\Scripts\activate.bat
        ```
    * Linux/Mac
        ```bash
        source bot/bin/activate
        ```

4. Install the dependencies
    * Windows
        ```bash
        pip install -r requirements.txt
        ```
    * Linux/Mac
        ```bash
        pip3 install -r requirements.txt
        ```

5. Setup the following environment variables in a `.env`
```bash
COMPILER_CLIENT_ID_1=
COMPILER_CLIENT_SECRET_1=
COMPILER_CLIENT_ID_2=
COMPILER_CLIENT_SECRET_2=
COMPILER_CLIENT_ID_3=
COMPILER_CLIENT_SECRET_3=
COMPILER_CLIENT_ID_4=
COMPILER_CLIENT_SECRET_4=
COMPILER_CLIENT_ID_5=
COMPILER_CLIENT_SECRET_5=
GUILD_ID=
BOT_ID=
BOT_TOKEN=
CHANNEL_ANNOUNCEMENTS=
CHANNEL_ANNOUNCEMENTS_RR=
CHANNEL_ANNOUNCEMENTS_EC=
CHANNEL_UNASSIGNED=
CHANNEL_WELCOME=
CHANNEL_BOT_TEST=
CHANNEL_SELECTION_YEAR=
CHANNEL_SELECTION_TOPIC=
CHANNEL_SELECTION_CAMPUS=
ROLE_UNASSIGN=
ROLE_BOT_DEV=
ROLE_MOD=
ROLE_CORE_RR=
ROLE_CORE_EC=
ROLE_FIRSTYEAR=
ROLE_SECONDYEAR=
ROLE_THIRDYEAR=
ROLE_FOURTHYEAR=
ROLE_GRAD=
ROLE_CAMPUS_RR=
ROLE_CAMPUS_EC=
ROLE_CAMPUS_OUTSIDER=
```

6. Run the bot using the following command
```bash
python3 src/bot.py
```

## How to contribute to Space Bot?

1. Fork this repository
​
2. Create a new branch called `username-beta`
​
3. Make your changes and create a pull request with the following information in the request message: 
    - The functionality you wish to change/add | What did you change/add
    - Screenshots of the feature working at your end
​
4. Send a review request to one or all of the following:
    - `ArvindAROO`
    - `sach-12`
    - `aditeyabaral`
    - `DevMashru`
​
5. Wait for approval for reviewers. Your PR may be directly accepted or requested for further changes

**Important**: Under no circumstances is anyone allowed to merge to the main branch.

## Maintainers

Contact any of us for any support.

[Arvind Krishna](https://github.com/ArvindAROO)<br>
[Sachin Shankar](https://github.com/sach-12)<br>
[Aditeya Baral](https://github.com/aditeyabaral)<br>
[Dev Mashru](https://github.com/DevMashru)

