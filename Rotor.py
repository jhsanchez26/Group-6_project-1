import time
import psutil
import threading


class PerformanceAnalyzer:
    """
    Analyzes performance metrics for the rotor machine.
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
class Rotor:
    """
    Represents a single rotor in a rotor machine.
    Each rotor has a wiring configuration and can rotate.
    """

    def __init__(self, wiring, notch_position=0, initial_position=0):
        """
        Initialize a rotor.

        Args:
            wiring: A string of 26 characters representing the substitution mapping
            notch_position: Position where the rotor triggers the next rotor (0-25)
            initial_position: Starting position of the rotor (0-25)
        """
        self.wiring = wiring.upper()
        self.notch_position = notch_position
        self.position = initial_position
        # Create reverse wiring for decryption
        self.reverse_wiring = [''] * 26
        for i, char in enumerate(self.wiring):
            self.reverse_wiring[ord(char) - ord('A')] = chr(ord('A') + i)
        self.reverse_wiring = ''.join(self.reverse_wiring)

    def rotate(self):
        """
        Rotate the rotor by one position.
        Returns True if the rotor completed a full rotation.
        """
        self.position = (self.position + 1) % 26
        return self.position == self.notch_position

    def encrypt_forward(self, char):
        """
        Encrypt a character going forward through the rotor.

        Args:
            char: Character to encrypt (A-Z)

        Returns:
            Encrypted character
        """
        if not char.isalpha():
            return char

        char = char.upper()
        # Convert to index (0-25)
        index = (ord(char) - ord('A') + self.position) % 26
        # Apply wiring
        encrypted_char = self.wiring[index]
        # Account for rotation offset
        encrypted_index = (ord(encrypted_char) - ord('A') - self.position) % 26
        return chr(ord('A') + encrypted_index)

    def encrypt_backward(self, char):
        """
        Encrypt a character going backward through the rotor (for decryption).

        Args:
            char: Character to encrypt (A-Z)

        Returns:
            Encrypted character
        """
        if not char.isalpha():
            return char

        char = char.upper()
        # Convert to index (0-25)
        index = (ord(char) - ord('A') + self.position) % 26
        # Apply reverse wiring
        encrypted_char = self.reverse_wiring[index]
        # Account for rotation offset
        encrypted_index = (ord(encrypted_char) - ord('A') - self.position) % 26
        return chr(ord('A') + encrypted_index)


class RotorMachine:
    """
    Rotor machine with 3 rotors.
    Encrypts/Decrypts with rotor rotation.
    """

    def __init__(self, rotor1_wiring, rotor2_wiring, rotor3_wiring,
                 rotor1_notch=0, rotor2_notch=0, rotor3_notch=0,
                 rotor1_pos=0, rotor2_pos=0, rotor3_pos=0):
        """
        Initialize the rotor machine with 3 rotors.

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
        """
        self.rotor1 = Rotor(rotor1_wiring, rotor1_notch, rotor1_pos)
        self.rotor2 = Rotor(rotor2_wiring, rotor2_notch, rotor2_pos)
        self.rotor3 = Rotor(rotor3_wiring, rotor3_notch, rotor3_pos)
        self.rotation_count = 0  # Track total rotations for performance analysis
    
    def rotate_rotors(self):
        """
        Rotate the rotors.
        Rightmost rotor always rotates. Middle and leftmost rotate when
        the previous rotor completes a full rotation.
        """
        # Rightmost rotor always rotates
        rotor3_completed = self.rotor3.rotate()
        self.rotation_count += 1
        
        # Middle rotor rotates if rightmost completed a rotation
        if rotor3_completed:
            rotor2_completed = self.rotor2.rotate()
            self.rotation_count += 1
            # Leftmost rotor rotates if middle completed a rotation
            if rotor2_completed:
                self.rotor1.rotate()
                self.rotation_count += 1
    
    def encrypt_char(self, char):
        """
        Encrypt a single character through all rotors.

        Args:
            char: Character to encrypt

        Returns:
            Encrypted character
        """
        if not char.isalpha():
            return char

        # Rotate rotors before encryption
        self.rotate_rotors()

        char = char.upper()

        # Forward through rotors
        result = self.rotor3.encrypt_forward(char)
        result = self.rotor2.encrypt_forward(result)
        result = self.rotor1.encrypt_forward(result)

        # Reflector
        result = chr(ord('Z') - (ord(result) - ord('A')))

        # Backward through rotors
        result = self.rotor1.encrypt_backward(result)
        result = self.rotor2.encrypt_backward(result)
        result = self.rotor3.encrypt_backward(result)

        return result

    def encrypt(self, message):
        """
        Encrypt a message.

        Args:
            message: Plaintext string to encrypt

        Returns:
            Encrypted string
        """
        encrypted = []
        for char in message:
            if char.isalpha():
                encrypted.append(self.encrypt_char(char))
            else:
                encrypted.append(char)
        return ''.join(encrypted)

    def reset(self, rotor1_pos=0, rotor2_pos=0, rotor3_pos=0):
        """
        Reset the rotors to initial positions.

        Args:
            rotor1_pos: Position for rotor 1
            rotor2_pos: Position for rotor 2
            rotor3_pos: Position for rotor 3
        """
        self.rotor1.position = rotor1_pos
        self.rotor2.position = rotor2_pos
        self.rotor3.position = rotor3_pos
        self.rotation_count = 0  # Reset rotation counter


def main():
    """
    Test the rotor machine with performance analysis.
    """
    # Define wiring configurations for the 3 rotors
    rotor1_wiring = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
    rotor2_wiring = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
    rotor3_wiring = "BDFHJLCPRTXVZNYEIWGAKMUSQO"

    # Create rotor machine
    machine = RotorMachine(
        rotor1_wiring, rotor2_wiring, rotor3_wiring,
        rotor1_notch=16, rotor2_notch=4, rotor3_notch=21
    )
    
    # Create performance analyzer
    analyzer = PerformanceAnalyzer()
    
    # Test messages
    test_messages = ['HELLO', 'HOPE', 'NEW YEAR']
    
    # Store performance data for all tests
    all_performance_data = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: '{message}'")
        print()
        
        # Start performance monitoring
        analyzer.start_monitoring()
        
        # Reset machine to initial rotor positions
        machine.reset(0, 0, 0)

        # Encrypt
        encrypted = machine.encrypt(message)
        encryption_rotations = machine.rotation_count
        
        # Reset machine to same initial rotor positions for decryption
        machine.reset(0, 0, 0)

        # Decrypt (can use encrypt again for the same result)
        decrypted = machine.encrypt(encrypted)
        total_rotations = encryption_rotations + machine.rotation_count
        
        # Stop performance monitoring
        analyzer.stop_monitoring()
        
        print(f"Plaintext:  {message}")
        print(f"Encrypted:  {encrypted}")
        print(f"Decrypted:  {decrypted}")
        print(f"Plaintext = Decryption?: {'Yes' if message.upper() == decrypted else 'No'}")
        print()
        
        # Collect performance data
        computation_time = analyzer.get_computation_time()
        cpu_usage = analyzer.get_average_cpu_usage()
        memory_usage = analyzer.get_average_memory_usage()
        performance_data = {
            'test_num': i,
            'message': message,
            'computation_time': computation_time,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'message_length': len(message),
            'total_rotations': total_rotations
        }
        all_performance_data.append(performance_data)
    
    # Display comprehensive performance analysis
    print("=" * 80)
    print("ROTOR MACHINE PERFORMANCE ANALYSIS")
    print("=" * 80)
    print()
    
    for data in all_performance_data:
        print(f"Test {data['test_num']}: '{data['message']}'")
        print(f"  Computation Time: {data['computation_time']:.2f} ms")
        print(f"  CPU Usage: {data['cpu_usage']:.1f}%")
        print(f"  Memory Usage: {data['memory_usage']:.1f}%")
        print(f"  Message Length: {data['message_length']} characters")
        print(f"  Total Rotor Rotations: {data['total_rotations']}")
        print()
    
    # Overall statistics
    total_time = sum(data['computation_time'] for data in all_performance_data)
    avg_cpu = sum(data['cpu_usage'] for data in all_performance_data) / len(all_performance_data)
    avg_memory = sum(data['memory_usage'] for data in all_performance_data) / len(all_performance_data)
    total_chars = sum(data['message_length'] for data in all_performance_data)
    total_rotations = sum(data['total_rotations'] for data in all_performance_data)
    
    print("OVERALL STATISTICS:")
    print(f"  Total Computation Time: {total_time:.2f} ms")
    print(f"  Average CPU Utilization: {avg_cpu:.1f}%")
    print(f"  Average Memory Utilization: {avg_memory:.1f}%")
    print(f"  Total Characters Processed: {total_chars}")
    print(f"  Total Rotor Rotations: {total_rotations}")
    print(f"  Average Time per Character: {total_time/total_chars:.3f} ms/char")
    print()


if __name__ == "__main__":
    main()
