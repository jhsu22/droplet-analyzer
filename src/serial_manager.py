"""
Serial Manager Script

Communicates to connected Arduino board
"""

import queue
import threading
import time

import serial
import serial.tools.list_ports

from config import SerialConfig, serial_config


class SerialManager:
    def __init__(self, port, baud_rate):
        self.serial_connection = serial.Serial()
        self.serial_connection.port = port
        self.serial_connection.baudrate = baud_rate
        self.serial_connection.timeout = 1

        self.read_queue = queue.Queue()
        self.is_running = False
        self.reader_thread = None

    def connect(self):
        if self.serial_connection.is_open:
            print("Already connected.")
            return True

        try:
            self.serial_connection.open()
            time.sleep(2)  # Wait for the Arduino to reset

            print(
                f"Connected to {self.serial_connection.port} at {self.serial_connection.baudrate} baud"
            )

            self.is_running = True
            self.reader_thread = threading.Thread(target=self.read_loop)
            self.reader_thread.start()

            print("Started reader thread.")

            return self.serial_connection

        except serial.SerialException as e:
            print(f"Failed to connect to {self.serial_connection.port}: {e}")
            return False

    def read_loop(self):
        while self.is_running:
            try:
                line = self.serial_connection.readline().decode("utf-8").strip()
                if line:
                    self.read_queue.put(line)

            except serial.SerialException as e:
                print(f"Serial error: {e}. Stopping reader thread.")
                self.is_running = False
                break

            except Exception as e:
                print(f"Error in reader thread: {e}")
                pass

            time.sleep(0.01)

    def send_command(self, command):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                if not command.endswith(
                    "\n"
                ):  # Add a newline character if it wasn't in the command
                    command += "\n"

                self.serial_connection.write(
                    command.encode("utf-8")
                )  # Send the command to the Arduino
                time.sleep(0.1)  # Wait for the Arduino to process the command

            except serial.SerialException as e:
                print(f"Failed to send command: {e}")
                return None
        else:
            print("Serial connection not established.")
            return None

    def read_line(self, timeout=None):
        try:
            return self.read_queue.get(block=True, timeout=timeout)

        except queue.Empty:
            return None

    def disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.is_running = False

            if self.reader_thread:
                self.reader_thread.join()

            self.serial_connection.close()

            serial_config.status = "disconnected"
            print("Disconnected.")

        else:
            print("Serial connection not established.")


def list_ports():
    ports = serial.tools.list_ports.comports()

    for port in ports:
        return (port.device, port.description)
