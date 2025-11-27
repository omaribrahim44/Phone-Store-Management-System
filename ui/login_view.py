# ui/login_view.py
"""
Login Screen for Phone Management System
Provides authentication before accessing the main application
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from controllers.auth_controller import AuthController


class LoginWindow:
    """Login window for user authentication"""
    
    def __init__(self, on_success_callback):
        """
        Initialize login window.
        
        Args:
            on_success_callback: Function to call after successful login
        """
        self.on_success_callback = on_success_callback
        self.login_attempts = 0
        self.max_attempts = 5
        
        # Create window
        self.window = tb.Window(themename="cosmo")
        self.window.title("Phone Management System - Login")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"500x600+{x}+{y}")
        
        self.create_ui()
        
        # Bind Enter key to login
        self.window.bind('<Return>', lambda e: self.attempt_login())
    
    def create_ui(self):
        """Create login UI"""
        # Main container
        main_frame = tb.Frame(self.window, padding=40)
        main_frame.pack(fill="both", expand=True)
        
        # Logo/Header section
        header_frame = tb.Frame(main_frame)
        header_frame.pack(pady=(0, 30))
        
        # App title
        tb.Label(
            header_frame,
            text="📱 Phone Management System",
            font=("Segoe UI", 24, "bold"),
            bootstyle="primary"
        ).pack()
        
        tb.Label(
            header_frame,
            text="Please login to continue",
            font=("Segoe UI", 11),
            bootstyle="secondary"
        ).pack(pady=(10, 0))
        
        # Login form card
        form_card = tb.Labelframe(
            main_frame,
            text="Login",
            padding=30,
            bootstyle="primary"
        )
        form_card.pack(fill="both", expand=True, pady=20)
        
        # Username field
        tb.Label(
            form_card,
            text="Username:",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.username_entry = tb.Entry(
            form_card,
            font=("Segoe UI", 12),
            width=30
        )
        self.username_entry.pack(fill="x", pady=(0, 20))
        self.username_entry.focus()
        
        # Password field
        tb.Label(
            form_card,
            text="Password:",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.password_entry = tb.Entry(
            form_card,
            font=("Segoe UI", 12),
            show="●",
            width=30
        )
        self.password_entry.pack(fill="x", pady=(0, 10))
        
        # Show password checkbox
        self.show_password_var = tb.BooleanVar(value=False)
        show_pass_check = tb.Checkbutton(
            form_card,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            bootstyle="secondary-round-toggle"
        )
        show_pass_check.pack(anchor="w", pady=(0, 20))
        
        # Login button
        self.login_btn = tb.Button(
            form_card,
            text="🔐 Login",
            command=self.attempt_login,
            bootstyle="primary",
            width=20
        )
        self.login_btn.pack(pady=(10, 0), ipady=10)
        
        # Status label
        self.status_label = tb.Label(
            form_card,
            text="",
            font=("Segoe UI", 9),
            bootstyle="danger"
        )
        self.status_label.pack(pady=(15, 0))
        
        # Footer
        footer_frame = tb.Frame(main_frame)
        footer_frame.pack(side="bottom", pady=(20, 0))
        
        tb.Label(
            footer_frame,
            text="Default credentials: admin / admin",
            font=("Segoe UI", 9),
            bootstyle="info"
        ).pack()
        
        tb.Label(
            footer_frame,
            text="⚠️ Change password after first login",
            font=("Segoe UI", 8),
            bootstyle="warning"
        ).pack(pady=(2, 0))
        
        tb.Label(
            footer_frame,
            text="© 2025 Phone Management System",
            font=("Segoe UI", 8),
            bootstyle="secondary"
        ).pack(pady=(5, 0))
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="●")
    
    def attempt_login(self):
        """Attempt to log in with provided credentials"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate inputs
        if not username:
            self.status_label.configure(text="⚠️ Please enter username")
            self.username_entry.focus()
            return
        
        if not password:
            self.status_label.configure(text="⚠️ Please enter password")
            self.password_entry.focus()
            return
        
        # Check max attempts
        if self.login_attempts >= self.max_attempts:
            messagebox.showerror(
                "Too Many Attempts",
                f"Maximum login attempts ({self.max_attempts}) exceeded.\n\n"
                "Please restart the application."
            )
            self.window.quit()
            return
        
        # Disable button during login
        self.login_btn.configure(state="disabled", text="Logging in...")
        self.status_label.configure(text="")
        self.window.update()
        
        # Attempt authentication
        try:
            user = AuthController.login(username, password)
            
            if user:
                # Login successful
                self.status_label.configure(
                    text="✓ Login successful!",
                    bootstyle="success"
                )
                self.window.update()
                
                # Close login window and call success callback
                self.window.after(500, self.on_login_success)
            else:
                # Login failed
                self.login_attempts += 1
                remaining = self.max_attempts - self.login_attempts
                
                self.status_label.configure(
                    text=f"✗ Invalid credentials. {remaining} attempts remaining.",
                    bootstyle="danger"
                )
                
                # Clear password
                self.password_entry.delete(0, 'end')
                self.password_entry.focus()
                
                # Re-enable button
                self.login_btn.configure(state="normal", text="🔐 Login")
                
        except Exception as e:
            messagebox.showerror("Login Error", f"An error occurred during login:\n\n{str(e)}")
            self.login_btn.configure(state="normal", text="🔐 Login")
    
    def on_login_success(self):
        """Handle successful login"""
        # Withdraw (hide) the login window
        self.window.withdraw()
        
        # Schedule the callback and window destruction
        if self.on_success_callback:
            # Call the success callback after a short delay
            self.window.after(100, self._complete_login)
    
    def _complete_login(self):
        """Complete the login process"""
        try:
            # Call the success callback
            if self.on_success_callback:
                self.on_success_callback()
        except Exception as e:
            print(f"Error starting main app: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Destroy the login window
            try:
                self.window.quit()
                self.window.destroy()
            except:
                pass
    
    def run(self):
        """Run the login window"""
        self.window.mainloop()


def show_login(on_success_callback):
    """
    Show login window and wait for successful authentication.
    
    Args:
        on_success_callback: Function to call after successful login
    """
    login_window = LoginWindow(on_success_callback)
    login_window.run()
