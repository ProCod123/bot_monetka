import datetime



def log_data_to_file(data, filename="log.txt"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
    with open(filename, "a", encoding='utf-8') as file:
        file.write(f"{timestamp}: {data}\n")
