import psycopg2, hashlib
import gold_price_etl_secret_code
import telegram
import asyncio

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

dataset  = gold_price_etl_secret_code.get_table_gold_pnj()
chat_id,bot_token = gold_price_etl_secret_code.get_information_telegram()

# Định nghĩa DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 8, 9),
    'retries': 0,  # Disable retries
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'gold_price_monitor',
    default_args=default_args,
    description='Daily Gold Price Tracking Tool',
    schedule_interval='0 2 * * *',  # Chạy mỗi ngày lúc 9h sáng UTC
    catchup=False,
)

# Tạo task trong DAG
def etl_task():
    data = dataset
    if data is not None:
        insert_or_update(data)

def review_data():
    data = dataset
    if data is not None:
        # Chuyển đổi dữ liệu thành dạng chuỗi để hiển thị trong log
        print("Dữ liệu vàng mới nhất:")
        print(data.to_string(index=False))
    else:
        print("Không có dữ liệu để review.")

async def send_chart_to_telegram(chat_id,bot_token,dataset):    
    # Get dataset and create chart
    if dataset is not None:
        chart_image = gold_price_etl_secret_code.create_chart(dataset)
        
        # Send the chart as photo to Telegram
        bot = telegram.Bot(token=bot_token)
        await bot.send_photo(chat_id = chat_id,photo=chart_image)

# Hàm đồng bộ bọc hàm async
def send_telegram_message():
    asyncio.run(send_chart_to_telegram(chat_id,bot_token,dataset))

# Task review dữ liệu
review_task = PythonOperator(
    task_id='review_task',
    python_callable=review_data,
    dag=dag,
)

send_telegram_message = PythonOperator(
    task_id='send_telegram_message',
    python_callable=send_telegram_message,
    dag=dag,
)

# Thứ tự thực thi
review_task >> send_telegram_message
