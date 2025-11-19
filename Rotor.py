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
    
    def rotate_rotors(self):
        """
        Rotate the rotors.
        Rightmost rotor always rotates. Middle and leftmost rotate when
        the previous rotor completes a full rotation.
        """
        # Rightmost rotor always rotates
        rotor3_completed = self.rotor3.rotate()
        
        # Middle rotor rotates if rightmost completed a rotation
        if rotor3_completed:
            rotor2_completed = self.rotor2.rotate()
            # Leftmost rotor rotates if middle completed a rotation
            if rotor2_completed:
                self.rotor1.rotate()
    
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


def main():
    """
    Test the rotor machine with the provided messages.
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
    
    # Test messages
    test_messages = ['HELLO', 'HOPE', 'NEW YEAR']
    
    for message in test_messages:
        # Reset machine to initial state
        machine.reset()
        
        # Encrypt
        encrypted = machine.encrypt(message)
        
        # Reset machine to same initial state for decryption
        machine.reset()
        
        # Decrypt (can use encrypt again for the same result)
        decrypted = machine.encrypt(encrypted)
        
        print(f"Plaintext: {message}")
        print(f"Cyphertext: {encrypted}")
        print(f"Decrypted Plaintext: {decrypted}")
        print(f"Plaintext = Decryption?: {'Yes' if message.upper() == decrypted else 'No'}")
        print()


if __name__ == "__main__":
    main()

