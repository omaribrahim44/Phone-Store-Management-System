# ui/users_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, simpledialog
from modules import models
from datetime import datetime

get_all_users = getattr(models, "get_all_users", None)
add_user = getattr(models, "add_user", None)
delete_user_by_id = getattr(models, "delete_user_by_id", None)
update_user_password = getattr(models, "update_user_password", None)

def safe_call(fn, *a, **kw):
    if fn is None:
        raise RuntimeError("Required function missing in modules.models")
    return fn(*a, **kw)

class UsersFrame:
    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=20)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)  # Make user list expandable
        
        self.all_users = []  # Store all users for filtering
        
        # ===== HEADER SECTION =====
        header = tb.Frame(self.frame)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.columnconfigure(1, weight=1)
        
        # Title
        tb.Label(
            header, 
            text="👥 User Management", 
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        ).grid(row=0, column=0, sticky="w")
        
        # Statistics Cards
        stats_frame = tb.Frame(header)
        stats_frame.grid(row=0, column=1, sticky="e")
        
        self.total_users_var = tb.StringVar(value="0")
        self.admin_count_var = tb.StringVar(value="0")
        self.active_users_var = tb.StringVar(value="0")
        
        self._create_stat_card(stats_frame, "Total Users", self.total_users_var, "info", 0)
        self._create_stat_card(stats_frame, "Admins", self.admin_count_var, "danger", 1)
        self._create_stat_card(stats_frame, "Staff", self.active_users_var, "success", 2)
        
        # ===== ADD USER CARD =====
        add_user_card = tb.Labelframe(
            self.frame, 
            text="  ➕ Create New User  ",
            bootstyle="primary",
            padding=20
        )
        add_user_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Form layout
        form_frame = tb.Frame(add_user_card)
        form_frame.pack(fill="x")
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        
        # Username
        tb.Label(
            form_frame, 
            text="Username:", 
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=8)
        
        self.u_user = tb.Entry(form_frame, width=25, font=("Segoe UI", 10))
        self.u_user.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=8)
        
        # Password
        tb.Label(
            form_frame, 
            text="Password:", 
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=2, sticky="w", padx=(0, 10), pady=8)
        
        password_frame = tb.Frame(form_frame)
        password_frame.grid(row=0, column=3, sticky="ew", pady=8)
        password_frame.columnconfigure(0, weight=1)
        
        self.u_pass = tb.Entry(password_frame, show="●", font=("Segoe UI", 10))
        self.u_pass.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.show_password = False
        self.toggle_btn = tb.Button(
            password_frame, 
            text="👁", 
            width=3,
            bootstyle="secondary-outline",
            command=self.toggle_password_visibility
        )
        self.toggle_btn.grid(row=0, column=1)
        
        # Role
        tb.Label(
            form_frame, 
            text="Role:", 
            font=("Segoe UI", 10, "bold")
        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=8)
        
        self.u_role = tb.Combobox(
            form_frame, 
            values=["Admin", "Cashier", "Technician"], 
            state="readonly",
            font=("Segoe UI", 10),
            width=23
        )
        self.u_role.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=8)
        self.u_role.set("Cashier")  # Default value
        
        # Full Name (optional)
        tb.Label(
            form_frame, 
            text="Full Name:", 
            font=("Segoe UI", 10, "bold")
        ).grid(row=1, column=2, sticky="w", padx=(0, 10), pady=8)
        
        self.u_fullname = tb.Entry(form_frame, width=25, font=("Segoe UI", 10))
        self.u_fullname.grid(row=1, column=3, sticky="ew", pady=8)
        
        # Create button
        btn_frame = tb.Frame(add_user_card)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        tb.Button(
            btn_frame, 
            text="✓  Create User", 
            bootstyle="success",
            command=self.create_user,
            width=20
        ).pack(side="right")
        
        tb.Button(
            btn_frame, 
            text="Clear", 
            bootstyle="secondary-outline",
            command=self.clear_form,
            width=15
        ).pack(side="right", padx=(0, 10))
        
        # ===== USER LIST CARD =====
        list_card = tb.Labelframe(
            self.frame, 
            text="  📋 User List  ",
            bootstyle="info",
            padding=15
        )
        list_card.grid(row=2, column=0, sticky="nsew")
        list_card.columnconfigure(0, weight=1)
        list_card.rowconfigure(1, weight=1)
        
        # Search and filter bar
        search_frame = tb.Frame(list_card)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        search_frame.columnconfigure(1, weight=1)
        
        tb.Label(
            search_frame, 
            text="🔍", 
            font=("Segoe UI", 12)
        ).grid(row=0, column=0, padx=(0, 8))
        
        self.search_var = tb.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_users())
        
        search_entry = tb.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            width=30
        )
        search_entry.grid(row=0, column=1, sticky="w", padx=(0, 15))
        search_entry.insert(0, "Search by username or role...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, "end") if search_entry.get() == "Search by username or role..." else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "Search by username or role...") if search_entry.get() == "" else None)
        
        # Filter by role
        tb.Label(
            search_frame, 
            text="Filter by Role:", 
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=2, padx=(20, 10))
        
        self.filter_role = tb.Combobox(
            search_frame,
            values=["All", "Admin", "Cashier", "Technician"],
            state="readonly",
            width=15,
            font=("Segoe UI", 10)
        )
        self.filter_role.set("All")
        self.filter_role.grid(row=0, column=3)
        self.filter_role.bind("<<ComboboxSelected>>", lambda e: self.filter_users())
        
        # Action buttons
        tb.Button(
            search_frame,
            text="🔄 Refresh",
            bootstyle="info-outline",
            command=self.refresh
        ).grid(row=0, column=4, padx=(15, 0))
        
        # Users table
        table_frame = tb.Frame(list_card)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        cols = ("id", "username", "full_name", "role", "created_at", "actions")
        self.tree = ttk.Treeview(
            table_frame, 
            columns=cols, 
            show="headings", 
            height=15
        )
        
        # Column configuration
        widths = {"id": 50, "username": 180, "full_name": 220, "role": 120, "created_at": 180, "actions": 200}
        labels = {"id": "ID", "username": "👤 Username", "full_name": "📝 Full Name", "role": "🎭 Role", "created_at": "📅 Created At", "actions": "⚙️ Actions"}
        alignments = {"id": "center", "username": "w", "full_name": "w", "role": "center", "created_at": "center", "actions": "center"}
        
        for c in cols:
            self.tree.heading(c, text=labels.get(c, c))
            self.tree.column(c, width=widths.get(c, 120), anchor=alignments.get(c, "w"))
        
        # Alternating row colors
        self.tree.tag_configure("oddrow", background="#f8f9fa")
        self.tree.tag_configure("evenrow", background="white")
        self.tree.tag_configure("admin", foreground="#dc3545", font=("Segoe UI", 10, "bold"))
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=hsb.set)
        
        # Bind double-click to edit
        self.tree.bind("<Double-Button-1>", self.on_row_double_click)
        
        # Action buttons frame
        actions_frame = tb.Frame(list_card)
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        
        tb.Label(
            actions_frame,
            text="Selected User Actions:",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 15))
        
        tb.Button(
            actions_frame, 
            text="🔑 Reset Password", 
            bootstyle="warning",
            command=self.reset_selected_password
        ).pack(side="left", padx=5)
        
        tb.Button(
            actions_frame, 
            text="✏️ Edit User", 
            bootstyle="info",
            command=self.edit_selected_user
        ).pack(side="left", padx=5)
        
        tb.Button(
            actions_frame, 
            text="🗑️ Delete User", 
            bootstyle="danger",
            command=self.delete_selected
        ).pack(side="left", padx=5)
        
        # Initial load
        self.refresh()

    def _create_stat_card(self, parent, label, var, color, column):
        """Helper to create statistic cards"""
        card = tb.Frame(parent, bootstyle=color)
        card.grid(row=0, column=column, padx=8)
        
        tb.Label(
            card,
            textvariable=var,
            font=("Segoe UI", 20, "bold"),
            bootstyle=f"{color}"
        ).pack(padx=15, pady=(10, 0))
        
        tb.Label(
            card,
            text=label,
            font=("Segoe UI", 9),
            bootstyle=f"{color}"
        ).pack(padx=15, pady=(0, 10))

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        self.show_password = not self.show_password
        if self.show_password:
            self.u_pass.configure(show="")
            self.toggle_btn.configure(text="🙈")
        else:
            self.u_pass.configure(show="●")
            self.toggle_btn.configure(text="👁")

    def clear_form(self):
        """Clear all form fields"""
        self.u_user.delete(0, "end")
        self.u_pass.delete(0, "end")
        self.u_fullname.delete(0, "end")
        self.u_role.set("Cashier")

    def refresh(self):
        """Refresh user list and statistics"""
        try:
            self.all_users = safe_call(get_all_users)
            self.update_statistics()
            self.filter_users()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")

    def update_statistics(self):
        """Update user statistics"""
        total = len(self.all_users)
        admin_count = sum(1 for u in self.all_users if u[3] == "Admin")
        staff_count = total - admin_count
        
        self.total_users_var.set(str(total))
        self.admin_count_var.set(str(admin_count))
        self.active_users_var.set(str(staff_count))

    def filter_users(self):
        """Filter users based on search and role filter"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filter values
        search_text = self.search_var.get().lower()
        if search_text == "search by username or role...":
            search_text = ""
        
        role_filter = self.filter_role.get()
        
        # Filter and display users
        row_num = 0
        for user in self.all_users:
            user_id, username, full_name, role, created_at = user
            
            # Apply filters
            if search_text and search_text not in username.lower() and search_text not in role.lower():
                continue
            
            if role_filter != "All" and role != role_filter:
                continue
            
            # Format created_at
            try:
                if created_at and len(created_at) > 10:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_at = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
            
            # Add action placeholder
            actions = "Double-click to edit"
            
            # Insert with alternating colors
            tag = "evenrow" if row_num % 2 == 0 else "oddrow"
            if role == "Admin":
                tag = "admin"
            
            self.tree.insert(
                "", 
                "end", 
                values=(user_id, username, full_name or "-", role, created_at, actions),
                tags=(tag,)
            )
            row_num += 1

    def create_user(self):
        """Create a new user"""
        username = self.u_user.get().strip()
        password = self.u_pass.get().strip()
        fullname = self.u_fullname.get().strip()
        role = self.u_role.get().strip() or "Cashier"
        
        # Validation
        if not username:
            messagebox.showerror("Validation Error", "Username is required!")
            self.u_user.focus()
            return
        
        if len(username) < 3:
            messagebox.showerror("Validation Error", "Username must be at least 3 characters long!")
            self.u_user.focus()
            return
        
        if not password:
            messagebox.showerror("Validation Error", "Password is required!")
            self.u_pass.focus()
            return
        
        if len(password) < 4:
            messagebox.showerror("Validation Error", "Password must be at least 4 characters long!")
            self.u_pass.focus()
            return
        
        try:
            safe_call(add_user, username, password, fullname, role)
            messagebox.showinfo(
                "Success", 
                f"✓ User '{username}' created successfully!\nRole: {role}"
            )
            self.clear_form()
            self.refresh()
        except Exception as e:
            messagebox.showerror("Failed", f"Failed to create user:\n{str(e)}")

    def delete_selected(self):
        """Delete selected user"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user to delete!")
            return
        
        user_data = self.tree.item(sel[0])['values']
        user_id = user_data[0]
        username = user_data[1]
        
        if messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete user:\n\n👤 {username}\n\nThis action cannot be undone!"
        ):
            try:
                safe_call(delete_user_by_id, user_id)
                messagebox.showinfo("Success", f"✓ User '{username}' deleted successfully!")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Failed", f"Failed to delete user:\n{str(e)}")

    def reset_selected_password(self):
        """Reset password for selected user"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user to reset password!")
            return
        
        user_data = self.tree.item(sel[0])['values']
        user_id = user_data[0]
        username = user_data[1]
        
        # Create custom dialog for password reset
        dialog = tb.Toplevel(title=f"Reset Password - {username}")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self.frame.winfo_toplevel())
        dialog.grab_set()
        
        tb.Label(
            dialog,
            text=f"Reset Password for: {username}",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(20, 10))
        
        tb.Label(
            dialog,
            text="New Password:",
            font=("Segoe UI", 10)
        ).pack(pady=(10, 5))
        
        pw_entry = tb.Entry(dialog, show="●", font=("Segoe UI", 11), width=30)
        pw_entry.pack(pady=5)
        pw_entry.focus()
        
        tb.Label(
            dialog,
            text="Confirm Password:",
            font=("Segoe UI", 10)
        ).pack(pady=(10, 5))
        
        pw_confirm_entry = tb.Entry(dialog, show="●", font=("Segoe UI", 11), width=30)
        pw_confirm_entry.pack(pady=5)
        
        def do_reset():
            new_pw = pw_entry.get().strip()
            confirm_pw = pw_confirm_entry.get().strip()
            
            if not new_pw:
                messagebox.showerror("Error", "Password cannot be empty!")
                return
            
            if len(new_pw) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters long!")
                return
            
            if new_pw != confirm_pw:
                messagebox.showerror("Error", "Passwords do not match!")
                return
            
            try:
                safe_call(update_user_password, user_id, new_pw)
                messagebox.showinfo("Success", f"✓ Password updated for '{username}'!")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Failed", f"Failed to update password:\n{str(e)}")
        
        btn_frame = tb.Frame(dialog)
        btn_frame.pack(pady=(15, 10))
        
        tb.Button(
            btn_frame,
            text="✓ Reset Password",
            bootstyle="success",
            command=do_reset
        ).pack(side="left", padx=5)
        
        tb.Button(
            btn_frame,
            text="Cancel",
            bootstyle="secondary",
            command=dialog.destroy
        ).pack(side="left", padx=5)
        
        # Bind Enter key
        pw_entry.bind("<Return>", lambda e: pw_confirm_entry.focus())
        pw_confirm_entry.bind("<Return>", lambda e: do_reset())

    def edit_selected_user(self):
        """Edit selected user (currently just shows info)"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user to edit!")
            return
        
        user_data = self.tree.item(sel[0])['values']
        user_id, username, full_name, role, created_at = user_data[:5]
        
        messagebox.showinfo(
            "User Information",
            f"ID: {user_id}\n"
            f"Username: {username}\n"
            f"Full Name: {full_name}\n"
            f"Role: {role}\n"
            f"Created: {created_at}\n\n"
            f"Use 'Reset Password' to change password."
        )

    def on_row_double_click(self, event):
        """Handle double-click on row"""
        self.edit_selected_user()
