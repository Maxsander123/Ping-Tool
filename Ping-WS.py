import socket
import struct
import time
import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog
import threading
import multiprocessing
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from datetime import datetime

ICMP_ECHO_REQUEST = 8

def checksum(source_string):
    """Calculate checksum of the source string."""
    sum = 0
    count_to = (len(source_string) // 2) * 2
    count = 0
    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + this_val
        sum = sum & 0xFFFFFFFF
        count = count + 2

    if count_to < len(source_string):
        sum = sum + source_string[-1]
        sum = sum & 0xFFFFFFFF

    sum = (sum >> 16) + (sum & 0xFFFF)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xFFFF
    answer = answer >> 8 | (answer << 8 & 0xFF00)
    return answer

def create_packet(seq_number):
    """Create an ICMP packet."""
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, 1, seq_number)
    data = struct.pack("d", time.time())
    my_checksum = checksum(header + data)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), 1, seq_number)
    return header + data

def ping_worker(address, interval, count, results, index):
    """Worker process to perform ping operations."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        results[index] = [(f"Permission Denied: Run the script as an administrator.", None)]
        return

    seq_number = 0
    worker_results = []
    for _ in range(count):
        packet = create_packet(seq_number)
        seq_number += 1
        start_time = time.time()
        sock.sendto(packet, (address, 1))
        try:
            sock.settimeout(interval)
            recv_packet, _ = sock.recvfrom(1024)
            end_time = time.time()
            elapsed_time = (end_time - start_time) * 1000
            worker_results.append((f"Reply from {address}: time={elapsed_time:.3f}ms", elapsed_time))
        except socket.timeout:
            worker_results.append((f"Request timed out for seq {seq_number}", None))
        time.sleep(interval)

    results[index] = worker_results

def aggregate_results(results):
    """Aggregate results from all processes."""
    all_times = []

    for worker_result in results:
        for message, elapsed_time in worker_result:
            if elapsed_time is not None:
                all_times.append(elapsed_time)

            result_box.insert(tk.END, message + "\n")
            result_box.see(tk.END)

    min_times = min(all_times) if all_times else 0
    max_times = max(all_times) if all_times else 0
    avg_times = sum(all_times) / len(all_times) if all_times else 0

    update_graph(all_times, min_times, max_times, avg_times)
    return results, min_times, max_times, avg_times

def start_ping():
    address = address_entry.get()
    interval = float(interval_entry.get())
    count = int(count_entry.get())
    save_dir = directory_entry.get()

    if not save_dir or not os.path.exists(save_dir):
        result_box.insert(tk.END, "Invalid or missing directory. Please set a valid save directory.\n")
        return

    num_workers = multiprocessing.cpu_count()
    result_box.delete(1.0, tk.END)  # Clear previous results

    # Split workload among workers
    count_per_worker = count // num_workers
    remainder = count % num_workers

    manager = multiprocessing.Manager()
    results = manager.list([None] * num_workers)

    processes = []
    for i in range(num_workers):
        worker_count = count_per_worker + (1 if i < remainder else 0)
        p = multiprocessing.Process(target=ping_worker, args=(address, interval, worker_count, results, i))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    aggregated_results, min_times, max_times, avg_times = aggregate_results(results)
    save_results(aggregated_results, address, save_dir, interval, count, min_times, max_times, avg_times)

def update_graph(all_times, min_times, max_times, avg_times):
    """Update the graph with the current statistics."""
    for widget in graph_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots()
    x = range(1, len(all_times) + 1)

    ax.plot(x, all_times, label="Ping Times (ms)")
    ax.axhline(y=min_times, color="green", linestyle="--", label=f"Min: {min_times:.2f} ms")
    ax.axhline(y=max_times, color="red", linestyle="--", label=f"Max: {max_times:.2f} ms")
    ax.axhline(y=avg_times, color="blue", linestyle="--", label=f"Avg: {avg_times:.2f} ms")

    ax.set_xlabel("Ping Count")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Ping Statistics")
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def save_results(results, address, directory, interval, count, min_times, max_times, avg_times):
    """Save the ping results to a file in the specified directory."""
    # Find the next available file number
    date = datetime.now().strftime("%Y-%m-%d")
    file_number = 1
    while os.path.exists(f"{directory}/{date}-{address}-{file_number}.txt"):
        file_number += 1

    file_path = f"{directory}/{date}-{address}-{file_number}.txt"

    with open(file_path, "w") as f:
        f.write(f"Ping Results for {address}\n")
        f.write(f"Date: {date}\n")
        f.write(f"Interval: {interval} seconds\n")
        f.write(f"Ping Count: {count}\n")
        f.write(f"Minimum Time: {min_times:.3f} ms\n")
        f.write(f"Maximum Time: {max_times:.3f} ms\n")
        f.write(f"Average Time: {avg_times:.3f} ms\n")
        f.write("\nDetailed Results:\n")

        for worker_result in results:
            for message, _ in worker_result:
                f.write(message + "\n")

    result_box.insert(tk.END, f"Results saved to {file_path}\n")

def select_directory():
    """Open a dialog to select the save directory."""
    selected_dir = filedialog.askdirectory(title="Select Directory to Save Results")
    if selected_dir:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, selected_dir)

def clear_results():
    """Clear the result box and reset the graph."""
    result_box.delete(1.0, tk.END)
    for widget in graph_frame.winfo_children():
        widget.destroy()

# GUI setup
root = tk.Tk()
root.title("Ping Utility with Multi-Core Support")
root.geometry("1000x800")
root.configure(bg="#f0f0f0")

# Input fields
frame = tk.Frame(root, bg="#f0f0f0", padx=10, pady=10)
frame.pack(pady=10, fill=tk.X)

tk.Label(frame, text="IP/Address:", bg="#f0f0f0", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
address_entry = ttk.Entry(frame, width=30)
address_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Interval (seconds):", bg="#f0f0f0", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
interval_entry = ttk.Entry(frame, width=10)
interval_entry.grid(row=1, column=1, padx=5, pady=5)
interval_entry.insert(0, "0.001")  # Default value

tk.Label(frame, text="Number of Pings:", bg="#f0f0f0", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
count_entry = ttk.Entry(frame, width=10)
count_entry.grid(row=2, column=1, padx=5, pady=5)
count_entry.insert(0, "100")  # Default value

tk.Label(frame, text="Save Directory:", bg="#f0f0f0", font=("Arial", 12)).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
directory_entry = ttk.Entry(frame, width=30)
directory_entry.grid(row=3, column=1, padx=5, pady=5)

directory_button = ttk.Button(frame, text="Select...", command=select_directory)
directory_button.grid(row=3, column=2, padx=5, pady=5)

tk.Label(frame, text="Number of Workers:", bg="#f0f0f0", font=("Arial", 12)).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
worker_entry = ttk.Entry(frame, width=10)
worker_entry.grid(row=4, column=1, padx=5, pady=5)
worker_entry.insert(0, str(multiprocessing.cpu_count()))

# Buttons
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=10)

start_button = ttk.Button(button_frame, text="Start Ping", command=start_ping)
start_button.grid(row=0, column=0, padx=5)

clear_button = ttk.Button(button_frame, text="Clear Results", command=clear_results)
clear_button.grid(row=0, column=1, padx=5)

# Result box
result_label = tk.Label(root, text="Ping Results:", bg="#f0f0f0", font=("Arial", 12))
result_label.pack(anchor=tk.W, padx=15)
result_box = scrolledtext.ScrolledText(root, width=90, height=20, font=("Courier", 10))
result_box.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

# Graph frame
graph_label = tk.Label(root, text="Ping Statistics Graph:", bg="#f0f0f0", font=("Arial", 12))
graph_label.pack(anchor=tk.W, padx=15)
graph_frame = tk.Frame(root, bg="#ffffff", relief=tk.SUNKEN, borderwidth=2)
graph_frame.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

# Run the application
root.mainloop()
