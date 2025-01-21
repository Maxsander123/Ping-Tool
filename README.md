# Ping Utility with Multi-Core Support

This is a Python-based graphical application designed to perform ICMP ping operations efficiently using multi-core processing. The tool provides graphical and textual insights into ping statistics, making it suitable for network troubleshooting and analysis.

## Features

- **ICMP Ping Support**: Sends ICMP echo requests to a specified address.
- **Multi-Core Processing**: Leverages multiple cores to perform pings concurrently.
- **Graphical Interface**: Includes a user-friendly GUI built with `tkinter`.
- **Ping Statistics**: Displays minimum, maximum, and average response times.
- **Graph Visualization**: Visual representation of ping times over the count.
- **Result Export**: Saves detailed results in text files for future reference.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Maxsander123/Ping-Tool.git
   cd Ping-Tool
   ```
2. Ensure Python 3.7+ is installed on your system.
3. Install the required dependencies:
   ```bash
   pip install matplotlib
   ```
4. Run the script with administrator privileges (required for raw socket operations):
   ```bash
   sudo python Ping-WS.py  # On Linux/MacOS
   python Ping-WS.py       # On Windows (run from an elevated terminal)
   ```

## Usage

1. Launch the script to open the GUI.
2. Enter the target IP/hostname, ping interval, and count in the respective fields.
3. Choose a directory to save results.
4. Click "Start Ping" to initiate the operation.
5. View results in the text area and ping statistics on the graph.

## Important Note: Responsible Usage

This tool is intended for educational and diagnostic purposes. It **must not** be used for:

- Generating excessive traffic to overload or disrupt services (Denial of Service - DoS).
- Sending pings with malicious intent.

### Legal Notice

Misuse of this tool to harm networks or systems violates ethical standards and may breach local laws and regulations. The authors bear no responsibility for misuse. Always obtain proper authorization before testing any network or system.

## Contributing

Contributions are welcome! If you encounter issues or have feature suggestions, please open an issue or submit a pull request on [GitHub](https://github.com/Maxsander123/Ping-Tool)
