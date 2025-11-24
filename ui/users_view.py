# ui/users_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, simpledialog
from modules import models

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
        self.frame = tb.Frame(parent, padding=12)
        self.frame.columnconfigure(0, weight=1)

        top = tb.Frame(self.frame); top.grid(row=0, column=0, sticky="ew", pady=(0,8))
        top.columnconfigure(1, weight=1)
        tb.Label(top, text="Username").grid(row=0, column=0, sticky="w"); self.u_user = tb.Entry(top); self.u_user.grid(row=0, column=1, sticky="ew", padx=6)
        tb.Label(top, text="Password").grid(row=0, column=2, sticky="w"); self.u_pass = tb.Entry(top, show="*"); self.u_pass.grid(row=0, column=3, sticky="w", padx=6)
        tb.Label(top, text="Role").grid(row=1, column=0, sticky="w"); self.u_role = tb.Combobox(top, values=["Admin","Cashier","Technician"], state="readonly"); self.u_role.grid(row=1, column=1, sticky="w", padx=6)
        tb.Button(top, text="Create User", bootstyle="success", command=self.create_user).grid(row=1, column=3, padx=6)

        # users table
        cols = ("id","username","full_name","role","created_at")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=12)
        widths = {"id":60,"username":160,"full_name":260,"role":120,"created_at":160}
        labels = {"id":"ID","username":"Username","full_name":"Full name","role":"Role","created_at":"Created"}
        alignments = {"id":"center","username":"w","full_name":"w","role":"center","created_at":"w"}
        for c in cols:
            self.tree.heading(c, text=labels.get(c,c))
            self.tree.column(c, width=widths.get(c,120), anchor=alignments.get(c,"w"))
        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview); vsb.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        footer = tb.Frame(self.frame); footer.grid(row=2, column=0, sticky="ew", pady=(6,0))
        tb.Button(footer, text="Refresh", bootstyle="primary", command=self.refresh).pack(side="left", padx=6)
        tb.Button(footer, text="Delete Selected", bootstyle="danger-outline", command=self.delete_selected).pack(side="left", padx=6)
        tb.Button(footer, text="Reset Password", bootstyle="warning-outline", command=self.reset_selected_password).pack(side="left", padx=6)

        self.refresh()

    def refresh(self):
        try:
            rows = safe_call(get_all_users)
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        for r in self.tree.get_children(): self.tree.delete(r)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def create_user(self):
        u = self.u_user.get().strip(); p = self.u_pass.get().strip(); role = self.u_role.get().strip() or "Cashier"
        if not u or not p:
            messagebox.showerror("Error","Username and password required"); return
        try:
            safe_call(add_user, u, p, "", role)
            messagebox.showinfo("OK","User created"); self.refresh()
        except Exception as e:
            messagebox.showerror("Failed", str(e))

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("No selection","Select a user"); return
        uid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm","Delete selected user?"):
            try:
                safe_call(delete_user_by_id, uid)
                messagebox.showinfo("Deleted","User removed"); self.refresh()
            except Exception as e:
                messagebox.showerror("Failed", str(e))

    def reset_selected_password(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("No selection","Select a user"); return
        uid = self.tree.item(sel[0])['values'][0]
        newpw = simpledialog.askstring("New password", "Enter new password:", show="*")
        if not newpw: return
        try:
            safe_call(update_user_password, uid, newpw)
            messagebox.showinfo("OK","Password updated")
        except Exception as e:
            messagebox.showerror("Failed", str(e))
