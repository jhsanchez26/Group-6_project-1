import secrets
import sys
import os
import time
import psutil
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Rotor Machine
from Rotor import RotorMachine

# Import DES class
import importlib.util
spec = importlib.util.spec_from_file_location("des_module", "Des.py")
des_module = importlib.util.module_from_spec(spec)
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()
try:
    spec.loader.exec_module(des_module)
finally:
    sys.stdout = old_stdout

DES = des_module.DES


class PerformanceAnalyzer:
    """
    Analyzes performance metrics for the hybrid cryptosystem.
    """
    
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.cpu_percent_samples = []
        self.memory_percent_samples = []
        self.monitoring = False
        
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.perf_counter()
        self.cpu_percent_samples = []
        self.memory_percent_samples = []
        self.monitoring = True
        
        # Start resource monitoring in background
        def monitor_resources():
            while self.monitoring:
                self.cpu_percent_samples.append(psutil.cpu_percent(interval=0.01))
                self.memory_percent_samples.append(psutil.virtual_memory().percent)
                time.sleep(0.01)
        
        self.monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.end_time = time.perf_counter()
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=0.1)
    
    def get_computation_time(self):
        """Get computation time in milliseconds."""
        return (self.end_time - self.start_time) * 1000
    
    def get_average_cpu_usage(self):
        """Get average CPU usage percentage."""
        return sum(self.cpu_percent_samples) / len(self.cpu_percent_samples) if self.cpu_percent_samples else 0
    
    def get_average_memory_usage(self):
        """Get average memory usage percentage."""
        return sum(self.memory_percent_samples) / len(self.memory_percent_samples) if self.memory_percent_samples else 0
    
    def analyze_complexity(self, message_length):
        """
        Analyze computational complexity based on message length.
        
        Rotor Machine: O(n) where n is message length
        DES: O(n) where n is message length (processes in 64-bit blocks)
        Combined: O(n) overall
        """
        rotor_complexity = f"O(n) where n = {message_length}"
        des_blocks = (message_length + 7) // 8  # 8 chars per 64-bit block (with padding)
        des_complexity = f"O(n) where n = {message_length} chars → {des_blocks} blocks"
        hybrid_complexity = f"O(n) where n = {message_length}"
        
        return {
            'rotor': rotor_complexity,
            'des': des_complexity,
            'hybrid': hybrid_complexity,
            'message_length': message_length,
            'des_blocks': des_blocks
        }


class HybridCryptosystem:
    """
    Hybrid cryptosystem that uses both Rotor Machine and DES.
    
    Encryption flow: Plaintext -> Rotor Machine -> DES -> Ciphertext
    Decryption flow: Ciphertext -> DES -> Rotor Machine -> Plaintext
    """
    
    def __init__(self, rotor1_wiring=None, rotor2_wiring=None, rotor3_wiring=None,
                 rotor1_notch=0, rotor2_notch=0, rotor3_notch=0,
                 rotor1_pos=0, rotor2_pos=0, rotor3_pos=0, des_key=None):
        """
        Initialize the hybrid cryptosystem.
        
        Args:
            rotor1_wiring: Wiring configuration for rotor 1 (leftmost)
            rotor2_wiring: Wiring configuration for rotor 2 (middle)
            rotor3_wiring: Wiring configuration for rotor 3 (rightmost)
            rotor1_notch: Notch position for rotor 1
            rotor2_notch: Notch position for rotor 2
            rotor3_notch: Notch position for rotor 3
            rotor1_pos: Initial position for rotor 1
            rotor2_pos: Initial position for rotor 2
            rotor3_pos: Initial position for rotor 3
            des_key: 64-bit key for DES (list of bits)
        """
        # Default rotor configurations if not provided
        if rotor1_wiring is None:
            rotor1_wiring = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
        if rotor2_wiring is None:
            rotor2_wiring = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
        if rotor3_wiring is None:
            rotor3_wiring = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
        
        # Initialize Rotor Machine
        self.rotor_machine = RotorMachine(
            rotor1_wiring, rotor2_wiring, rotor3_wiring,
            rotor1_notch, rotor2_notch, rotor3_notch,
            rotor1_pos, rotor2_pos, rotor3_pos
        )
        
        # Store initial rotor positions for reset
        self.initial_rotor_positions = (rotor1_pos, rotor2_pos, rotor3_pos)
        
        # Initialize DES
        self.des = DES()
        
        # Generate or use provided DES key
        if des_key is None:
            self.des_key = [secrets.randbelow(2) for _ in range(64)]
        else:
            self.des_key = des_key
    
    def reset_rotors(self):
        """Reset the rotor machine to initial positions."""
        self.rotor_machine.reset(*self.initial_rotor_positions)
    
    def encrypt(self, plaintext):
        """
        Encrypt plaintext using Rotor Machine first, then DES.
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            Encrypted bit array (DES output format)
        """
        # Reset rotors to initial position
        self.reset_rotors()
        
        # Encrypt with Rotor Machine
        rotor_encrypted = self.rotor_machine.encrypt(plaintext)
        
        # Encrypt the rotor output with DES
        des_encrypted = self.des.encrypt(rotor_encrypted, self.des_key)
        
        return des_encrypted
    
    def decrypt(self, ciphertext_bits):
        """
        Decrypt ciphertext using DES first, then Rotor Machine.
        
        Args:
            ciphertext_bits: Encrypted bit array (from DES)
        
        Returns:
            Decrypted plaintext string
        """
        # Decrypt with DES
        des_decrypted = self.des.decrypt(ciphertext_bits, self.des_key)
        
        # Reset rotors and decrypt with Rotor Machine
        self.reset_rotors()
        rotor_decrypted = self.rotor_machine.encrypt(des_decrypted)
        
        return rotor_decrypted
    
    def encrypt_to_string(self, plaintext):
        """
        Encrypt plaintext and return as readable string.
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            Tuple of (encrypted_bits, encrypted_string_representation)
        """
        encrypted_bits = self.encrypt(plaintext)
        encrypted_string = self.des.bits_to_string(encrypted_bits)
        return encrypted_bits, encrypted_string
    
    def get_des_key_hex(self):
        """
        Get the DES key as a hexadecimal string for display.
        
        Returns:
            Hexadecimal representation of the DES key
        """
        # Convert bit array to hex string
        hex_str = ""
        for i in range(0, len(self.des_key), 4):
            nibble = self.des_key[i:i+4]
            val = 0
            for bit in nibble:
                val = (val << 1) | bit
            hex_str += format(val, 'x')
        return hex_str.upper()
    
    def set_des_key_from_hex(self, hex_key):
        """
        Set the DES key from a hexadecimal string.
        
        Args:
            hex_key: 16-character hexadecimal string representing 64-bit key
        """
        if len(hex_key) != 16:
            raise ValueError("Hex key must be exactly 16 characters (64 bits)")
        
        bits = []
        for char in hex_key:
            val = int(char, 16)
            bits.extend([(val >> i) & 1 for i in range(3, -1, -1)])
        
        self.des_key = bits


def main():
    """
    Test the hybrid cryptosystem with test messages and performance analysis.
    """    
    # Create hybrid cryptosystem
    crypto = HybridCryptosystem(
        rotor1_notch=16, rotor2_notch=4, rotor3_notch=21
    )
    
    # Create performance analyzer
    analyzer = PerformanceAnalyzer()
 
    # Test messages
    test_messages = ['HOW ARE YOU', 'HAPPY NEW YEAR', 'WELCOME TO PUERTO RICO']
    
    # Store performance data for all tests
    all_performance_data = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"Plaintext {i}: '{message}'")
        print()
        
        # Start performance monitoring
        analyzer.start_monitoring()
        
        # Rotor Machine Encryption (E1)
        crypto.reset_rotors()
        rotor_encrypted = crypto.rotor_machine.encrypt(message)

        print("Encryption:")
        print(f"E1 (Rotor): {rotor_encrypted}")
        
        # DES Encryption (E2)
        des_encrypted_bits = crypto.des.encrypt(rotor_encrypted, crypto.des_key)
        des_encrypted_string = crypto.des.bits_to_string(des_encrypted_bits)
        print(f"E2 (DES):   {des_encrypted_string.encode('unicode_escape').decode('ascii')}")
        
        print()
        print("Decryption:")
        
        # DES Decryption (D1)
        des_decrypted = crypto.des.decrypt(des_encrypted_bits, crypto.des_key)
        print(f"D1 (DES):   {des_decrypted}")
        
        # Rotor Machine Decryption (D2)
        crypto.reset_rotors()
        final_decrypted = crypto.rotor_machine.encrypt(des_decrypted)  # Rotor is symmetric
        print(f"D2 (Rotor): {final_decrypted}")
        
        # Stop performance monitoring
        analyzer.stop_monitoring()
        
        # Verification
        print(f"Plaintext = Decryption?: {'Yes' if message.upper() == final_decrypted.upper() else 'No'}")
        print()
        
        # Collect performance data
        computation_time = analyzer.get_computation_time()
        cpu_usage = analyzer.get_average_cpu_usage()
        memory_usage = analyzer.get_average_memory_usage()
        complexity_analysis = analyzer.analyze_complexity(len(message))
        
        performance_data = {
            'test_num': i,
            'message': message,
            'computation_time': computation_time,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'complexity': complexity_analysis
        }
        all_performance_data.append(performance_data)
    
    # Display computational performance analysis
    print("PERFORMANCE ANALYSIS")
    print()
    
    for data in all_performance_data:
        print(f"Test {data['test_num']}: '{data['message']}'")
        print(f"  Computational Complexity (Big O): {data['complexity']['hybrid']}")
        print(f"  Computation Time: {data['computation_time']:.2f} ms")
        print(f"  CPU Usage: {data['cpu_usage']:.1f}%")
        print(f"  Memory Usage: {data['memory_usage']:.1f}%")
        print(f"  Message Length: {data['complexity']['message_length']} characters")
        print(f"  DES Blocks Processed: {data['complexity']['des_blocks']} blocks")
        print()
    
    # Overall statistics
    total_time = sum(data['computation_time'] for data in all_performance_data)
    avg_cpu = sum(data['cpu_usage'] for data in all_performance_data) / len(all_performance_data)
    avg_memory = sum(data['memory_usage'] for data in all_performance_data) / len(all_performance_data)
    total_chars = sum(data['complexity']['message_length'] for data in all_performance_data)
    
    print("OVERALL STATISTICS:")
    print(f"  Total Computation Time: {total_time:.2f} ms")
    print(f"  Average CPU Utilization: {avg_cpu:.1f}%")
    print(f"  Average Memory Utilization: {avg_memory:.1f}%")
    print(f"  Total Characters Processed: {total_chars}")
    print(f"  Average Time per Character: {total_time/total_chars:.3f} ms/char")
    print()


if __name__ == "__main__":
    main()
