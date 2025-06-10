import pandas as pd


def up_file():
    # 读取Excel文件
    file_path = r"C:\Users\XYCX\Desktop\广州市.xlsx"  # 请替换为你的Excel文件路径
    df = pd.read_excel(file_path)

    # 提取司机ID列
    driver_ids = df['司机ID'].astype(str).str.strip()  # 清理空格并转换为字符串

    # 每4900行一个sheet
    chunk_size = 4900
    num_chunks = (len(driver_ids) + chunk_size - 1) // chunk_size

    # 创建一个Excel文件
    with pd.ExcelWriter(r"C:\Users\XYCX\Desktop\喜行广州.xlsx", engine='openpyxl') as writer:
        for i in range(num_chunks):
            start_row = i * chunk_size
            end_row = min(start_row + chunk_size, len(driver_ids))

            # 获取当前块的司机ID
            chunk = driver_ids[start_row:end_row].reset_index(drop=True)

            # 创建固定内容
            header = [
                '导入说明：\n1.模版字段信息（表头）不可增加或删除。前3行不可删除，需要导入的数据从第4行开始。\n2.红色字段为必填信息；蓝色字段为示例数据，不可删除或修改。\n3.最多支持5000行数据。\n4.添加司机时，仅支持导入当前城市司机。\n5.删除司机时，仅支持删除当前城市已加入优质司机车队的司机。',
                '司机ID',
                '28178517147'
                # '导入说明：\n1.模版字段信息（表头）不可增加或删除。前3行不可删除，需要导入的数据从第4行开始。2.红色字段为必填信息；蓝色字段为示例数据，不可删除或修改。',
                # '司机编号',
                # '28178517147'
            ]

            # 创建新的DataFrame，将固定内容与司机ID合并
            data = pd.DataFrame(header + chunk.tolist(), columns=['内容'])

            # 将数据写入相应的sheet
            data.to_excel(writer, sheet_name=f'Sheet{i + 1}', index=False, header=False)

    print("数据拆分完成！")


up_file()

