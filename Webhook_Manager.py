import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
from requests.auth import HTTPBasicAuth
import json
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class WebhookManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.api_key = ''
        self.list_id = ''
        self.base_url = 'https://api.createsend.com/api/v3.3'
        self.url_list_webhooks = ''
        self.url_create_webhook = ''
        self.headers = {
            'Content-Type': 'application/json',
        }
        self.webhooks = []
        self.create_widgets()

    def create_widgets(self):
        self.title("Webhook Manager")
        self.geometry("800x600")

        # API Key
        self.api_key_label = ctk.CTkLabel(self, text="API Key:")
        self.api_key_label.pack(pady=(10, 0))
        self.api_key_entry = ctk.CTkEntry(self)
        self.api_key_entry.pack(pady=(0, 10))

        # List ID
        self.list_id_label = ctk.CTkLabel(self, text="List ID:")
        self.list_id_label.pack(pady=(10, 0))
        self.list_id_entry = ctk.CTkEntry(self)
        self.list_id_entry.pack(pady=(0, 10))

        # Apply Button
        self.apply_button = ctk.CTkButton(self, text="Apply Settings", command=self.apply_settings)
        self.apply_button.pack(pady=(10, 20))

        # Frame for Listbox and Buttons
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Listbox
        self.listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.refresh_button = ctk.CTkButton(button_frame, text="Refresh Webhooks", command=self.refresh_webhooks)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        self.create_button = ctk.CTkButton(button_frame, text="Create Webhook", command=self.prompt_create_webhook)
        self.create_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ctk.CTkButton(button_frame, text="Delete Selected Webhook", command=self.delete_selected_webhook)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.activate_button = ctk.CTkButton(button_frame, text="Activate Selected Webhook", command=self.activate_selected_webhook)
        self.activate_button.pack(side=tk.LEFT, padx=5)

        self.deactivate_button = ctk.CTkButton(button_frame, text="Deactivate Selected Webhook", command=self.deactivate_selected_webhook)
        self.deactivate_button.pack(side=tk.LEFT, padx=5)

        # Details Textbox
        self.details_label = ctk.CTkLabel(self, text="Webhook Details:")
        self.details_label.pack(pady=(20, 0))
        self.details_textbox = ctk.CTkTextbox(self, height=150)
        self.details_textbox.pack(fill=tk.BOTH, padx=10, pady=10)

    def apply_settings(self):
        self.api_key = self.api_key_entry.get()
        self.list_id = self.list_id_entry.get()
        self.url_list_webhooks = f'{self.base_url}/lists/{self.list_id}/webhooks.json'
        self.url_create_webhook = f'{self.base_url}/lists/{self.list_id}/webhooks.json'
        self.refresh_webhooks()

    def fetch_webhooks(self):
        try:
            response = requests.get(self.url_list_webhooks, auth=HTTPBasicAuth(self.api_key, ''), headers=self.headers)
            response.raise_for_status()
            webhooks = response.json()
            return webhooks
        except requests.RequestException as e:
            logging.error(f'Failed to fetch webhooks: {e}')
            messagebox.showerror("Error", f'Failed to fetch webhooks: {e}')
            return []

    def create_webhook(self, url):
        webhook_data = {
            "Events": [
                "Subscribe",
                "Deactivate"
            ],
            "Url": url,
            "PayloadFormat": "json"
        }
        try:
            response = requests.post(self.url_create_webhook, auth=HTTPBasicAuth(self.api_key, ''), headers=self.headers, data=json.dumps(webhook_data))
            response.raise_for_status()
            messagebox.showinfo("Success", "Webhook created successfully")
        except requests.RequestException as e:
            logging.error(f'Failed to create webhook: {e}')
            messagebox.showerror("Error", f'Failed to create webhook: {e}')

    def delete_webhook(self, webhook_id):
        delete_url = f'{self.base_url}/lists/{self.list_id}/webhooks/{webhook_id}.json'
        try:
            response = requests.delete(delete_url, auth=HTTPBasicAuth(self.api_key, ''), headers=self.headers)
            response.raise_for_status()
            messagebox.showinfo("Success", "Webhook deleted successfully")
        except requests.RequestException as e:
            logging.error(f'Failed to delete webhook: {e}')
            messagebox.showerror("Error", f'Failed to delete webhook: {e}')

    def update_webhook_status(self, webhook_id, status):
        update_url = f'{self.base_url}/lists/{self.list_id}/webhooks/{webhook_id}/{"activate" if status else "deactivate"}.json'
        try:
            response = requests.put(update_url, auth=HTTPBasicAuth(self.api_key, ''), headers=self.headers)
            response.raise_for_status()
            messagebox.showinfo("Success", f"Webhook {'activated' if status else 'deactivated'} successfully")
        except requests.RequestException as e:
            logging.error(f'Failed to update webhook status: {e}')
            messagebox.showerror("Error", f'Failed to update webhook status: {e}')

    def refresh_webhooks(self):
        self.webhooks = self.fetch_webhooks()
        self.listbox.delete(0, tk.END)
        for webhook in self.webhooks:
            status = "Active" if webhook.get("Active") else "Inactive"
            self.listbox.insert(tk.END, f"{webhook['WebhookID']}: {webhook['Url']} - {status}")

    def prompt_create_webhook(self):
        url = simpledialog.askstring("Create Webhook", "Enter the webhook URL:")
        if url:
            self.create_webhook(url)
            self.refresh_webhooks()

    def delete_selected_webhook(self):
        selected = self.listbox.curselection()
        if selected:
            webhook_id = self.webhooks[selected[0]]['WebhookID']
            self.delete_webhook(webhook_id)
            self.refresh_webhooks()
        else:
            messagebox.showwarning("Warning", "No webhook selected")

    def activate_selected_webhook(self):
        selected = self.listbox.curselection()
        if selected:
            webhook_id = self.webhooks[selected[0]]['WebhookID']
            self.update_webhook_status(webhook_id, True)
            self.refresh_webhooks()
        else:
            messagebox.showwarning("Warning", "No webhook selected")

    def deactivate_selected_webhook(self):
        selected = self.listbox.curselection()
        if selected:
            webhook_id = self.webhooks[selected[0]]['WebhookID']
            self.update_webhook_status(webhook_id, False)
            self.refresh_webhooks()
        else:
            messagebox.showwarning("Warning", "No webhook selected")

    def on_select(self, event):
        selected = self.listbox.curselection()
        if selected:
            webhook_id = self.webhooks[selected[0]]['WebhookID']
            webhook_details = self.fetch_webhook_details(webhook_id)
            self.details_textbox.delete(1.0, tk.END)
            self.details_textbox.insert(tk.END, json.dumps(webhook_details, indent=4))
        else:
            self.details_textbox.delete(1.0, tk.END)

    def fetch_webhook_details(self, webhook_id):
        details_url = f'{self.base_url}/lists/{self.list_id}/webhooks/{webhook_id}.json'
        try:
            response = requests.get(details_url, auth=HTTPBasicAuth(self.api_key, ''), headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f'Failed to fetch webhook details: {e}')
            messagebox.showerror("Error", f'Failed to fetch webhook details: {e}')
            return {}

if __name__ == "__main__":
    app = WebhookManager()
    app.mainloop()
