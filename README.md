# The Howard Ratner of Bots

## Description

Python bot I created to read messages from a +EV sports betting discord (https://twitter.com/OxJuiced), parse message, and place the bets for me.
Through out the day bets need to be placed quickly as lines shift rapidly. To automate this process and increase likely of getting bets in on time, I created this bot.

Feel free to have a look around and setup the bot yourself (or take the parts that you like).
Currently the bot is only designed to work for prizepicks.

The bot also has an email service that can be setup with proper credientials. If setup, emails will be sent to specified recipients.
Emails are sent if:

- A bet is successfulled placed (time, website, date, amount wagered, and URL to the slip are all included in the email)
- A bet is failed to be placed

I can answer questions via email or discord. Feel free to reach out.

- Email: jonwakefield.mi@gmail.com
- Discord: notkevindurant#4421

## NOTE

Please be careful and courteous when operating the bot. Some websites do not allow bots to act as user agents. Please keep this in mind.

## What is EV betting:

Here's a video that explains what EV betting is: https://www.youtube.com/watch?v=y8HopDn4M9A

## Disclaimer

Use this project at your own discretion.
I can not be held liable for any bot malfunctions.

## Diagram

Highlevel diagram outlining how the bot works
![High level system diagram](system_diagram.png)
