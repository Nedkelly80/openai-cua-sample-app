import subprocess
import time
import tempfile
import os
import signal
from typing import Literal, List, Dict


class LibmuttComputer:
    """Computer implementation for the mutt email client.
    
    This provides an interface to interact with mutt through terminal commands
    and screenshots. Mutt is a text-based email client that runs in terminal.
    """
    
    def __init__(self, display=":0"):
        self.display = display
        self.mutt_process = None
        self.dimensions = (1280, 720)  # Default terminal size
        
    def get_environment(self) -> Literal["windows", "mac", "linux", "browser"]:
        return "linux"
    
    def get_dimensions(self) -> tuple[int, int]:
        return self.dimensions
    
    def __enter__(self):
        """Start mutt in a terminal emulator."""
        try:
            # Check if we have a display available
            result = subprocess.run(
                ["echo", "$DISPLAY"], 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            # Start xterm with mutt if display is available
            if self.display:
                # Launch mutt in xterm for visual interaction
                self.mutt_process = subprocess.Popen([
                    "xterm", 
                    "-display", self.display,
                    "-geometry", "160x50",
                    "-title", "Mutt Email Client",
                    "-e", "mutt"
                ], 
                env={**os.environ, "DISPLAY": self.display}
                )
                time.sleep(2)  # Give mutt time to start
                
        except Exception as e:
            print(f"Warning: Could not start mutt GUI: {e}")
            # Fallback to headless mode
            
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up mutt process."""
        if self.mutt_process:
            try:
                self.mutt_process.terminate()
                self.mutt_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.mutt_process.kill()
            except:
                pass
    
    def _exec(self, cmd: str) -> str:
        """Execute a command and return its output."""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                env={**os.environ, "DISPLAY": self.display}
            )
            return result.stdout
        except Exception as e:
            return f"Error: {e}"
    
    def screenshot(self) -> str:
        """Take a screenshot of the mutt interface using ImageMagick."""
        try:
            # Use import command to capture the xterm window with mutt
            cmd = (
                f"export DISPLAY={self.display} && "
                f"import -window root png:- | base64 -w 0"
            )
            
            return self._exec(cmd)
        except Exception as e:
            # Fallback: return a placeholder indicating mutt is running
            import base64
            placeholder = "mutt email client running in terminal"
            return base64.b64encode(placeholder.encode()).decode()
    
    def click(self, x: int, y: int, button: str = "left") -> None:
        """Simulate mouse click using xdotool."""
        button_map = {"left": 1, "middle": 2, "right": 3}
        b = button_map.get(button, 1)
        self._exec(f"DISPLAY={self.display} xdotool mousemove {x} {y} click {b}")
    
    def double_click(self, x: int, y: int) -> None:
        """Simulate double mouse click."""
        self._exec(
            f"DISPLAY={self.display} xdotool mousemove {x} {y} click --repeat 2 1"
        )
    
    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        """Simulate scrolling in the mutt interface."""
        self._exec(f"DISPLAY={self.display} xdotool mousemove {x} {y}")
        clicks = abs(scroll_y)
        button = 4 if scroll_y < 0 else 5
        for _ in range(clicks):
            self._exec(f"DISPLAY={self.display} xdotool click {button}")
    
    def type(self, text: str) -> None:
        """Type text into mutt interface."""
        # Escape single quotes in the user text
        safe_text = text.replace("'", "'\\\\''")
        # Send text to the focused window (mutt)
        cmd = f"DISPLAY={self.display} xdotool type -- '{safe_text}'"
        self._exec(cmd)
    
    def wait(self, ms: int = 1000) -> None:
        """Wait for specified milliseconds."""
        time.sleep(ms / 1000)
    
    def move(self, x: int, y: int) -> None:
        """Move mouse cursor to specified position."""
        self._exec(f"DISPLAY={self.display} xdotool mousemove {x} {y}")
    
    def keypress(self, keys: List[str]) -> None:
        """Send key combinations to mutt."""
        # Map common keys to xdotool format
        key_map = {
            "enter": "Return",
            "esc": "Escape",
            "tab": "Tab",
            "space": "space",
            "backspace": "BackSpace",
            "delete": "Delete",
            "ctrl": "ctrl",
            "alt": "alt",
            "shift": "shift",
            "up": "Up",
            "down": "Down",
            "left": "Left", 
            "right": "Right",
            "home": "Home",
            "end": "End",
            "pageup": "Page_Up",
            "pagedown": "Page_Down"
        }
        
        # Convert keys to xdotool format
        mapped_keys = []
        for key in keys:
            mapped_key = key_map.get(key.lower(), key.lower())
            mapped_keys.append(mapped_key)
        
        # Join keys with + for key combinations
        key_combination = "+".join(mapped_keys)
        self._exec(f"DISPLAY={self.display} xdotool key {key_combination}")
    
    def drag(self, path: List[Dict[str, int]]) -> None:
        """Simulate mouse drag operation."""
        if not path or len(path) < 2:
            return
            
        start = path[0]
        end = path[-1]
        
        # Move to start position and press mouse button
        self._exec(f"DISPLAY={self.display} xdotool mousemove {start['x']} {start['y']}")
        self._exec(f"DISPLAY={self.display} xdotool mousedown 1")
        
        # Drag through intermediate points
        for point in path[1:]:
            self._exec(f"DISPLAY={self.display} xdotool mousemove {point['x']} {point['y']}")
            time.sleep(0.1)  # Small delay for smooth dragging
        
        # Release mouse button
        self._exec(f"DISPLAY={self.display} xdotool mouseup 1")
    
    def get_current_url(self) -> str:
        """Get current 'location' in mutt (inbox, folder, etc.)."""
        # For mutt, this could represent the current folder or mailbox
        # Since mutt doesn't have URLs, we'll return a descriptive string
        return "mutt://localhost/inbox"
    
    # Additional mutt-specific methods that could be useful
    
    def send_mutt_command(self, command: str) -> str:
        """Send a command directly to mutt via key sequence."""
        # This could be used to send mutt-specific commands like:
        # 'q' to quit, 'c' to compose, 'r' to reply, etc.
        self.type(command)
        return f"Sent command '{command}' to mutt"
    
    def compose_email(self, to: str = "", subject: str = "", body: str = "") -> None:
        """Helper method to compose an email in mutt."""
        # Press 'c' to compose new email
        self.keypress(['c'])
        self.wait(500)
        
        # Enter recipient if provided
        if to:
            self.type(to)
        self.keypress(['enter'])
        self.wait(200)
        
        # Enter subject if provided  
        if subject:
            self.type(subject)
        self.keypress(['enter'])
        self.wait(200)
        
        # Enter body if provided
        if body:
            self.type(body)
    
    def quit_mutt(self) -> None:
        """Quit mutt application."""
        self.keypress(['q'])
        self.wait(500)
        # Confirm quit if prompted
        self.keypress(['y'])