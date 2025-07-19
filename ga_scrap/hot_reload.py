"""
GA-Scrap Hot Reload Module
File watching and automatic reload functionality
"""

import asyncio
import sys
import importlib
import subprocess
import signal
import os
from pathlib import Path
from typing import Optional, Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from colorama import Fore, Style
import time

class HotReloader:
    """
    Hot reload functionality for GA-Scrap applications
    
    Features:
    - Watch Python files for changes
    - Automatically restart scraper on file changes
    - Configurable file patterns and directories
    - Graceful process management
    """
    
    def __init__(
        self,
        script_path: str,
        watch_dirs: List[str] = None,
        watch_patterns: List[str] = None,
        ignore_patterns: List[str] = None,
        debounce_delay: float = 1.0
    ):
        """
        Initialize Hot Reloader
        
        Args:
            script_path: Path to the main script to run
            watch_dirs: Directories to watch (default: current directory)
            watch_patterns: File patterns to watch (default: *.py)
            ignore_patterns: Patterns to ignore
            debounce_delay: Delay before restarting after file change
        """
        self.script_path = Path(script_path)
        self.watch_dirs = watch_dirs or [str(self.script_path.parent)]
        self.watch_patterns = watch_patterns or ["*.py"]
        self.ignore_patterns = ignore_patterns or ["__pycache__", "*.pyc", ".git"]
        self.debounce_delay = debounce_delay
        
        self.observer = Observer()
        self.process: Optional[subprocess.Popen] = None
        self.restart_pending = False
        self.last_restart_time = 0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n{Fore.YELLOW}🛑 Shutting down hot reloader...{Style.RESET_ALL}")
        self.stop()
        sys.exit(0)
    
    def _should_watch_file(self, file_path: str) -> bool:
        """Check if file should be watched based on patterns"""
        path = Path(file_path)
        
        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if pattern in str(path):
                return False
        
        # Check watch patterns
        for pattern in self.watch_patterns:
            if path.match(pattern):
                return True
        
        return False
    
    def _log(self, message: str, level: str = "info"):
        """Log message with color coding"""
        colors = {
            'info': Fore.CYAN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'success': Fore.GREEN,
            'debug': Fore.MAGENTA
        }
        
        color = colors.get(level, Fore.WHITE)
        timestamp = time.strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] [Hot Reload] {message}{Style.RESET_ALL}")
    
    def _start_process(self):
        """Start the main script process"""
        try:
            if self.process:
                self._stop_process()
            
            self._log(f"🚀 Starting: {self.script_path}", "info")
            
            # Start the process
            self.process = subprocess.Popen(
                [sys.executable, str(self.script_path)],
                cwd=self.script_path.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Start output monitoring in background
            asyncio.create_task(self._monitor_output())
            
        except Exception as e:
            self._log(f"❌ Failed to start process: {e}", "error")
    
    async def _monitor_output(self):
        """Monitor process output and display it"""
        if not self.process:
            return
        
        try:
            while self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    # Print output with prefix
                    print(f"{Fore.WHITE}[App] {line.rstrip()}{Style.RESET_ALL}")
                await asyncio.sleep(0.1)
        except Exception as e:
            self._log(f"Error monitoring output: {e}", "warning")
    
    def _stop_process(self):
        """Stop the current process"""
        if self.process:
            try:
                self._log("🛑 Stopping current process...", "warning")
                
                # Try graceful shutdown first
                self.process.terminate()
                
                # Wait a bit for graceful shutdown
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self._log("⚡ Force killing process...", "warning")
                    self.process.kill()
                    self.process.wait()
                
                self.process = None
                self._log("✅ Process stopped", "success")
                
            except Exception as e:
                self._log(f"Error stopping process: {e}", "error")
    
    async def _restart_with_delay(self):
        """Restart process after debounce delay"""
        if self.restart_pending:
            return
        
        self.restart_pending = True
        current_time = time.time()
        
        # Debounce: wait for delay period without new changes
        await asyncio.sleep(self.debounce_delay)
        
        # Check if another restart was triggered during delay
        if current_time < self.last_restart_time:
            self.restart_pending = False
            return
        
        self._log("🔄 Restarting application...", "info")
        self._start_process()
        self.restart_pending = False
        self.last_restart_time = time.time()
    
    def start(self):
        """Start hot reload monitoring"""
        self._log("🔥 Starting hot reload...", "success")
        self._log(f"📁 Watching directories: {', '.join(self.watch_dirs)}", "info")
        self._log(f"📄 Watching patterns: {', '.join(self.watch_patterns)}", "info")
        
        # Create file system event handler
        event_handler = HotReloadHandler(self)
        
        # Setup observers for each watch directory
        for watch_dir in self.watch_dirs:
            if Path(watch_dir).exists():
                self.observer.schedule(event_handler, watch_dir, recursive=True)
                self._log(f"👀 Watching: {watch_dir}", "info")
            else:
                self._log(f"⚠️  Directory not found: {watch_dir}", "warning")
        
        # Start file watching
        self.observer.start()
        
        # Start initial process
        self._start_process()
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop hot reload monitoring"""
        self._log("🛑 Stopping hot reload...", "info")
        
        # Stop file watching
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        
        # Stop current process
        self._stop_process()
        
        self._log("✅ Hot reload stopped", "success")

class HotReloadHandler(FileSystemEventHandler):
    """File system event handler for hot reload"""
    
    def __init__(self, reloader: HotReloader):
        self.reloader = reloader
        super().__init__()
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # Check if we should watch this file
        if not self.reloader._should_watch_file(file_path):
            return
        
        self.reloader._log(f"📝 File changed: {Path(file_path).name}", "info")
        
        # Trigger restart
        asyncio.create_task(self.reloader._restart_with_delay())

class DevServer:
    """
    Development server with hot reload for GA-Scrap apps
    """
    
    def __init__(self, app_dir: str):
        """
        Initialize development server
        
        Args:
            app_dir: Directory containing the GA-Scrap app
        """
        self.app_dir = Path(app_dir)
        self.main_script = self.app_dir / "main.py"
        
        if not self.main_script.exists():
            raise FileNotFoundError(f"main.py not found in {app_dir}")
    
    def start(self):
        """Start development server with hot reload"""
        print(f"{Fore.GREEN}🔥 GA-Scrap Dev Server{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📁 App Directory: {self.app_dir}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚀 Main Script: {self.main_script}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Edit your files and they will auto-reload!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Press Ctrl+C to stop{Style.RESET_ALL}")
        print("-" * 50)
        
        # Create hot reloader
        reloader = HotReloader(
            script_path=str(self.main_script),
            watch_dirs=[str(self.app_dir)],
            watch_patterns=["*.py", "*.yaml", "*.yml", "*.json"],
            debounce_delay=1.0
        )
        
        # Start hot reload
        reloader.start()

def run_with_hot_reload(script_path: str, watch_dirs: List[str] = None):
    """
    Convenience function to run a script with hot reload
    
    Args:
        script_path: Path to the script to run
        watch_dirs: Directories to watch for changes
    """
    reloader = HotReloader(
        script_path=script_path,
        watch_dirs=watch_dirs
    )
    reloader.start()
