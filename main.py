from __future__ import annotations

import os
from typing import Optional

import requests
import yarl
from colorama import Fore, init
from tabulate import tabulate
from dotenv import load_dotenv

init(autoreset=True)
load_dotenv()

if os.name == "nt":
    from colorama import just_fix_windows_console

    just_fix_windows_console()


class GoogleSearchAPI:
    API_URL = yarl.URL("https://www.googleapis.com/customsearch/v1")
    API_KEY = os.environ["GOOGLE_API"]
    CX = os.environ["GOOGLE_CX"]
    BASE_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    @staticmethod
    def search(
        query: str,
        nsfw_filter_enabled: bool = False,
        num_results: int = 10,
        page: int = 1,
        exact_terms: Optional[str] = None,
        exclude_terms: Optional[str] = None,
        file_type: Optional[str] = None,
        or_terms: Optional[str] = None,
        site_search: Optional[str] = None,
    ) -> dict:
        if not GoogleSearchAPI.API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set")

        if not GoogleSearchAPI.CX:
            raise ValueError("GOOGLE_CX is not set")

        params = {
            "key": GoogleSearchAPI.API_KEY,
            "cx": GoogleSearchAPI.CX,
            "q": query,
            "num": num_results,
            "start": page,
        }

        if nsfw_filter_enabled:
            params["safe"] = "off"

        if exact_terms:
            params["exactTerms"] = exact_terms

        if exclude_terms:
            params["excludeTerms"] = exclude_terms

        if file_type:
            params["fileType"] = file_type

        if or_terms:
            params["orTerms"] = or_terms

        if site_search:
            params["siteSearch"] = site_search

        response = requests.get(
            GoogleSearchAPI.API_URL, headers=GoogleSearchAPI.BASE_HEADERS, params=params
        )
        response.raise_for_status()

        return response.json()


class ConsolePrinter:
    @staticmethod
    def print_logo() -> str:
        with open("logo.txt") as f:
            logo = f.read()

        logo = logo.replace("{0}", "\t\t\t" + Fore.BLUE)
        logo = logo.replace("{1}", Fore.RED)
        logo = logo.replace("{2}", Fore.YELLOW)
        logo = logo.replace("{3}", Fore.BLUE)
        logo = logo.replace("{4}", Fore.GREEN)
        logo = logo.replace("{5}", Fore.RED)
        return logo

    @staticmethod
    def print_search_results(results: dict):
        r = []
        for _, item in enumerate(results.get("items", []), start=1):
            temp = [
                [f"{Fore.YELLOW}{item['title']}{Fore.WHITE}"],
                [f"{Fore.CYAN}{item['link']}{Fore.WHITE}"],
                [f"{Fore.WHITE}{item['snippet']}{Fore.WHITE}"],
            ]
            temp_table = str(
                tabulate(
                    temp,
                    tablefmt="simple",
                    showindex=False,
                    numalign="center",
                    maxcolwidths=95,
                )
            )
            r.append([temp_table])

        table = tabulate(
            r, tablefmt="fancy_grid", showindex=range(1, len(r) + 1), numalign="center"
        )
        print(table)


class SearchApp:
    def __init__(self):
        self.logo = ConsolePrinter.print_logo()

    def run(self):
        print(self.logo)

        query = input(
            f"\t\t\t{Fore.WHITE}[*] {Fore.GREEN}Enter search query: {Fore.WHITE}"
        )
        num_results = input(
            f"\t\t\t{Fore.WHITE}[*] {Fore.GREEN}Enter number of results: {Fore.WHITE}"
        )

        if not num_results.isdigit():
            print(
                f"\t\t\t{Fore.WHITE}[*] {Fore.RED}Invalid number of results. Defaulting to 5...{Fore.WHITE}"
            )
            num_results = 5
        else:
            num_results = int(num_results)

        print(
            f"\t\t\t{Fore.WHITE}[*] {Fore.GREEN}Searching for {Fore.YELLOW}{num_results}{Fore.GREEN} results for {Fore.YELLOW}`{query}`{Fore.GREEN}...{Fore.WHITE}"
        )
        print()

        results = GoogleSearchAPI.search(query, num_results=num_results)
        ConsolePrinter.print_search_results(results)


if __name__ == "__main__":
    app = SearchApp()
    app.run()
