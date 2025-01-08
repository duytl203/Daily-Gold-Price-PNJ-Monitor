import requests
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
from io import BytesIO

def get_information_telegram():
    chat_id = '***************************'  # Replace with your actual chat ID
    bot_token = '****************'  # Replace with your bot token
    return chat_id,bot_token

def get_table_gold_pnj():
    data = []
    try:
        response = requests.get('https://giavang.pnj.com.vn', timeout=10)
        response.raise_for_status()  # Raise an error for bad HTTP response
        
        soup = BeautifulSoup(response.text, 'html.parser')
        headers = [th.text.strip() for th in soup.find_all("th", class_="style1")]
        table_body = soup.find_all("tbody")
        
        for tbody in table_body:
            rows = tbody.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if cells[0].get("rowspan"):
                    current_region = cells[0].text.strip()
                    data.append([current_region, cells[1].text.strip(), cells[2].text.strip(), cells[3].text.strip(), cells[4].text.strip()])
                else:
                    data.append([current_region, cells[0].text.strip(), cells[1].text.strip(), cells[2].text.strip(), cells[3].text.strip()])
        
        # Convert data to pandas DataFrame
        gold_table = pd.DataFrame(data, columns=headers)
        gold_table['Giá mua'] = gold_table['Giá mua'].astype(str).str.replace('.', '', regex=False).astype(int)
        gold_table['Giá bán'] = gold_table['Giá bán'].astype(str).str.replace('.', '', regex=False).astype(int)
        gold_table['Thời gian cập nhật'] = pd.to_datetime(gold_table['Thời gian cập nhật'], format="%d/%m/%Y %H:%M:%S")
        # gold_table['Loại vàng'] = np.where(gold_table['Khu vực'] != 'Giá vàng nữ trang',gold_table['Loại vàng'] + ' ' + gold_table['Khu vực'],gold_table['Loại vàng'])
        
        gold_table_final = gold_table.groupby(['Loại vàng', 'Thời gian cập nhật']).agg(
            buy_price=('Giá mua', 'max'),
            sale_price=('Giá bán', 'max')
        ).reset_index()

        order = ['Vàng 333 (8K)', 'Vàng 375 (9K)', 'Vàng 416 (10K)', 'Vàng 585 (14K)', 'Vàng 610 (14.6K)', 'Vàng 650 (15.6K)', 
         'Vàng 680 (16.3K)', 'Vàng 750 (18K)', 'Vàng 916 (22K)', 'Vàng nữ trang 99', 'Vàng nữ trang 999', 'Vàng nữ trang 999.9', 
         'Nhẫn Trơn PNJ 999.9', 'PNJ', 'SJC']

        gold_table_final['Loại vàng'] = pd.Categorical(gold_table_final['Loại vàng'], categories=order, ordered=True)
        return gold_table_final.sort_values('Loại vàng')
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request error: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")

def create_chart(df):
    plt.figure(figsize=(12, 6))
    
    x = np.arange(len(df["Loại vàng"]))  # Tạo các giá trị trên trục x
    plt.plot(x, df["buy_price"], marker='o', label="Giá mua", color='blue', alpha=0.7)
    plt.plot(x, df["sale_price"], marker='o', label="Giá bán", color='red', alpha=0.7)
    
    # Hiển thị giá trị trên mỗi điểm
    for i in range(len(df)):
        # Giá trị "Giá mua" hiển thị phía dưới
        plt.text(x[i], df["buy_price"].iloc[i], f"{df['buy_price'].iloc[i]}", ha='center', va='top', fontsize=10, color='blue')
        # Giá trị "Giá bán" hiển thị phía trên
        plt.text(x[i], df["sale_price"].iloc[i], f"{df['sale_price'].iloc[i]}", ha='center', va='bottom', fontsize=10, color='red')
    
    # Cấu hình biểu đồ
    plt.xlabel("Loại vàng")
    plt.ylabel("Giá (VND)")
    plt.title(f"Giá mua và bán theo loại vàng (Cập nhật vào: {df["Thời gian cập nhật"].iloc[0]})")
    plt.xticks(x, df["Loại vàng"], rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    # Save chart to a BytesIO object
    chart_image = BytesIO()
    plt.savefig(chart_image, format='png')
    chart_image.seek(0)  # Rewind the BytesIO object to the start
    return chart_image
