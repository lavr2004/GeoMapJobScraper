from bin.parsers.pracujpl_all.pracujpl_all import PracujPLAllWarszawaParser

def main():
    launch_parser_pracujpl_all_warszawa()

def launch_parser_pracujpl_all_warszawa():
    parser = PracujPLAllWarszawaParser()

    parser.parse(1)

    parser.update_coordinates()

    parser.commit_changes()

    print(f"OK: parsing {parser.PLATFORMNAME_STR} finished")
    print("=" * 100)

if __name__ == "__main__":
    main()