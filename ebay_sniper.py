
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import webbrowser
import os


class EbaySniper:

    def __init__(self, root):

        self.root = root
        self.root.title("eBay Auction Monitor - Lesson 5")
        self.root.geometry("1150x650")

        self.auctions = []
        self.alerted_auctions = set()

        self.data_file = "auctions.json"

        self.create_interface()
        self.load_auctions()
        self.update_countdowns()

    # --------------------------------------------------
    # CREATE INTERFACE
    # --------------------------------------------------

    def create_interface(self):

        title = ttk.Label(
            self.root,
            text="eBay Auction Monitor",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        # Auction input area
        input_frame = ttk.LabelFrame(
            self.root,
            text="Add an auction"
        )
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            input_frame,
            text="eBay URL:"
        ).grid(row=0, column=0, padx=5, pady=5)

        self.url_entry = ttk.Entry(
            input_frame,
            width=75
        )
        self.url_entry.grid(
            row=0, column=1, padx=5, pady=5
        )

        ttk.Button(
            input_frame,
            text="Fetch Auction Details",
            command=self.fetch_auction
        ).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(
            input_frame,
            text="Maximum bid (£):"
        ).grid(row=1, column=0, padx=5, pady=5)

        self.max_bid_entry = ttk.Entry(
            input_frame,
            width=15
        )
        self.max_bid_entry.grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )

        self.details_label = ttk.Label(
            input_frame,
            text="Paste a listing URL and click Fetch Auction Details."
        )
        self.details_label.grid(
            row=2, column=0, columnspan=3,
            padx=5, pady=8, sticky="w"
        )

        ttk.Button(
            input_frame,
            text="Add Auction to Monitor",
            command=self.add_auction
        ).grid(
            row=3, column=1, sticky="w",
            padx=5, pady=8
        )

        # Auction table
        table_frame = ttk.LabelFrame(
            self.root,
            text="Your Auctions"
        )
        table_frame.pack(
            fill="both", expand=True,
            padx=10, pady=10
        )

        columns = (
            "name",
            "price",
            "maximum",
            "date",
            "time",
            "countdown",
            "status"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        headings = {
            "name": "Auction",
            "price": "Current Price",
            "maximum": "Maximum Bid",
            "date": "Ending Date",
            "time": "Ending Time",
            "countdown": "Time Remaining",
            "status": "Status"
        }

        widths = {
            "name": 260,
            "price": 100,
            "maximum": 100,
            "date": 110,
            "time": 100,
            "countdown": 130,
            "status": 120
        }

        for column in columns:

            self.table.heading(
                column,
                text=headings[column]
            )

            self.table.column(
                column,
                width=widths[column],
                anchor="center"
            )

        self.table.pack(
            fill="both", expand=True,
            padx=5, pady=5
        )

        self.table.tag_configure(
            "soon",
            background="#ffe0b2"
        )

        self.table.tag_configure(
            "finished",
            background="#eeeeee"
        )

        self.table.tag_configure(
            "waiting",
            background="#ffffff"
        )

        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Open Selected Auction",
            command=self.open_auction
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Refresh Selected Price",
            command=self.refresh_selected_price
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Remove Selected Auction",
            command=self.remove_auction
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Save Auctions",
            command=self.save_auctions
        ).pack(side="left", padx=5)

    # --------------------------------------------------
    # FETCH EBAY LISTING
    # --------------------------------------------------

    def fetch_auction(self):

        url = self.url_entry.get().strip()

        if not url:
            messagebox.showwarning(
                "Missing URL",
                "Please paste an eBay listing URL."
            )
            return

        if "ebay." not in url.lower():
            messagebox.showwarning(
                "Invalid URL",
                "Please enter an eBay listing URL."
            )
            return

        self.details_label.config(
            text="Fetching listing information..."
        )
        self.root.update_idletasks()

        try:

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/130.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-GB,en;q=0.9"
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=20
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            # Extract title
            title = self.extract_title(soup)

            # Extract current price
            price = self.extract_price(soup)

            # Extract ending date/time
            end_time = self.extract_end_time(
                soup,
                response.text
            )

            self.details_label.config(
                text=(
                    f"Title: {title}\n"
                    f"Current price: {price}\n"
                    f"Ending: {end_time}"
                )
            )

            self.fetched_title = title
            self.fetched_price = price
            self.fetched_end_time = end_time
            self.fetched_url = url

            messagebox.showinfo(
                "Auction Retrieved",
                "Auction information retrieved.\n\n"
                "Check the details before adding it."
            )

        except requests.exceptions.HTTPError as error:

            self.details_label.config(
                text="eBay rejected the request."
            )

            messagebox.showerror(
                "eBay Request Error",
                "eBay may have blocked the request.\n\n"
                f"{error}\n\n"
                "Try again later or enter the details manually."
            )

        except requests.exceptions.RequestException as error:

            self.details_label.config(
                text="Could not connect to eBay."
            )

            messagebox.showerror(
                "Connection Error",
                f"Could not retrieve the listing:\n\n{error}"
            )

        except Exception as error:

            self.details_label.config(
                text="Could not read auction information."
            )

            messagebox.showerror(
                "Error",
                f"Something went wrong:\n\n{error}"
            )

    # --------------------------------------------------
    # EXTRACT TITLE
    # --------------------------------------------------

    def extract_title(self, soup):

        # Try eBay page title
        element = soup.find(
            "meta",
            attrs={"property": "og:title"}
        )

        if element and element.get("content"):
            return element["content"].strip()

        # Try page title
        if soup.title:
            return soup.title.get_text(
                strip=True
            )

        return "eBay Auction"

    # --------------------------------------------------
    # EXTRACT PRICE
    # --------------------------------------------------

    def extract_price(self, soup):

        # Try common eBay price metadata
        selectors = [
            ("meta", {"itemprop": "price"}),
            ("meta", {"property": "product:price:amount"}),
            ("meta", {"property": "og:price:amount"})
        ]

        for tag_name, attributes in selectors:

            element = soup.find(
                tag_name,
                attrs=attributes
            )

            if element:

                price = (
                    element.get("content")
                    or element.get("value")
                )

                if price:
                    try:
                        return float(
                            re.sub(r"[^0-9.]", "", price)
                        )
                    except ValueError:
                        pass

        # Try JSON-LD structured data
        for script in soup.find_all(
            "script",
            type="application/ld+json"
        ):

            try:
                data = json.loads(
                    script.string or script.get_text()
                )

                price = self.find_price_in_json(data)

                if price is not None:
                    return price

            except Exception:
                continue

        # Try visible price text
        text = soup.get_text(" ", strip=True)

        match = re.search(
            r"£\s?([\d,]+(?:\.\d{2})?)",
            text
        )

        if match:

            return float(
                match.group(1).replace(",", "")
            )

        return None

    def find_price_in_json(self, data):

        if isinstance(data, dict):

            if "price" in data:

                try:
                    return float(
                        str(data["price"]).replace(",", "")
                    )
                except (ValueError, TypeError):
                    pass

            for value in data.values():

                result = self.find_price_in_json(value)

                if result is not None:
                    return result

        elif isinstance(data, list):

            for item in data:

                result = self.find_price_in_json(item)

                if result is not None:
                    return result

        return None

    # --------------------------------------------------
    # EXTRACT ENDING DATE AND TIME
    # --------------------------------------------------

    def extract_end_time(self, soup, html):

        # Look for common ending-time fields in page source
        patterns = [
            r'"itemEndDate"\s*:\s*"([^"]+)"',
            r'"endTime"\s*:\s*"([^"]+)"',
            r'"auctionEndTime"\s*:\s*"([^"]+)"',
            r'"endDate"\s*:\s*"([^"]+)"'
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                html,
                re.IGNORECASE
            )

            if match:

                result = self.parse_datetime(
                    match.group(1)
                )

                if result:
                    return result

        # Try JSON-LD
        for script in soup.find_all(
            "script",
            type="application/ld+json"
        ):

            try:

                data = json.loads(
                    script.string or script.get_text()
                )

                result = self.find_end_time_in_json(
                    data
                )

                if result:
                    return result

            except Exception:
                continue

        return None

    def find_end_time_in_json(self, data):

        if isinstance(data, dict):

            for key, value in data.items():

                if key.lower() in (
                    "itemenddate",
                    "endtime",
                    "auctionendtime",
                    "enddate"
                ):

                    result = self.parse_datetime(
                        str(value)
                    )

                    if result:
                        return result

            for value in data.values():

                result = self.find_end_time_in_json(
                    value
                )

                if result:
                    return result

        elif isinstance(data, list):

            for item in data:

                result = self.find_end_time_in_json(
                    item
                )

                if result:
                    return result

        return None

    def parse_datetime(self, value):

        value = value.strip()

        try:

            # ISO format, including timezone if supplied
            result = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )

            # Convert timezone-aware time to local time
            if result.tzinfo is not None:

                result = result.astimezone().replace(
                    tzinfo=None
                )

            return result

        except ValueError:
            return None

    # --------------------------------------------------
    # ADD AUCTION
    # --------------------------------------------------

    def add_auction(self):

        if not hasattr(self, "fetched_title"):

            messagebox.showwarning(
                "Fetch First",
                "Please fetch the auction details first."
            )
            return

        try:

            maximum_bid = float(
                self.max_bid_entry.get()
            )

            if maximum_bid <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Maximum Bid",
                "Enter a valid maximum bid."
            )
            return

        if self.fetched_end_time is None:

            messagebox.showwarning(
                "Ending Time Missing",
                "The ending time could not be retrieved.\n\n"
                "This auction cannot be monitored accurately "
                "until its ending time is available."
            )
            return

        auction = {
            "id": str(datetime.now().timestamp()),
            "name": self.fetched_title,
            "url": self.fetched_url,
            "current_price": self.fetched_price,
            "maximum_bid": maximum_bid,
            "end_time": self.fetched_end_time.isoformat()
        }

        self.auctions.append(auction)

        self.refresh_table()
        self.save_auctions()

        messagebox.showinfo(
            "Auction Added",
            "Auction added to your monitor."
        )

        # Clear input fields
        self.url_entry.delete(0, tk.END)
        self.max_bid_entry.delete(0, tk.END)

        self.details_label.config(
            text="Paste another eBay listing URL."
        )

        del self.fetched_title
        del self.fetched_price
        del self.fetched_end_time
        del self.fetched_url

    # --------------------------------------------------
    # REFRESH TABLE
    # --------------------------------------------------

    def refresh_table(self):

        selected = self.table.selection()

        current_ids = {
            auction["id"] for auction in self.auctions
        }

        # Remove deleted auctions
        for item_id in self.table.get_children():

            if item_id not in current_ids:
                self.table.delete(item_id)

        now = datetime.now()

        for auction in self.auctions:

            end_time = datetime.fromisoformat(
                auction["end_time"]
            )

            remaining = (
                end_time - now
            ).total_seconds()

            if remaining <= 0:

                countdown = "00:00:00"
                status = "Finished"
                tag = "finished"

            else:

                countdown = self.format_countdown(
                    remaining
                )

                if remaining <= 60:

                    status = "Ending Soon"
                    tag = "soon"

                else:

                    status = "Waiting"
                    tag = "waiting"

            current_price = auction.get(
                "current_price"
            )

            if current_price is None:
                price_text = "Unknown"
            else:
                price_text = f"£{current_price:.2f}"

            values = (
                auction["name"],
                price_text,
                f"£{auction['maximum_bid']:.2f}",
                end_time.strftime("%d/%m/%Y"),
                end_time.strftime("%H:%M:%S"),
                countdown,
                status
            )

            auction_id = auction["id"]

            if self.table.exists(auction_id):

                self.table.item(
                    auction_id,
                    values=values,
                    tags=(tag,)
                )

            else:

                self.table.insert(
                    "",
                    "end",
                    iid=auction_id,
                    values=values,
                    tags=(tag,)
                )

        # Restore selection
        for auction_id in selected:

            if self.table.exists(auction_id):
                self.table.selection_set(auction_id)

    # --------------------------------------------------
    # COUNTDOWN
    # --------------------------------------------------

    def format_countdown(self, seconds):

        seconds = int(seconds)

        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        if days > 0:

            return (
                f"{days}d {hours:02}:{minutes:02}:{seconds:02}"
            )

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def update_countdowns(self):

        now = datetime.now()

        for auction in self.auctions:

            end_time = datetime.fromisoformat(
                auction["end_time"]
            )

            remaining = (
                end_time - now
            ).total_seconds()

            if 0 < remaining <= 60:

                alert_id = (
                    auction["id"], 60
                )

                if alert_id not in self.alerted_auctions:

                    self.root.bell()

                    self.alerted_auctions.add(
                        alert_id
                    )

            if 0 < remaining <= 15:

                alert_id = (
                    auction["id"], 15
                )

                if alert_id not in self.alerted_auctions:

                    self.root.bell()

                    self.alerted_auctions.add(
                        alert_id
                    )

        self.refresh_table()

        self.root.after(
            1000,
            self.update_countdowns
        )

    # --------------------------------------------------
    # OPEN AUCTION
    # --------------------------------------------------

    def open_auction(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showwarning(
                "Select Auction",
                "Please select an auction first."
            )
            return

        auction_id = selected[0]

        for auction in self.auctions:

            if auction["id"] == auction_id:

                webbrowser.open(
                    auction["url"]
                )

                return

    # --------------------------------------------------
    # REFRESH SELECTED PRICE
    # --------------------------------------------------

    def refresh_selected_price(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showwarning(
                "Select Auction",
                "Please select an auction first."
            )
            return

        auction_id = selected[0]

        for auction in self.auctions:

            if auction["id"] == auction_id:

                try:

                    headers = {
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 Chrome/130.0.0.0 "
                            "Safari/537.36"
                        )
                    }

                    response = requests.get(
                        auction["url"],
                        headers=headers,
                        timeout=20
                    )

                    response.raise_for_status()

                    soup = BeautifulSoup(
                        response.text,
                        "html.parser"
                    )

                    price = self.extract_price(
                        soup
                    )

                    if price is None:

                        messagebox.showwarning(
                            "Price Not Found",
                            "Could not retrieve the current price."
                        )

                    else:

                        auction["current_price"] = price

                        self.refresh_table()
                        self.save_auctions()

                        messagebox.showinfo(
                            "Price Updated",
                            f"Current price: £{price:.2f}"
                        )

                except Exception as error:

                    messagebox.showerror(
                        "Refresh Failed",
                        str(error)
                    )

                return

    # --------------------------------------------------
    # REMOVE AUCTION
    # --------------------------------------------------

    def remove_auction(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showwarning(
                "Select Auction",
                "Please select an auction first."
            )
            return

        auction_id = selected[0]

        self.auctions = [
            auction for auction in self.auctions
            if auction["id"] != auction_id
        ]

        self.refresh_table()
        self.save_auctions()

    # --------------------------------------------------
    # SAVE AUCTIONS
    # --------------------------------------------------

    def save_auctions(self):

        try:

            with open(
                self.data_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.auctions,
                    file,
                    indent=4
                )

        except Exception as error:

            messagebox.showerror(
                "Save Error",
                str(error)
            )

    # --------------------------------------------------
    # LOAD AUCTIONS
    # --------------------------------------------------

    def load_auctions(self):

        if not os.path.exists(
            self.data_file
        ):
            return

        try:

            with open(
                self.data_file,
                "r",
                encoding="utf-8"
            ) as file:

                self.auctions = json.load(
                    file
                )

            self.refresh_table()

        except Exception as error:

            messagebox.showerror(
                "Load Error",
                str(error)
            )


# ------------------------------------------------------
# START PROGRAM
# ------------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = EbaySniper(root)

    root.mainloop()
