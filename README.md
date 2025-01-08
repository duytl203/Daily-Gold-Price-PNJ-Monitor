# Daily-Gold-Price-PNJ-Monitor
Starting from the accumulation of two types of gold, PNJ and SJC, last year, and because it took too much time every day to visit websites or apps to check the gold prices, I decided to program a schedule to receive daily gold price information through Telegram.

When using it, you just need to replace the **chat_id** and **bot_token** in the get_information_telegram function in the file gold_price_etl_secret_code.py, and you're good to go. 

These are the necessary details to get information from the chat box, which you will have to create yourself in Telegram. To create your own chat box, you can search on Google for more information!

Every day at 2 AM UTC, you will receive a chart from Telegram to get the gold price you need daily.

After that, just run the **start.sh** file, and you're all set!
![image](https://github.com/user-attachments/assets/a7be00c8-31dc-4773-892c-0235f572ee52)
