import argparse


def main():
    parser = argparse.ArgumentParser(prog="Scrapper médicos",
                                     description="Crawling e extração de 3 sites")

    parser.add_argument('-d', "--driver",
                        help="Driver do Web Browser.",
                        choices=["chrome", "firefox", "undetected_chrome"],
                        type=str)

    parser.add_argument('-s', "--scraper",
                        help="Scraper a ser executado",
                        choices=["CFM_scraper", "Doctoralia_scraper", "EMEC_scraper"],
                        type=str)

    args = parser.parse_args()
    print(f"Using driver: {args.driver}")

    # TODO Add option to make scrapping from each one of the 3 websites, and to
    # make the output on the CLI or to a .csv, or to a .json file.


if __name__ == '__main__':
    main()
